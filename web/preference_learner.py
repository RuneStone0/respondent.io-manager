#!/usr/bin/env python3
"""
Module for learning user preferences from behavior
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from bson import ObjectId
from pymongo.collection import Collection
import uuid
import hashlib
import json
try:
    from .hidden_projects_tracker import log_hidden_project, is_project_hidden
    from .ai_analyzer import analyze_hide_feedback, extract_similarity_patterns, find_similar_projects, should_hide_project_based_on_feedback
except ImportError:
    from hidden_projects_tracker import log_hidden_project, is_project_hidden
    from ai_analyzer import analyze_hide_feedback, extract_similarity_patterns, find_similar_projects, should_hide_project_based_on_feedback


def record_project_hidden(
    hidden_projects_log_collection: Collection,
    user_preferences_collection: Collection,
    user_id: str,
    project_id: str,
    feedback_text: Optional[str] = None,
    hidden_method: str = "manual"
) -> bool:
    """
    Track when user hides a project with optional feedback
    
    Args:
        hidden_projects_log_collection: Collection for hidden_projects_log
        user_preferences_collection: Collection for user_preferences
        user_id: User ID
        project_id: Project ID
        feedback_text: Optional feedback text
        hidden_method: Method used to hide
        
    Returns:
        True if successful
    """
    try:
        # Log to hidden_projects_log
        log_hidden_project(
            hidden_projects_log_collection,
            user_id,
            project_id,
            hidden_method,
            feedback_text=feedback_text
        )
        
        # Update user_preferences
        user_preferences_collection.update_one(
            {'user_id': user_id},
            {
                '$addToSet': {'hidden_projects': project_id},
                '$set': {'updated_at': datetime.utcnow()}
            },
            upsert=True
        )
        
        return True
    except Exception as e:
        print(f"Error recording project hidden: {e}")
        return False


def record_category_hidden(
    hidden_projects_log_collection: Collection,
    user_preferences_collection: Collection,
    user_id: str,
    category_name: str,
    category_pattern: Dict[str, Any],
    project_ids: List[str]
) -> bool:
    """
    Track when user hides an entire category
    
    Args:
        hidden_projects_log_collection: Collection for hidden_projects_log
        user_preferences_collection: Collection for user_preferences
        user_id: User ID
        category_name: Category name
        category_pattern: Category pattern
        project_ids: List of project IDs in category
        
    Returns:
        True if successful
    """
    try:
        # Log each project
        for project_id in project_ids:
            log_hidden_project(
                hidden_projects_log_collection,
                user_id,
                project_id,
                'category',
                category_name=category_name
            )
        
        # Update user_preferences
        user_preferences_collection.update_one(
            {'user_id': user_id},
            {
                '$addToSet': {
                    'hidden_projects': {'$each': project_ids},
                    'hidden_categories': {
                        'name': category_name,
                        'pattern': category_pattern,
                        'hidden_at': datetime.utcnow()
                    }
                },
                '$set': {'updated_at': datetime.utcnow()}
            },
            upsert=True
        )
        
        return True
    except Exception as e:
        print(f"Error recording category hidden: {e}")
        return False


def record_project_kept(
    user_preferences_collection: Collection,
    user_id: str,
    project_id: str
) -> bool:
    """
    Track when user keeps a project
    
    Args:
        user_preferences_collection: Collection for user_preferences
        user_id: User ID
        project_id: Project ID
        
    Returns:
        True if successful
    """
    try:
        user_preferences_collection.update_one(
            {'user_id': user_id},
            {
                '$addToSet': {'kept_projects': project_id},
                '$set': {'updated_at': datetime.utcnow()}
            },
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error recording project kept: {e}")
        return False


def analyze_feedback_and_learn(
    user_preferences_collection: Collection,
    user_id: str,
    project_id: str,
    feedback_text: str,
    project_data: Dict[str, Any],
    ai_analysis_cache_collection: Optional[Collection] = None
) -> Dict[str, Any]:
    """
    Store raw feedback text in user preferences for AI-based hiding decisions
    
    Args:
        user_preferences_collection: Collection for user_preferences
        user_id: User ID
        project_id: Project ID
        feedback_text: User feedback
        project_data: Project data
        ai_analysis_cache_collection: Optional MongoDB collection for AI analysis cache
        
    Returns:
        Dictionary with feedback information
    """
    try:
        # Store raw feedback text in user preferences
        feedback_entry = {
            'id': str(uuid.uuid4()),  # Generate unique ID
            'feedback_text': feedback_text,
            'project_id': project_id,
            'hidden_at': datetime.utcnow()
        }
        user_preferences_collection.update_one(
            {'user_id': user_id},
            {
                '$push': {
                    'hide_feedback': feedback_entry
                },
                '$set': {'updated_at': datetime.utcnow()}
            },
            upsert=True
        )
        
        # Invalidate AI analysis cache for this user since feedback changed
        if ai_analysis_cache_collection is not None:
            ai_analysis_cache_collection.delete_many({'user_id': user_id})
        
        return {'feedback_text': feedback_text, 'project_id': project_id}
    except Exception as e:
        print(f"Error storing feedback: {e}")
        return {'feedback_text': feedback_text, 'project_id': project_id}


def update_user_preferences(
    user_preferences_collection: Collection,
    user_id: str
) -> Dict[str, Any]:
    """
    Analyze hidden/kept projects to learn preferences
    
    Args:
        user_preferences_collection: Collection for user_preferences
        user_id: User ID
        
    Returns:
        Updated preferences dictionary
    """
    try:
        prefs = user_preferences_collection.find_one({'user_id': user_id})
        if not prefs:
            return {}
        
        # This is a placeholder - in a full implementation, we'd analyze
        # hidden vs kept projects to learn preferences
        # For now, just return current preferences
        
        return {
            'hidden_projects': prefs.get('hidden_projects', []),
            'kept_projects': prefs.get('kept_projects', []),
            'hidden_categories': prefs.get('hidden_categories', []),
            'learned_patterns': prefs.get('learned_patterns', [])
        }
    except Exception as e:
        print(f"Error updating user preferences: {e}")
        return {}


def get_user_preferences(
    user_preferences_collection: Collection,
    user_id: str
) -> Dict[str, Any]:
    """
    Get learned preferences
    
    Args:
        user_preferences_collection: Collection for user_preferences
        user_id: User ID
        
    Returns:
        Preferences dictionary
    """
    try:
        prefs = user_preferences_collection.find_one({'user_id': user_id})
        if not prefs:
            return {
                'hidden_projects': [],
                'kept_projects': [],
                'hidden_categories': [],
                'learned_patterns': [],
                'question_answers': [],
                'learned_exclusions': [],
                'hide_feedback': []
            }
        
        return {
            'hidden_projects': prefs.get('hidden_projects', []),
            'kept_projects': prefs.get('kept_projects', []),
            'hidden_categories': prefs.get('hidden_categories', []),
            'learned_patterns': prefs.get('learned_patterns', []),
            'question_answers': prefs.get('question_answers', []),
            'learned_exclusions': prefs.get('learned_exclusions', []),
            'hide_feedback': prefs.get('hide_feedback', [])
        }
    except Exception as e:
        print(f"Error getting user preferences: {e}")
        return {
            'hidden_projects': [],
            'kept_projects': [],
            'hidden_categories': [],
            'learned_patterns': [],
            'question_answers': [],
            'learned_exclusions': [],
            'hide_feedback': []
        }


def should_hide_project(
    user_preferences_collection: Collection,
    user_id: str,
    project: Dict[str, Any]
) -> bool:
    """
    Use learned preferences to suggest hiding
    
    Args:
        user_preferences_collection: Collection for user_preferences
        user_id: User ID
        project: Project data
        
    Returns:
        True if project should be hidden based on preferences
    """
    try:
        prefs = get_user_preferences(user_preferences_collection, user_id)
        
        # Check if project matches any hidden category patterns
        for category in prefs.get('hidden_categories', []):
            pattern = category.get('pattern', {})
            # Simple matching - could be enhanced
            project_text = f"{project.get('name', '')} {project.get('description', '')}".lower()
            keywords = pattern.get('keywords', [])
            if any(keyword.lower() in project_text for keyword in keywords):
                return True
        
        # Check learned patterns
        for learned in prefs.get('learned_patterns', []):
            patterns = learned.get('patterns', {})
            project_text = f"{project.get('name', '')} {project.get('description', '')}".lower()
            keywords = patterns.get('keywords', [])
            if any(keyword.lower() in project_text for keyword in keywords):
                return True
        
        return False
    except Exception as e:
        print(f"Error checking if should hide project: {e}")
        return False


def _compute_feedback_hash(feedback_list: List[Dict[str, Any]]) -> str:
    """
    Compute a hash of the feedback list to detect changes
    
    Args:
        feedback_list: List of feedback entries
        
    Returns:
        SHA256 hash string of the feedback list
    """
    # Create a stable representation of feedback for hashing
    # Only include feedback_text and id (to detect additions/deletions/edits)
    feedback_data = []
    for feedback in feedback_list:
        feedback_data.append({
            'id': feedback.get('id', ''),
            'feedback_text': feedback.get('feedback_text', '')
        })
    
    # Sort by id to ensure consistent hashing
    feedback_data.sort(key=lambda x: x.get('id', ''))
    
    # Create hash
    feedback_json = json.dumps(feedback_data, sort_keys=True)
    return hashlib.sha256(feedback_json.encode('utf-8')).hexdigest()


def should_hide_based_on_ai_preferences(
    user_preferences_collection: Collection,
    user_id: str,
    project: Dict[str, Any],
    ai_analysis_cache_collection: Optional[Collection] = None
) -> bool:
    """
    Check if project should be hidden based on user's raw feedback using AI
    
    This function uses AI to analyze the project against all stored raw feedback
    to determine if it should be hidden based on the user's previous reasons.
    Uses caching to avoid expensive AI calls when hide_feedback hasn't changed.
    
    Args:
        user_preferences_collection: Collection for user_preferences
        user_id: User ID
        project: Project data
        ai_analysis_cache_collection: Optional MongoDB collection for AI analysis cache
        
    Returns:
        True if project should be hidden based on AI analysis of user feedback
    """
    try:
        project_id = project.get('id')
        if not project_id:
            return False
        
        prefs = get_user_preferences(user_preferences_collection, user_id)
        
        # Get all stored raw feedback
        hide_feedback = prefs.get('hide_feedback', [])
        if not hide_feedback:
            return False
        
        # Compute hash of current feedback to check if cache is still valid
        feedback_hash = _compute_feedback_hash(hide_feedback)
        
        # Check cache if available
        if ai_analysis_cache_collection is not None:
            cache_entry = ai_analysis_cache_collection.find_one({
                'user_id': user_id,
                'project_id': str(project_id)
            })
            
            if cache_entry:
                cached_hash = cache_entry.get('hide_feedback_hash')
                # If feedback hasn't changed, return cached result
                if cached_hash == feedback_hash:
                    return cache_entry.get('should_hide', False)
        
        # Cache miss or feedback changed - run AI analysis
        should_hide = should_hide_project_based_on_feedback(project, hide_feedback)
        
        # Store result in cache if available
        if ai_analysis_cache_collection is not None:
            ai_analysis_cache_collection.update_one(
                {
                    'user_id': user_id,
                    'project_id': str(project_id)
                },
                {
                    '$set': {
                        'user_id': user_id,
                        'project_id': str(project_id),
                        'hide_feedback_hash': feedback_hash,
                        'should_hide': should_hide,
                        'cached_at': datetime.utcnow()
                    }
                },
                upsert=True
            )
        
        return should_hide
    except Exception as e:
        print(f"Error checking AI preferences: {e}")
        return False


def store_question_answer(
    user_preferences_collection: Collection,
    user_id: str,
    question_id: str,
    question_text: str,
    answer: bool,
    pattern: Dict[str, Any],
    project_id: Optional[str] = None
) -> bool:
    """
    Store a user's answer to an AI-generated question
    
    Args:
        user_preferences_collection: Collection for user_preferences
        user_id: User ID
        question_id: Unique question ID
        question_text: The question text
        answer: User's answer (True/False)
        pattern: Pattern associated with the question
        project_id: Optional project ID that triggered the question
        
    Returns:
        True if successful
    """
    try:
        # Store the question answer
        question_answer = {
            'question_id': question_id,
            'question_text': question_text,
            'answer': answer,
            'pattern': pattern,
            'project_id': project_id,
            'answered_at': datetime.utcnow()
        }
        
        user_preferences_collection.update_one(
            {'user_id': user_id},
            {
                '$addToSet': {'question_answers': question_answer},
                '$set': {'updated_at': datetime.utcnow()}
            },
            upsert=True
        )
        
        # If answer is False (user doesn't match the requirement), add to learned exclusions
        if not answer:
            learned_exclusion = {
                'question_id': question_id,
                'pattern': pattern,
                'learned_at': datetime.utcnow()
            }
            user_preferences_collection.update_one(
                {'user_id': user_id},
                {
                    '$addToSet': {'learned_exclusions': learned_exclusion},
                    '$set': {'updated_at': datetime.utcnow()}
                },
                upsert=True
            )
        
        return True
    except Exception as e:
        print(f"Error storing question answer: {e}")
        return False


def find_and_auto_hide_similar(
    hidden_projects_log_collection: Collection,
    user_preferences_collection: Collection,
    user_id: str,
    hidden_project_id: str,
    all_projects: List[Dict[str, Any]],
    similarity_patterns: Dict[str, Any]
) -> List[str]:
    """
    Find similar projects based on feedback and auto-hide them
    
    Args:
        hidden_projects_log_collection: Collection for hidden_projects_log
        user_preferences_collection: Collection for user_preferences
        user_id: User ID
        hidden_project_id: Hidden project ID
        all_projects: List of all projects
        similarity_patterns: Patterns extracted from feedback
        
    Returns:
        List of project IDs that were auto-hidden
    """
    try:
        similar_projects = find_similar_projects(
            user_id,
            hidden_project_id,
            all_projects,
            similarity_patterns
        )
        
        auto_hidden_ids = []
        for project in similar_projects:
            project_id = project.get('id')
            if project_id and not is_project_hidden(hidden_projects_log_collection, user_id, project_id):
                log_hidden_project(
                    hidden_projects_log_collection,
                    user_id,
                    project_id,
                    'auto_similar'
                )
                auto_hidden_ids.append(project_id)
        
        # Update user preferences
        if auto_hidden_ids:
            user_preferences_collection.update_one(
                {'user_id': user_id},
                {
                    '$addToSet': {'hidden_projects': {'$each': auto_hidden_ids}},
                    '$set': {'updated_at': datetime.utcnow()}
                },
                upsert=True
            )
        
        return auto_hidden_ids
    except Exception as e:
        print(f"Error finding and auto-hiding similar projects: {e}")
        return []


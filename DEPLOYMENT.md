# Cloud Run Deployment Guide

This guide explains how to deploy the RespondentPro application to Google Cloud Platform (GCP) Cloud Run.

## Prerequisites

1. **Google Cloud Account**: You need a GCP account with billing enabled
2. **gcloud CLI**: Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. **Docker**: Docker is included with gcloud CLI, but you can also install it separately

## Initial Setup

1. **Authenticate with Google Cloud**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable required APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   ```

3. **Create Artifact Registry repository** (if it doesn't exist):
   ```bash
   gcloud artifacts repositories create respondentpro-repo \
     --repository-format=docker \
     --location=us-central1 \
     --description="Docker repository for RespondentPro" \
     --public
   ```
   
   **Note**: The repository is created with public access (no IAM required). The `cloudbuild.yaml` will automatically create this repository with public access if it doesn't exist.

## Environment Variables

Cloud Run requires environment variables to be set. You'll need to configure these in the Cloud Run service:

### Required Environment Variables

- `MONGODB_URI`: Your MongoDB connection string (e.g., `mongodb+srv://user:pass@cluster.mongodb.net/`)
- `MONGODB_DB`: Your MongoDB database name (default: `respondent_manager`)
- `SECRET_KEY`: A secret key for Flask sessions (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)

### Optional Environment Variables

- `FLASK_DEBUG`: Set to `true` for debug mode (default: `false` - recommended for production)
- `HOST`: Host to bind to (default: `0.0.0.0` - don't change this)
- `PORT`: Port to listen on (Cloud Run sets this automatically - don't override)

## Deployment Methods

### Method 1: Using Cloud Build (Recommended)

This method uses the `cloudbuild.yaml` file for automated builds with Artifact Registry:

```bash
# Submit the build to Cloud Build
# The cloudbuild.yaml uses Artifact Registry (modern, cheaper than Container Registry)
gcloud builds submit --config cloudbuild.yaml

# The build will automatically deploy to Cloud Run
```

**Note**: The `cloudbuild.yaml` will automatically create the Artifact Registry repository with public access if it doesn't exist. If you need to create it manually:
```bash
gcloud artifacts repositories create respondentpro-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Docker repository for RespondentPro" \
  --public
```

You can customize the region and repository name by passing substitutions:
```bash
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_REGION=us-east1,_REPOSITORY=my-repo
```

After deployment, set environment variables:
```bash
gcloud run services update respondentpro \
  --region us-central1 \
  --set-env-vars MONGODB_URI="your-mongodb-uri",MONGODB_DB="respondent_manager",SECRET_KEY="your-secret-key"
```

### Method 2: Manual Docker Build and Deploy

1. **Configure Docker for Artifact Registry**:
   ```bash
   gcloud auth configure-docker us-central1-docker.pkg.dev
   ```

2. **Build the Docker image**:
   ```bash
   docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/respondentpro-repo/respondentpro:latest .
   ```

3. **Push to Artifact Registry**:
   ```bash
   docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/respondentpro-repo/respondentpro:latest
   ```

4. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy respondentpro \
     --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/respondentpro-repo/respondentpro:latest \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated \
     --min-instances 0 \
     --max-instances 1 \
     --cpu 1 \
     --memory 256Mi \
     --set-env-vars MONGODB_URI="your-mongodb-uri",MONGODB_DB="respondent_manager",SECRET_KEY="your-secret-key"
   ```

### Method 3: Direct Deploy from Source

```bash
gcloud run deploy respondentpro \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 1 \
  --cpu 1 \
  --memory 256Mi \
  --set-env-vars MONGODB_URI="your-mongodb-uri",MONGODB_DB="respondent_manager",SECRET_KEY="your-secret-key"
```

## Setting Environment Variables

You can set or update environment variables after deployment:

```bash
gcloud run services update respondentpro \
  --region us-central1 \
  --update-env-vars MONGODB_URI="new-uri",SECRET_KEY="new-key"
```

Or use the Cloud Console:
1. Go to Cloud Run in the GCP Console
2. Click on your service
3. Click "Edit & Deploy New Revision"
4. Go to "Variables & Secrets" tab
5. Add or update environment variables

## MongoDB Atlas Configuration

If using MongoDB Atlas, ensure:

1. **Network Access**: Whitelist Cloud Run's IP ranges or use `0.0.0.0/0` (less secure but works for Cloud Run)
2. **Database User**: Has `readWrite` permissions on your database
3. **Connection String**: Use the format `mongodb+srv://username:password@cluster.mongodb.net/`

## Updating the Service

After making code changes:

1. **Using Cloud Build**:
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

2. **Manual update**:
   ```bash
   # Rebuild and push to Artifact Registry
   docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/respondentpro-repo/respondentpro:latest .
   docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/respondentpro-repo/respondentpro:latest
   
   # Deploy new revision
   gcloud run deploy respondentpro \
     --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/respondentpro-repo/respondentpro:latest \
     --region us-central1
   ```

## Viewing Logs

```bash
gcloud run services logs read respondentpro --region us-central1
```

Or view in the Cloud Console under Cloud Run → Logs.

## Scaling Configuration

The service is configured for minimal cost:
- **Min instances**: 0 (scales to zero when not in use)
- **Max instances**: 1 (limits concurrent instances)
- **CPU**: 1 (minimum allocation)
- **Memory**: 256Mi (minimum allocation)

To update these settings:

```bash
gcloud run services update respondentpro \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 1 \
  --cpu 1 \
  --memory 256Mi
```

## Security Considerations

1. **Authentication**: The default deployment allows unauthenticated access. To require authentication:
   ```bash
   gcloud run services update respondentpro \
     --region us-central1 \
     --no-allow-unauthenticated
   ```

2. **Secrets Management**: For sensitive values, use [Secret Manager](https://cloud.google.com/secret-manager):
   ```bash
   # Create a secret
   echo -n "your-secret-value" | gcloud secrets create secret-key --data-file=-
   
   # Grant Cloud Run access
   gcloud secrets add-iam-policy-binding secret-key \
     --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   
   # Use in Cloud Run
   gcloud run services update respondentpro \
     --region us-central1 \
     --update-secrets SECRET_KEY=secret-key:latest
   ```

## Troubleshooting

1. **Check service status**:
   ```bash
   gcloud run services describe respondentpro --region us-central1
   ```

2. **View recent logs**:
   ```bash
   gcloud run services logs read respondentpro --region us-central1 --limit 50
   ```

3. **Test locally with Docker**:
   ```bash
   docker build -t respondentpro .
   docker run -p 8080:8080 \
     -e MONGODB_URI="your-uri" \
     -e MONGODB_DB="respondent_manager" \
     -e SECRET_KEY="your-key" \
     respondentpro
   ```

4. **Common issues**:
   - **Port binding errors**: Cloud Run sets PORT automatically, don't override it
   - **MongoDB connection failures**: Check network access and connection string
   - **Memory issues**: Increase memory allocation in Cloud Run settings

## Cost Optimizations

This deployment is configured with several cost optimizations:

### 1. **Multi-Stage Docker Build**
- Uses a two-stage build process to minimize final image size
- Build dependencies are discarded, keeping only runtime requirements
- Smaller images = faster deployments and lower storage costs

### 2. **Artifact Registry (instead of Container Registry)**
- Artifact Registry is the modern, recommended service
- Better pricing and performance than legacy Container Registry
- More granular access controls

### 3. **Optimized Cloud Build Machine**
- Uses `E2_HIGHCPU_2` instead of `E2_HIGHCPU_8` (75% cheaper for builds)
- Builds may take slightly longer but cost significantly less

### 4. **Minimal Cloud Run Configuration**
- Scale to zero (min instances: 0) - no cost when idle
- Maximum 1 instance - prevents unexpected scaling costs
- Minimum resources (1 CPU, 256Mi memory) - cheapest tier

## Cost Estimation

With the minimal cost configuration (scale to zero, max 1 instance, 1 CPU, 256Mi memory):

Cloud Run pricing is based on:
- **CPU**: Only charged when handling requests (scales to zero when idle)
- **Memory**: Only charged when handling requests (scales to zero when idle)
- **Requests**: Per million requests (first 2 million free per month)
- **Minimum instances**: 0 (no cost when idle)

**Expected costs**:
- **Idle time**: $0 (scales to zero)
- **Active usage**: ~$0.00002400 per vCPU-second, ~$0.00000250 per GiB-second
- **Requests**: First 2 million free, then $0.40 per million
- **Build costs**: Significantly reduced with E2_HIGHCPU_2 machine type

For low to moderate traffic (e.g., < 100k requests/month), expect costs of **$0-2/month** or even free if within the free tier limits.

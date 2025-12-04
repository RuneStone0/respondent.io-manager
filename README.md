# Respondent.io Management CLI

A lightweight, no-nonsense command-line tool for power users of Respondent.io.
Respondent.io is a research platform that connects companies with participants for paid studies, interviews, and surveys. Incentives can range from pocket change to serious money, but the catch? A ton of low-paying or super-long “$200 over 7 days” traps that waste your time.
This CLI fixes that.

With it you can:
* List all your active projects in one glance
* Instantly calculate real hourly rates (because $200 sounds nice until you realize it’s $200 for 10 hours of diary entries)
* Hide junk projects automatically — e.g. anything under $70 flat or below your desired hourly rate

Why bother? Because life’s too short to manually click “Not interested” on fifty $10 surveys. Save your brainpower for the gigs that actually pay the rent.

Quick Example
```
Bashrespondent hide --min-hourly 80    # bye-bye low-rate nonsense
respondent hide --min-incentive 70     # ignore anything under $70
respondent list --show-hourly          # see real rates at a glance
```

Light, fast, and mildly judgmental about bad incentives. Enjoy the extra free time (and money).

## Features

- **Authentication**: Verify your authentication status with Respondent.io
- **List Projects**: Browse available projects with calculated hourly rates
- **Hide Projects**: Hide individual projects or filter and hide multiple projects by:
  - Project ID
  - Hourly rate threshold
  - Total incentive threshold

## Installation

1. Clone or download this repository

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Getting Your Credentials

1. Log into respondent.io in your browser
2. Open Developer Tools (F12) → Network tab
3. Refresh the page or click around until you see requests to app.respondent.io
4. Click any request (e.g. one to `/api/v1/projects` or `/api/v1/me`)
5. In the Request Headers section, copy these two values:
    - cookie: find respondent.session.sid=, copy the whole thing (just the value after = is enough if you prefer)
    - authorization: copy the Bearer token (it looks like `Bearer eyJhbGciOi...`)
6. Paste values into `config.json`

## Usage
```bash
# Test your authentication status
python main.py auth

# List projects
python main.py projects

# Hide a single project by ID:
python main.py hide --id 692f1ffb607b02364a3c37d6

# Hide all projects with an hourly rate lower than the specified amount
python main.py hide --hourly-rate 50

# Hide all projects with a total incentive lower than the specified amount:
python main.py hide --incentive 50
```

## Security Notes

- Never commit your `config.json` file to version control
- Keep your session cookies and authorization tokens secure
- Tokens expire periodically - you may need to refresh them

## License

This project is provided as-is for personal use.

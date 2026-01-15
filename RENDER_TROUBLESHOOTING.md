# Fix Render Production Issues

## Problem: 500 Internal Server Error on /presentations/generate/

### Root Causes (Most Likely):
1. Database migrations not applied to production
2. API token not generated in production database
3. Environment variables not properly set

### Quick Fixes:

#### Option 1: Use Render Shell (Recommended)
1. Go to your Render backend service dashboard
2. Click "Shell" tab
3. Run these commands in order:

```bash
# Run migrations
python manage.py migrate

# Create the API token
python generate_token.py

# Check database connection
python manage.py shell -c "from django.contrib.auth.models import User; print(f'Users: {User.objects.count()}')"
```

#### Option 2: Manual Deploy with Post-Deploy Script
Update your `render.yaml` to include a post-deploy hook:

```yaml
services:
  - type: web
    name: presentation-backend
    runtime: python
    buildCommand: "pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate"
    startCommand: "gunicorn presentation_project.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 2"
    # ... rest of config
```

This ensures migrations run automatically during deployment.

#### Option 3: Check Render Logs
1. In Render dashboard, click your backend service
2. Go to "Logs" tab
3. Look for error messages that show the actual issue
4. Common errors:
   - `Token matching query does not exist` → Run generate_token.py
   - `relation "auth_user" does not exist` → Run migrations
   - `Environment variable not found` → Check Settings tab

### Verification Steps:
After applying the fixes, test with:
```bash
curl -H "Authorization: Token 57cade5694b471be8aa9b035d5ceb90d4d452e93" https://presentation-slides.onrender.com/api/presentations/
```

Should return: `{"count": 0, "next": null, "previous": null, "results": []}`

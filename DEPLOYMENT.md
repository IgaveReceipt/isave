# Deployment Guide

## Prerequisites

- Python 3.13+
- Node.js 20+
- PostgreSQL (for production)
- Git

## Environment Variables

### Backend (.env)
```bash
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:password@host:port/dbname
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

## Deployment Options

### Option 1: Heroku

#### Backend
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create igave-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Deploy
git push heroku main

# Run migrations
heroku run python backend/manage.py migrate
heroku run python backend/manage.py createsuperuser
```

#### Frontend (Vercel)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend/igave_receipts
vercel --prod
```

### Option 2: Railway

1. Connect GitHub repository
2. Select `backend` as root directory
3. Add PostgreSQL service
4. Set environment variables
5. Deploy automatically on push

### Option 3: DigitalOcean App Platform

1. Create new app from GitHub
2. Configure build settings:
   - Backend: Django app
   - Frontend: Next.js app
3. Add managed PostgreSQL database
4. Set environment variables
5. Deploy

## Local Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd frontend/igave_receipts
npm install
npm run dev
```

## Testing Before Deployment

```bash
# Backend tests
cd backend
pytest -v
flake8
python manage.py test

# Frontend build
cd frontend/igave_receipts
npm run build
npm audit
```

## Post-Deployment Checklist

- [ ] Database migrations applied
- [ ] Static files collected (if applicable)
- [ ] Environment variables set correctly
- [ ] CORS configured properly
- [ ] SSL/HTTPS enabled
- [ ] Superuser created
- [ ] Security headers configured
- [ ] Monitoring/logging set up
- [ ] Backup strategy implemented
- [ ] Domain DNS configured

# Igave

Igave is a modern receipt scanning and management system designed to help customers organize their expenses efficiently. The application features a robust Django backend and a dynamic Next.js frontend.

## 🚀 Tech Stack

- **Backend:** Django 5 (Python), Django REST Framework
- **Frontend:** Next.js 15 (React, TypeScript), Tailwind CSS
- **Database:** SQLite (Development) / PostgreSQL (Production ready)
- **Styling:** Tailwind CSS

## 📂 Project Structure

The project is organized into two main directories:

```
Igave/
├── backend/            # Django API and business logic
│   ├── igave/          # Project configuration (settings, urls)
│   ├── igaveapp/       # Main application (models, views, migrations)
│   └── manage.py       # Django management script
├── frontend/           # Next.js User Interface
│   └── igave_receipts/ # Next.js application source
└── requirements.txt    # Python dependencies
```

## 🛠️ Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### 1. Backend Setup

Navigate to the backend directory and set up the Python environment.

```bash
cd backend
# Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```
The backend API will be available at `http://localhost:8000`.

### 2. Frontend Setup

Navigate to the frontend directory and install dependencies.

```bash
cd frontend/igave_receipts

# Install Node modules
npm install

# Start the development server
npm run dev
```
The frontend application will be available at `http://localhost:3000`.

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate

# Run all tests with pytest
pytest -v

# Run Django tests
python manage.py test

# Check code quality
flake8
```

### Frontend Tests
```bash
cd frontend/igave_receipts

# Build for production
npm run build

# Security audit
npm audit
```

### Pre-Deployment Check
Run the comprehensive pre-deployment script:
```bash
./scripts/pre-deploy-check.sh
```

## 📡 API Endpoints

The backend provides the following REST API endpoints:

### Authentication
- `POST /api/token/` - Obtain JWT token pair
- `POST /api/token/refresh/` - Refresh access token

### Users
- `GET /api/users/` - List users (authenticated)
- `GET /api/users/me/` - Get current user info

### Receipts
- `GET /api/receipts/` - List user's receipts
- `POST /api/receipts/` - Create new receipt
- `GET /api/receipts/{id}/` - Get receipt details
- `PUT /api/receipts/{id}/` - Update receipt
- `DELETE /api/receipts/{id}/` - Delete receipt

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for:
- Heroku
- Railway
- DigitalOcean
- Vercel (Frontend)

## 📊 Project Status

- ✅ Backend API with Django REST Framework
- ✅ JWT Authentication
- ✅ Receipt CRUD operations
- ✅ User isolation and permissions
- ✅ Comprehensive test suite (9 tests passing)
- ✅ Code linting with flake8
- ✅ CI/CD with GitHub Actions
- ✅ Production-ready settings
- ✅ Security configurations
- 🔄 Frontend UI (in development)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`./scripts/pre-deploy-check.sh`)
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request
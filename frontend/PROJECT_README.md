# Ripple - Fundraising Platform

A full-stack fundraising platform similar to GoFundMe, built with FastAPI and React. Ripple enables individuals and organisations to create campaigns, accept donations, and track their fundraising progress across three campaign types: goal-based fundraising, time-bound events, and ad-hoc giving opportunities.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Licence](#licence)

## ✨ Features

### Current Features (MVP)

- **User Authentication**
  - User registration and login with JWT tokens
  - Secure password hashing with bcrypt
  - Token-based API authentication
  - Protected routes and endpoints

- **Giver Profile Management**
  - Automatic profile creation on registration
  - Complete profile editing (personal and address details)
  - Donation history tracking
  - Total contribution analytics

- **Campaign Management**
  - Three campaign types: goal-based, time-bound, and ad-hoc
  - Campaign CRUD operations
  - Automatic status workflows (draft, active, completed, cancelled)
  - Real-time aggregate tracking (current amount, donor count)

- **Donation System**
  - Donation creation with optional messages
  - Anonymous donation support
  - Automatic aggregate updates on completion
  - Donation status tracking (pending, completed, cancelled, failed)

- **Mobile-First Frontend**
  - Responsive design optimised for mobile devices
  - Clean, accessible UI with custom colour palette
  - Form validation and error handling
  - Loading states and user feedback

### Coming Soon

- 🔄 Stripe payment integration
- 📧 Email notifications
- 🔍 Campaign search and filtering
- 📊 Enhanced analytics and reporting
- 📱 Campaign updates and comments
- 🔗 Social sharing
- 📈 Campaign progress visualisations

## 🛠 Technology Stack

### Backend

- **Framework**: FastAPI 0.104+
- **Database**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0+
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Containerisation**: Docker & Docker Compose
- **API Documentation**: OpenAPI/Swagger (built-in)

### Frontend

- **Framework**: React 18
- **Build Tool**: Vite 5
- **Routing**: React Router 6
- **HTTP Client**: Axios
- **Testing**: Vitest + React Testing Library
- **Styling**: Custom CSS (mobile-first)

### Development Tools

- **Version Control**: Git with Conventional Commits
- **Code Quality**: ESLint
- **Testing**: Vitest, pytest (planned)
- **API Testing**: Custom shell scripts

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React Application (Port 3000)                       │  │
│  │  - Authentication UI                                 │  │
│  │  - Profile Management                                │  │
│  │  - Campaign Browsing (coming soon)                   │  │
│  │  - Donation Flow (coming soon)                       │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       │ (Axios)
┌──────────────────────▼──────────────────────────────────────┐
│                      Backend API                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI Application (Port 8000)                     │  │
│  │  - JWT Authentication                                │  │
│  │  - RESTful API Endpoints                             │  │
│  │  - Business Logic                                    │  │
│  │  - Data Validation                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ SQLAlchemy ORM
┌──────────────────────▼──────────────────────────────────────┐
│                    Database Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MySQL Database (Port 3306)                          │  │
│  │  - Users & Authentication                            │  │
│  │  - Giver Profiles                                    │  │
│  │  - Campaigns                                         │  │
│  │  - Donations                                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- **Docker Desktop** (recommended) or:
  - Python 3.11+
  - MySQL 8.0+
  - Node.js 18+
  - npm or yarn

### Quick Start (Docker - Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/david-crosby/ripple-fundraiser.git
   cd ripple-fundraiser
   ```

2. **Start the backend services**
   ```bash
   cd backend
   docker-compose up -d
   ```
   
   This will start:
   - MySQL database on port 3306
   - FastAPI application on port 8000

3. **Install and start the frontend**
   ```bash
   cd ../frontend
   npm install
   cp .env.example .env
   npm run dev
   ```
   
   The frontend will be available at http://localhost:3000

4. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup (Without Docker)

#### Backend Setup

1. **Create and activate virtual environment**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install --break-system-packages -r requirements.txt
   ```

3. **Configure database**
   ```bash
   # Create MySQL database
   mysql -u root -p
   CREATE DATABASE ripple;
   CREATE USER 'ripple_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON ripple.* TO 'ripple_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

4. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Update VITE_API_BASE_URL if needed
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

## 📁 Project Structure

```
ripple-fundraiser/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   ├── auth.py       # Authentication routes
│   │   │   ├── campaigns.py  # Campaign routes
│   │   │   ├── donations.py  # Donation routes
│   │   │   └── givers.py     # Giver profile routes
│   │   ├── core/             # Core functionality
│   │   │   ├── config.py     # Configuration settings
│   │   │   └── security.py   # Security utilities (JWT, hashing)
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── giver.py
│   │   │   ├── campaign.py
│   │   │   └── donation.py
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── database.py       # Database connection
│   │   └── main.py          # Application entry point
│   ├── tests/               # Backend tests (planned)
│   ├── scripts/             # Utility scripts
│   ├── docker-compose.yml   # Docker configuration
│   ├── Dockerfile          # Container image
│   └── requirements.txt    # Python dependencies
│
├── frontend/                  # React frontend application
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   │   └── Header.jsx
│   │   ├── contexts/        # React contexts
│   │   │   └── AuthContext.jsx
│   │   ├── pages/          # Page components
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Profile.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── services/       # API service layer
│   │   │   └── api.js
│   │   ├── test/          # Test utilities
│   │   ├── App.jsx        # Main app component
│   │   ├── main.jsx      # Entry point
│   │   └── index.css     # Global styles
│   ├── package.json      # Dependencies
│   └── vite.config.js   # Build configuration
│
└── README.md             # This file
```

## 💻 Development

### Backend Development

**Run development server with auto-reload:**
```bash
cd backend
docker-compose up
```

**View logs:**
```bash
docker-compose logs -f api
```

**Access database:**
```bash
docker-compose exec db mysql -u ripple_user -p ripple
```

**Run database migrations (when implemented):**
```bash
alembic upgrade head
```

### Frontend Development

**Start development server:**
```bash
cd frontend
npm run dev
```

**Build for production:**
```bash
npm run build
```

**Preview production build:**
```bash
npm run preview
```

**Lint code:**
```bash
npm run lint
```

### Code Style

- **Backend**: Follow PEP 8 Python style guide
- **Frontend**: ESLint configuration included
- **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/) format

Example commit messages:
```
feat(auth): add password reset functionality
fix(donations): correct amount aggregation calculation
docs(readme): update installation instructions
test(campaigns): add unit tests for campaign creation
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest                        # Run all tests (when implemented)
pytest tests/test_auth.py    # Run specific test file
pytest -v --cov=app          # Run with coverage report
```

**Current testing approach:**
- Manual API testing with shell scripts
- Database cleanup utilities included

**Planned improvements:**
- Unit tests with pytest
- Integration tests
- Test fixtures and factories

### Frontend Tests

```bash
cd frontend
npm test                  # Run all tests
npm test -- --watch      # Run in watch mode
npm run test:ui          # Run with UI
npm run test:coverage    # Generate coverage report
```

**Test coverage:**
- ✅ Login component (9 test cases)
- ✅ Register component (12 test cases)
- ✅ AuthContext (11 test cases)
- Total: 32 tests across 3 test suites

## 📚 API Documentation

### Interactive Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
```
POST   /auth/register      # Register new user
POST   /auth/login         # Login and get token
GET    /auth/me           # Get current user
```

#### Giver Profiles
```
GET    /givers/me              # Get own profile
PUT    /givers/me              # Update own profile
GET    /givers/{id}            # Get profile by ID
GET    /givers/me/donations    # Get own donations
```

#### Campaigns
```
GET    /campaigns              # List all campaigns
POST   /campaigns              # Create campaign
GET    /campaigns/{id}         # Get campaign details
PUT    /campaigns/{id}         # Update campaign
DELETE /campaigns/{id}         # Delete campaign
GET    /campaigns/{id}/donations  # Get campaign donations
```

#### Donations
```
POST   /donations                      # Create donation
GET    /donations/{id}                 # Get donation details
POST   /donations/{id}/complete        # Complete donation
POST   /donations/{id}/cancel          # Cancel donation
```

### Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## 🚢 Deployment

### Backend Deployment

**Docker (Production):**
```bash
cd backend
docker-compose -f docker-compose.prod.yml up -d
```

**Environment Variables for Production:**
```env
DATABASE_URL=mysql+pymysql://user:pass@host:3306/ripple
SECRET_KEY=your-production-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
```

**Recommended platforms:**
- AWS ECS/Fargate
- Google Cloud Run
- DigitalOcean App Platform
- Railway
- Fly.io

### Frontend Deployment

**Build for production:**
```bash
cd frontend
npm run build
```

The `dist/` directory contains static files ready for deployment.

**Recommended platforms:**
- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages
- Cloudflare Pages

**Environment variables:**
```env
VITE_API_BASE_URL=https://api.yourdomian.com
```

### Database Backup

```bash
# Backup
docker-compose exec db mysqldump -u ripple_user -p ripple > backup.sql

# Restore
docker-compose exec -T db mysql -u ripple_user -p ripple < backup.sql
```

## 🗺 Roadmap

### Phase 1: MVP ✅ (Completed)
- [x] User authentication system
- [x] Giver profile management
- [x] Campaign CRUD operations
- [x] Donation system architecture
- [x] Mobile-first frontend
- [x] Comprehensive testing suite

### Phase 2: Payment Integration (In Progress)
- [ ] Stripe integration
- [ ] Payment processing
- [ ] Webhook handling
- [ ] Transaction records
- [ ] Receipt generation

### Phase 3: Core Features
- [ ] Campaign browsing and search
- [ ] Campaign creation UI
- [ ] Donation flow UI
- [ ] Email notifications
- [ ] Campaign updates
- [ ] Progress visualisations

### Phase 4: Enhanced Features
- [ ] Social sharing
- [ ] Campaign comments
- [ ] Image uploads
- [ ] Campaign categories
- [ ] Advanced analytics
- [ ] Donor recognition tiers

### Phase 5: Platform Maturity
- [ ] Admin dashboard
- [ ] Reporting and exports
- [ ] API rate limiting
- [ ] Advanced security features
- [ ] Multi-currency support
- [ ] Internationalisation (i18n)

## 🤝 Contributing

Contributions are welcome! This is a learning project, but follows professional development practices.

### Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes using Conventional Commits
4. Write or update tests
5. Ensure all tests pass
6. Push to your branch (`git push origin feat/amazing-feature`)
7. Open a Pull Request

### Coding Standards

- **Python**: PEP 8, type hints where appropriate
- **JavaScript**: ESLint configuration, JSDoc comments
- **Tests**: Write tests for new features
- **Documentation**: Update relevant documentation

## 📝 Licence

This project is part of a personal learning journey to master Python and React through building a complete full-stack application.

## 👤 Author

**David "Bing" Crosby**

- GitHub: [@david-crosby](https://github.com/david-crosby)
- LinkedIn: [David Bing Crosby](https://www.linkedin.com/in/david-bing-crosby/)

## 🙏 Acknowledgements

- FastAPI for the excellent Python web framework
- React team for the powerful UI library
- The open-source community for inspiration and tools

---

**Built with ❤️ as a full-stack learning project**

*Ripple - Making waves in fundraising*

# Fundraiser Platform - Backend Setup

FastAPI backend for the fundraiser platform with MySQL database.

## Prerequisites

- Python 3.11+ (tested with Python 3.13)
- Docker Desktop (for MySQL)
- `uv` package manager

**Note:** This project uses `bcrypt` directly (not `passlib`) for Python 3.13 compatibility.

## Project Structure

```
.
├── docker-compose.yml    # MySQL database configuration
├── backend/
│   ├── main.py          # FastAPI application entry point
│   ├── database.py      # SQLAlchemy configuration
│   ├── models.py        # Database models
│   ├── pyproject.toml   # Project dependencies (uv)
│   └── .env.example     # Environment variables template
```

## Setup Instructions

### 1. Start the MySQL Database

From the project root directory:

```bash
# Start MySQL container in the background
docker-compose up -d

# Check that MySQL is running
docker-compose ps

# View MySQL logs (optional)
docker-compose logs db
```

The database will be accessible at `localhost:3306` with the following credentials:
- Database: `fundraiser_dev`
- User: `fundraiser_user`
- Password: `fundraiser_pass`

### 2. Set Up the Backend Environment

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment and install dependencies with uv
uv venv
source .venv/bin/activate  # On macOS/Linux

# Install dependencies (note the quotes around uvicorn[standard] for zsh)
uv pip install fastapi 'uvicorn[standard]' sqlalchemy pymysql cryptography python-dotenv pydantic pydantic-settings bcrypt 'python-jose[cryptography]' python-multipart email-validator

# Create your .env file from the example
cp .env.example .env

# IMPORTANT: Generate a secure secret key for JWT tokens
# Run this command and copy the output to your .env file
openssl rand -hex 32
```

### 3. Run the FastAPI Application

```bash
# Make sure you're in the backend directory with venv activated
uvicorn main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Test the Setup

Visit http://localhost:8000/docs to see the interactive API documentation.

Try these endpoints:
- `GET /` - Welcome message
- `GET /health` - Health check (verifies database connection)
- `GET /users/count` - Count of users in database (will be 0 initially)

## Development Workflow

### Running the Application

```bash
# Start MySQL (if not already running)
docker-compose up -d

# Activate virtual environment
cd backend
source .venv/bin/activate

# Run the development server (excluding .venv from auto-reload)
uvicorn main:app --reload --reload-exclude '.venv/*'
```

### Stopping the Application

```bash
# Stop FastAPI: Ctrl+C in the terminal

# Stop MySQL container
docker-compose down

# Stop and remove all data (careful!)
docker-compose down -v
```

### Database Management

```bash
# Connect to MySQL CLI
docker exec -it fundraiser_db mysql -u fundraiser_user -pfundraiser_pass fundraiser_dev

# View tables
SHOW TABLES;

# View users table structure
DESCRIBE users;

# Query users
SELECT * FROM users;
```

## Next Steps

1. **Test the new features** - Run `./test_campaigns.sh` to test campaigns and givers
2. **Add donation endpoints** - Create endpoints for processing donations
3. **Integrate Stripe** - Add payment processing for donations
4. **Add image uploads** - Integrate S3 for campaign images
5. **Build the React frontend** - Create UI to interact with these endpoints
6. **Add email notifications** - Notify users of donations and campaign updates

## Testing

### Run Tests
```bash
# Test authentication flow
./test_auth.sh

# Test complete platform (campaigns, givers, etc.)
./test_campaigns.sh
```

### Clean Up Test Data
```bash
# Remove all test users and their data
./cleanup_db.sh
```

The cleanup script safely removes:
- Test users (usernames starting with `testuser_`)
- Their giver profiles
- Their campaigns
- Their donations

## Authentication

The backend now includes full JWT-based authentication with auto-generated giver profiles:

### Available Endpoints:
- `POST /auth/register` - Register a new user (auto-creates giver profile)
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info (protected)
- `GET /protected` - Example protected endpoint

### Campaign Management:
- `POST /campaigns/` - Create a campaign (fundraising/event/adhoc)
- `GET /campaigns/` - List campaigns with filters
- `GET /campaigns/{id}` - Get campaign details
- `PUT /campaigns/{id}` - Update campaign
- `DELETE /campaigns/{id}` - Cancel campaign
- `GET /campaigns/my/campaigns` - Get your campaigns

### Giver Profiles & Donations:
- `GET /givers/profile/me` - Get your giver profile
- `PUT /givers/profile/me` - Update your profile
- `GET /givers/profile/{user_id}` - View public profile
- `GET /givers/profile/me/donations` - Your donation history
- `GET /givers/leaderboard` - Top givers leaderboard

### Quick Test:
```bash
# Run comprehensive test
./test_campaigns.sh

# Or test authentication only
./test_auth.sh
```

**See [AUTHENTICATION.md](AUTHENTICATION.md) for detailed authentication guide.**

## Campaign Types

Ripple supports three types of campaigns:

1. **Fundraising** - Traditional campaigns with goals and deadlines
2. **Event** - Time-bound event fundraising (e.g., charity gala)
3. **Ad-hoc Giving** - Simple one-time giving opportunities

## Giver Profiles

Every user automatically gets a giver profile that tracks:
- Total donated amount
- Number of donations
- Giving history
- Public/private visibility settings
- Individual or company profile type

## Project Structure

```
.
├── docker-compose.yml    # MySQL database configuration
├── AUTHENTICATION.md     # Authentication testing guide
├── test_auth.sh          # Authentication test script
├── test_campaigns.sh     # Comprehensive test script
├── backend/
│   ├── main.py          # FastAPI application entry point
│   ├── database.py      # SQLAlchemy configuration
│   ├── models.py        # Database models (User, Campaign, Donation, GiverProfile)
│   ├── schemas.py       # Pydantic schemas for validation
│   ├── auth.py          # Authentication utilities
│   ├── routers/         # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py      # Authentication endpoints
│   │   ├── campaigns.py # Campaign CRUD endpoints
│   │   └── givers.py    # Giver profile & donation endpoints
│   ├── pyproject.toml   # Project dependencies (uv)
│   └── .env.example     # Environment variables template
```

## Database Models

### User
- Authentication and account management
- One-to-many relationship with campaigns
- One-to-one relationship with giver profile

### Campaign
- Three types: fundraising, event, adhoc_giving
- Tracks goal amount, current amount, and status
- Belongs to a creator (User)

### GiverProfile
- Individual or company profiles
- Tracks total donated and donation count
- Public/private visibility settings

### Donation
- Links givers to campaigns
- Tracks payment status (pending/completed/failed/refunded)
- Supports anonymous donations and messages

## Useful Commands

```bash
# Add a new dependency
uv pip install package-name

# Update dependencies
uv pip install --upgrade package-name

# Check what's installed
uv pip list

# Freeze requirements (optional)
uv pip freeze > requirements.txt

# Run tests (when you add them)
pytest
```

## Troubleshooting

### MySQL connection issues

If you get `Can't connect to MySQL server`:
1. Check Docker is running: `docker ps`
2. Check MySQL container is healthy: `docker-compose ps`
3. Wait a few seconds for MySQL to initialise fully
4. Check logs: `docker-compose logs db`

### Port already in use

If port 3306 or 8000 is already in use:
- For MySQL: Change the port in `docker-compose.yml` (e.g., `"3307:3306"`)
- For FastAPI: Run with `uvicorn main:app --reload --port 8001`

### Import errors

Make sure you're in the backend directory and the virtual environment is activated:
```bash
cd backend
source .venv/bin/activate
```

### Bcrypt / Python 3.13 compatibility

If you encounter bcrypt errors with Python 3.13:
- This project uses `bcrypt` directly (v4.0+) instead of `passlib`
- If you see errors about `passlib`, uninstall it: `uv pip uninstall passlib`
- Reinstall dependencies: `uv pip install bcrypt`

## Environment Variables

Key variables in `.env`:

- `DATABASE_URL` - MySQL connection string
- `SECRET_KEY` - Secret key for JWT tokens (change in production!)
- `DEBUG` - Enable debug mode (True for development)

## Git Commits

This project uses Conventional Commits. Examples:

```bash
git commit -m "feat: add user authentication endpoints"
git commit -m "fix: resolve database connection timeout"
git commit -m "docs: update README with deployment instructions"
```
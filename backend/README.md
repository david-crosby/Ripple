# Fundraiser Platform - Backend Setup

FastAPI backend for the fundraiser platform with MySQL database.

## Prerequisites

- Python 3.11+
- Docker Desktop (for MySQL)
- `uv` package manager

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
uv pip install fastapi 'uvicorn[standard]' sqlalchemy pymysql cryptography python-dotenv pydantic pydantic-settings

# Create your .env file from the example
cp .env.example .env
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

1. **Add authentication** - Implement JWT-based authentication
2. **Create more models** - Campaign, Donation, etc.
3. **Add CRUD routes** - Create endpoints for managing resources
4. **Set up the frontend** - Create React app with Vite
5. **Integrate Stripe** - Add payment processing

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
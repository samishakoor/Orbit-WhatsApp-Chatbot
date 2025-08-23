# Orbit-WhatsApp-Chatbot

A multimodal WhatsApp Chatbot.

## 🚀 Quick Start

### Prerequisites

- Python 3.13
- uv (Python package manager)

### Installation

1. **Install uv** (if not already installed):

   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone the repository**:

   ```bash
   git clone <your-repo-url>
   cd Orbit-WhatsApp-Chatbot
   ```

3. **Create and activate virtual environment**:

   ```bash
   uv venv
   source .venv/bin/activate  # On Linux/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```

4. **Install dependencies**:

   ```bash
   uv pip install -e .
   ```

5. **Run the application**:
   ```bash
   uv run python run.py
   ```

## 🔧 Development Setup

### Install development dependencies

```bash
uv pip install -e .[dev]
```

### Run tests

```bash
uv run pytest
```

### Code formatting

```bash
uv run black .
uv run isort .
```

### Type checking

```bash
uv run mypy .
```

## 📦 Dependency Management

This project uses **uv** for dependency management instead of pip. Here are the key commands:

### Adding new dependencies

```bash
uv add package_name          # Add to main dependencies
uv add --dev package_name    # Add to dev dependencies
```

### Installing dependencies

```bash
uv pip install -e .          # Install main dependencies
uv pip install -e .[dev]     # Install dev dependencies
uv pip install -e .[test]    # Install test dependencies
uv pip install -e .[docs]    # Install documentation dependencies
```

### Updating dependencies

```bash
uv lock                      # Update lock file
uv pip install -e .          # Install updated dependencies
```

## 🔄 Migration from pip to uv

If you're migrating from the old pip-based setup:

1. **Run the migration script**:

   ```bash
   python migrate_to_uv.py
   ```

2. **Or migrate manually**:

   ```bash
   # Backup requirements.txt
   mv requirements.txt requirements.txt.backup

   # Create uv environment
   uv venv

   # Install dependencies
   uv pip install -e .

   # Generate lock file
   uv lock
   ```

## 🏗️ Project Structure

```
Orbit-WhatsApp-Chatbot/
├── app/                    # Application code
│   ├── api/               # API endpoints
│   ├── core/              # Core configuration and dependencies
│   ├── db/                # Database models and session management
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Business logic services
├── alembic/               # Database migrations
├── pyproject.toml         # Project configuration and dependencies
├── .uv/                   # uv configuration
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🚀 Running the Application

### Development server

```bash
uv run python run.py
```

### Production server

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Database migrations

```bash
uv run alembic upgrade head
```

## 📚 API Documentation

Once the application is running, you can access:

- **Interactive API docs**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 🔐 Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname
# or for SQLite (default)
DATABASE_URL=sqlite:///./app.db

# Security
SECRET_KEY=your-secret-key-here

# Environment
ENVIRONMENT=development
DEBUG=true
```

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_auth.py

# Run with verbose output
uv run pytest -v
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and formatting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:

- Check the [documentation](https://docs.astral.sh/uv/)
- Open an [issue](https://github.com/yourusername/orbit-whatsapp-chatbot/issues)
- Contact the development team

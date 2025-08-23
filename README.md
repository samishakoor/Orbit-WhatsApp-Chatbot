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

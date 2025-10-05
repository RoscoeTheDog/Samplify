# Samplify - Media Library Automation Tool

Samplify is a tool designed to help content creators organize their media libraries through automated processing with customizable templates. Process different media types to various output locations using keywords, regex patterns, or media metadata attributes.

**Current Status**: 🚧 **Django Web UI Migration in Progress**

This project is transitioning from a CLI-based tool to a modern Django web application using the BMAD (Business Management and Development) methodology.

---

## Features

- **Real-time file detection** - Automated monitoring of input directories
- **Customizable processing rules** - Define output destinations with filters
- **Multi-processing support** - Efficient batch processing using all CPU cores
- **GPU acceleration** - Hardware-accelerated encoding where available
- **Wide file support** - FFmpeg for audio/video, Pillow for images
- **Regex pattern matching** - Advanced filename and type filtering
- **Web-based UI** - Browser interface for schema management (in development)

---

## Quick Start

### Prerequisites

- **Python 3.10+** installed and in PATH
- **Git** for cloning the repository
- **Internet connection** for dependency installation

### Installation (Clone-to-Run)

#### Windows

```bash
# Clone repository
git clone https://github.com/RoscoeTheDog/Samplify.git
cd Samplify

# Run automated setup script
setup_env.bat

# The script will:
# - Create virtual environment
# - Install all dependencies
# - Provide next steps
```

#### macOS / Linux

```bash
# Clone repository
git clone https://github.com/RoscoeTheDog/Samplify.git
cd Samplify

# Run automated setup script
chmod +x setup_env.sh
./setup_env.sh

# The script will:
# - Create virtual environment
# - Install all dependencies
# - Provide next steps
```

### Manual Setup (Alternative)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Run Django migrations (when Django is set up)
python manage.py migrate

# Start development server
python manage.py runserver
```

---

## Project Structure

```
Samplify/
├── docs/              # Comprehensive project documentation
├── setup_env.bat      # Windows setup script
├── setup_env.sh       # macOS/Linux setup script
├── requirements.txt   # Core dependencies
├── requirements-dev.txt  # Development tools
├── .gitignore         # Git exclusion patterns
└── README.md          # This file
```

---

## Documentation

Full documentation is available in the `/docs` directory:

- **[Project Brief](docs/brief.md)** - Project overview and goals
- **[PRD (Product Requirements)](docs/prd/index.md)** - Detailed requirements
- **[Architecture](docs/architecture/index.md)** - Technical design
- **[User Stories](docs/stories/index.md)** - Implementation roadmap
- **[Coding Standards](docs/architecture/coding-standards.md)** - Development guidelines

Quick access: [Developer Quick Start Guide](docs/README.md#quick-start-for-developers)

---

## Development

This project follows a structured development workflow using the BMAD methodology:

- **Git Workflow**: See [Development Workflow Requirements](docs/prd/requirements.md#development-workflow-requirements) (DW1-DW6)
- **Coding Standards**: See [CS1-CS13 Standards](docs/architecture/coding-standards.md)
- **Testing Strategy**: See [Testing Documentation](docs/architecture/testing-strategy.md)

### Virtual Environment

Always activate the virtual environment before development:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

To deactivate:
```bash
deactivate
```

---

## Technology Stack

- **Backend**: Django 4.2 LTS (Python 3.10+)
- **Database**: SQLite with WAL mode
- **Frontend**: HTML/CSS/JavaScript (vanilla, no frameworks)
- **Media Processing**: FFmpeg, Pillow
- **File Monitoring**: Watchdog
- **Logging**: Loguru

See [Tech Stack Documentation](docs/architecture/tech-stack.md) for complete details.

---

## Platform Support

- ✅ **Windows 10/11** (64-bit)
- ✅ **macOS 12+** (Monterey and later)
- ✅ **Linux** (Ubuntu 20.04+, Debian 11+, Fedora 35+)

---

## License

*License information to be added*

---

## Project History

- **v0.1-pre-bmad** - Original CLI-based implementation (independent development)
- **Current** - Django Web UI migration using BMAD methodology

See the `original` branch for the pre-BMAD baseline.

---

**For detailed setup instructions, troubleshooting, and development guidelines, see the [full documentation](docs/README.md).**

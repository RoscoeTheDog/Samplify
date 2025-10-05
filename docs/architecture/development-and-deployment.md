# Development and Deployment

### Local Development Setup

**Current State** (no formal setup):
1. Clone repository
2. ⚠️ **Unknown dependencies** - no requirements file
3. Ensure ffmpeg installed and in system PATH
4. Run `python __main__.py` (creates user directories and database automatically)

**Known Issues**:
- Database drops on every run (development mode still active)
- No virtual environment configuration
- Windows-only (hardcoded paths, WMIC dependency)

### Build and Deployment Process

**No build process exists** - this is a Python script

- **Deployment**: Manual copy (not packaged)
- **Environments**: Only local development
- **Configuration**: XML templates in `%USERPROFILE%\Documents\Samplify\Templates\`

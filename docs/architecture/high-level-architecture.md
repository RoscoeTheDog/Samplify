# High Level Architecture

### Technical Summary

Samplify is currently a **Python-based CLI script** that processes media files (audio, video, images) based on XML-defined templates. It uses:

- **Multiprocessing** for parallel media conversion
- **Watchdog** for file system monitoring
- **FFmpeg** (via subprocess) for audio/video processing
- **PIL** for image processing
- **SQLAlchemy** for database ORM
- **SQLite** for data persistence
- **Structlog** for structured logging

The architecture is **brownfield script-based** with manual orchestration in `__main__.py`. There is **no web interface** - all configuration is done via XML files stored in user documents folder.

### Actual Tech Stack

| Category           | Technology     | Version         | Notes                                           |
| ------------------ | -------------- | --------------- | ----------------------------------------------- |
| Runtime            | Python         | 3.x (inferred)  | No explicit version constraint found            |
| Database           | SQLite         | N/A             | Via SQLAlchemy, database file in `/database/`  |
| ORM                | SQLAlchemy     | Unknown version | Used for all database operations                |
| Logging            | Structlog      | Unknown version | Custom processors and console renderer          |
| Media Processing   | FFmpeg         | External binary | Via subprocess calls, not bundled               |
| Image Processing   | PIL            | Unknown version | For image format conversions                    |
| File Watching      | Watchdog       | Unknown version | For real-time input directory monitoring        |
| Multiprocessing    | Python stdlib  | Built-in        | Using `multiprocessing.Process` and `deque`     |
| XML Parsing        | ElementTree    | Built-in        | For template configuration parsing              |
| GPU Detection      | WMIC (Windows) | System tool     | Windows-specific GPU vendor detection           |
| **Missing**        | Requirements   | **NONE FOUND**  | ⚠️ No requirements.txt or dependency management |

### Repository Structure Reality Check

- **Type**: Single Python project (not Django, not web-based)
- **Package Manager**: None detected (no requirements.txt, setup.py, or pyproject.toml found)
- **Notable**: User data stored in `%USERPROFILE%\Documents\Samplify` (not in project directory)

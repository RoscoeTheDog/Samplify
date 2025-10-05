# Story 1.4: FFmpeg Detection & Download Service

### User Story
As a **developer**,
I want **an automated FFmpeg detection and download service**,
So that **the system can bundle platform-specific FFmpeg binaries without git repository bloat**.

### Story Context
**Existing System Integration:**
- Integrates with: Story 1.1 (Django project), existing FFmpeg subprocess calls
- Technology: Python subprocess, urllib/requests for downloads
- Follows pattern: FR7 FFmpeg binary management requirement
- Touch points: FFmpeg path resolution, media processing services

### Acceptance Criteria

**Functional Requirements:**
1. FFmpeg detection service created as Django utility (`utils/ffmpeg.py`)
2. OS detection logic (Windows/macOS/Linux) using `platform.system()`
3. Binary path resolution checks `/bin/<platform>/ffmpeg[.exe]` first
4. Automatic download logic if FFmpeg not found:
   - Windows: Download from `https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip`
   - macOS: Download from `https://evermeet.cx/ffmpeg/ffmpeg-<version>.zip`
   - Linux: Download from `https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz`
5. Extract downloaded archive to `/bin/<platform>/`
6. Verify FFmpeg works via `ffmpeg -version` subprocess call
7. Fallback: Display manual installation instructions if auto-download fails
8. Cache FFmpeg path in Django cache for performance

**Integration Requirements:**
9. Service called BEFORE any media operations (FR7 requirement)
10. Path resolution works across all platforms
11. FFmpeg subprocess calls use resolved path
12. Service integrates with existing media processing handlers

**Quality Requirements:**
13. Download completes within 60 seconds (timeout)
14. Binary verification succeeds on all platforms
15. Error messages are clear and actionable
16. No FFmpeg binaries committed to git (.gitignore configured)

### Technical Notes
- **Integration Approach:** Utility service called on Django startup, caches FFmpeg path
- **Existing Pattern Reference:** FR7 FFmpeg binary management, CR6 platform support
- **Key Constraints:** Must work offline after initial download, no git bloat

### Definition of Done
- [x] FFmpeg detection service implemented
- [x] Auto-download works on Windows/macOS/Linux
- [x] Binary verification succeeds
- [x] Manual installation instructions provided
- [x] .gitignore excludes /bin/ directory
- [x] Documentation updated with FFmpeg setup details

### Risk Assessment
- **Primary Risk:** FFmpeg download URLs become unavailable
- **Mitigation:** Provide manual installation instructions, document alternative sources
- **Rollback:** Remove auto-download, require manual FFmpeg installation

---

<!-- Powered by BMAD™ Core -->

# Manage Profiles

## Purpose

This task provides a comprehensive interface for viewing, editing, deleting, exporting, and importing project profile profiles.

## Overview

Profiles are stored in `~/.bmad-profiles/` and can be managed through this task. Operations include:

- **List** - View all available profiles
- **View** - Display profile details
- **Edit** - Modify profile configuration
- **Delete** - Remove profiles
- **Export** - Share profiles with team
- **Import** - Load profiles from team
- **Search** - Find profiles by keyword

## Main Menu

When user invokes `/manage-profiles`:

```
💾 Profile Manager

Available profiles: 3

1. List all profiles
2. View profile details
3. Edit profile
4. Delete profile
5. Export profile
6. Import profile
7. Search profiles
8. Show profile directory location
9. Exit

Select 1-9:
```

## Operation 1: List All Profiles

Display all profiles with summary information:

```javascript
const profileManager = require('../../tools/lib/profile-manager');
const profiles = profileManager.listProfiles();

profiles.forEach((profile, index) => {
  console.log(`${index + 1}. ${profile.name}`);
  console.log(`   ID: ${profile.id}`);
  console.log(`   Created: ${new Date(profile.created).toLocaleDateString()}`);
  if (profile.based_on && profile.based_on.length > 0) {
    console.log(`   Templates: ${profile.based_on.join(', ')}`);
  }
  if (profile.description) {
    console.log(`   ${profile.description}`);
  }
  console.log('');
});
```

Example output:

```
📋 Your Profiles (3)

1. My Django Setup
   ID: my-django-setup
   Created: Oct 1, 2025
   Templates: base/coding-style-base, languages/python/coding-style-python, frameworks/django/django-context
   Django 5.0 project with Ruff linting, mypy type checking, and pytest

2. React TypeScript Modern
   ID: react-ts-modern
   Created: Sep 28, 2025
   Templates: base/coding-style-base, languages/typescript/coding-style-typescript, frameworks/react/react-context
   React 18 + TypeScript + Tailwind + Zustand

3. C++ Game Development
   ID: cpp-game-dev
   Created: Sep 15, 2025
   Templates: base/coding-style-base, languages/cpp/coding-style-cpp
   C++20 game development with Unreal Engine patterns

[R]eturn to menu | [E]xit
```

## Operation 2: View Profile Details

Show detailed information about a specific profile:

```
Enter profile ID or number from list:
> my-django-setup

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Profile: My Django Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID: my-django-setup
Created: October 1, 2025
Version: 1.0
BMAD Version: 2.0.0

Description:
Django 5.0 project with Ruff linting, mypy type checking, and pytest

Tags: python, django, web, backend

Based on Templates:
  - base/coding-style-base
  - languages/python/coding-style-python
  - frameworks/django/django-context

Configuration:
  Python:
    - Version: 3.12+
    - Formatter: Ruff
    - Linter: Ruff
    - Type Checker: mypy
    - Line Length: 100
    - Type Hints: Required-All
    - Docstring Format: Google

  Django:
    - Version: 5.x
    - DRF: Yes
    - Database: PostgreSQL
    - View Style: CBV-Primary
    - Test Framework: pytest
    - Admin Usage: Moderate

[... more configuration ...]

File Location:
/Users/username/.bmad-profiles/my-django-setup.yaml

Options:
1. Edit this profile
2. Export this profile
3. Delete this profile
4. Use in current project
5. Return to menu

Select 1-5:
```

## Operation 3: Edit Profile

Allow modification of profile metadata and configuration:

```
Editing profile: my-django-setup

What would you like to edit?
1. Name
2. Description
3. Tags
4. Configuration values
5. Cancel

Select 1-5:
```

### Edit Configuration Values

```
Current configuration has 47 values.

Options:
1. Edit specific value (guided)
2. Open in text editor
3. Regenerate from scratch
4. Cancel

Select 1-4:
```

If user selects "Edit specific value":

```
Select category:
1. Python (8 settings)
2. Django (12 settings)
3. Code Style (15 settings)
4. Comment Guidelines (7 settings)
5. Experience Levels (5 settings)

Select 1-5:
> 1

Python Settings:
1. python_version: "3.12+"
2. formatter: "Ruff"
3. linter: "Ruff"
4. type_checker: "mypy"
5. line_length: 100
6. type_hints_level: "Required-All"
7. docstring_format: "Google"
8. venv_approach: "poetry"

Select setting to edit (1-8) or [B]ack:
> 5

Current value: 100
New value:
> 120

✓ Updated line_length to 120

Continue editing? (y/n):
```

After editing:

```
✅ Profile updated successfully!

Changes made:
  - line_length: 100 → 120

Profile version incremented: 1.0 → 1.1

[R]eturn to menu | [E]xit
```

## Operation 4: Delete Profile

Remove a profile with confirmation:

```
Enter profile ID to delete:
> old-profile

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  WARNING: Delete Profile
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Profile: Old Profile (old-profile)
Created: August 15, 2025
Last used: Never

This action CANNOT be undone.
The profile file will be permanently deleted.

Type the profile ID to confirm deletion:
> old-profile

✅ Profile "old-profile" deleted successfully!
Removed: ~/.bmad-profiles/old-profile.yaml

[R]eturn to menu | [E]xit
```

## Operation 5: Export Profile

Export profile to a file for sharing:

```
Enter profile ID to export:
> my-django-setup

Export format:
1. YAML file (portable, readable)
2. JSON file (for tooling)
3. Both

Select 1-3:
> 1

Export location (default: ./my-django-setup.yaml):
>

✅ Profile exported successfully!

File: ./my-django-setup.yaml
Size: 4.2 KB

To share with your team:
1. Commit this file to your repo
2. Team members can import with:
   /manage-profiles → Import profile → my-django-setup.yaml

Or share directly:
npx bmad-method profile import my-django-setup.yaml

[R]eturn to menu | [E]xit
```

Implementation:

```javascript
const profileManager = require('../../tools/lib/profile-manager');

function exportProfile(profileId, exportPath) {
  const success = profileManager.exportProfile(profileId, exportPath);

  if (success) {
    const stats = fs.statSync(exportPath);
    console.log(`✅ Profile exported successfully!`);
    console.log(`File: ${exportPath}`);
    console.log(`Size: ${(stats.size / 1024).toFixed(1)} KB`);
  } else {
    console.error(`❌ Export failed`);
  }
}
```

## Operation 6: Import Profile

Import profile from a file:

```
Import Profile

Options:
1. Import from file path
2. Import from URL
3. Browse recent exports
4. Cancel

Select 1-4:
> 1

Enter file path:
> ./team-django-profile.yaml

Reading profile file...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 Import Preview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Profile: Team Django Standards
ID: team-django-profile
Created: September 1, 2025
Templates: base/coding-style-base, languages/python/coding-style-python, frameworks/django/django-context

Configuration includes:
  - Python 3.11+ with Black formatter
  - Django 4.2 patterns
  - pytest for testing
  - Strict type checking with mypy
  [... more details ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Options:
1. Import with original ID (team-django-profile)
2. Import with custom ID
3. View full configuration
4. Cancel

Select 1-4:
> 1

✅ Profile imported successfully!

Saved as: team-django-profile
Location: ~/.bmad-profiles/team-django-profile.yaml

To use this profile:
/init-profile

[R]eturn to menu | [E]xit
```

### Import from URL

```
Enter profile URL:
> https://raw.githubusercontent.com/company/profiles/main/django-standard.yaml

Downloading profile...
✓ Downloaded successfully

[... continues with import preview ...]
```

### Handle Conflicts

If profile ID already exists:

```
⚠️ Conflict: Profile "my-django-setup" already exists

Existing profile:
  Name: My Django Setup
  Created: October 1, 2025

Importing profile:
  Name: My Django Setup
  Created: September 28, 2025

Options:
1. Overwrite existing profile
2. Keep both (import as "my-django-setup-2")
3. Compare profiles
4. Cancel import

Select 1-4:
```

## Operation 7: Search Profiles

Search profiles by keyword:

```
Search profiles

Enter search term (name, description, or tag):
> django

Found 2 profiles matching "django":

1. My Django Setup (my-django-setup)
   Django 5.0 project with Ruff linting...
   Tags: python, django, web, backend

2. Team Django Standards (team-django-profile)
   Team standards for Django 4.2 projects
   Tags: python, django, team-standard

Select profile (1-2) to view details, or [B]ack:
```

Implementation:

```javascript
const profileManager = require('../../tools/lib/profile-manager');

function searchProfiles(query) {
  const results = profileManager.searchProfiles(query);

  if (results.length === 0) {
    console.log(`No profiles found matching "${query}"`);
    return;
  }

  console.log(`Found ${results.length} profile(s) matching "${query}":\n`);
  results.forEach((profile, index) => {
    console.log(`${index + 1}. ${profile.name} (${profile.id})`);
    if (profile.description) {
      console.log(`   ${profile.description}`);
    }
    if (profile.tags) {
      console.log(`   Tags: ${profile.tags.join(', ')}`);
    }
    console.log('');
  });
}
```

## Operation 8: Show Profile Directory

Display the profile storage location:

```
📁 Profile Directory

Location: /Users/username/.bmad-profiles/

Contents:
  my-django-setup.yaml (4.2 KB)
  react-ts-modern.yaml (3.8 KB)
  cpp-game-dev.yaml (5.1 KB)
  profiles-index.json (0.8 KB)

Total: 3 profiles (13.9 KB)

You can:
  - Manually edit files in this directory
  - Backup this directory for safekeeping
  - Share files with team members
  - Delete this directory to reset all profiles

[O]pen in file manager | [R]eturn to menu | [E]xit
```

## Error Handling

### Corrupted Profile File

```
❌ Error: Could not load profile "broken-profile"

Reason: Invalid YAML syntax at line 42
Details: Unexpected token

Options:
1. Attempt to repair automatically
2. Open file in text editor to fix manually
3. Delete corrupted profile
4. Restore from backup (if available)

Select 1-4:
```

### Empty Profile Directory

```
📂 No profiles found

Location: ~/.bmad-profiles/

You don't have any saved profiles yet.

To create your first profile:
1. Setup project profile in a project: /init-profile
2. Save as profile when prompted

Or import a shared profile:
/manage-profiles → Import profile

[R]eturn to menu | [E]xit
```

## Batch Operations

### Export Multiple Profiles

```
Would you like to export multiple profiles?

Options:
1. Export all profiles
2. Select profiles to export
3. Cancel

Select 1-3:
> 1

Export all 3 profiles to directory:
> ./profiles-backup/

Creating directory...
Exporting profiles...
  ✓ my-django-setup.yaml
  ✓ react-ts-modern.yaml
  ✓ cpp-game-dev.yaml

✅ Exported 3 profiles to ./profiles-backup/
```

### Delete Multiple Profiles

```
⚠️ Delete Multiple Profiles

Select profiles to delete:
[ ] 1. my-django-setup
[x] 2. old-profile-v1
[x] 3. experimental-profile
[ ] 4. react-ts-modern

Use [SPACE] to toggle, [ENTER] to confirm

Selected: 2 profiles

Type DELETE to confirm:
> DELETE

✅ Deleted 2 profiles successfully
```

## Integration Points

This task uses:

- `tools/lib/profile-manager.js` - All profile operations
- `~/.bmad-profiles/` - Profile storage
- File system operations for import/export

## Notes for AI Agents

- **Provide clear navigation**: Always show way back to menu
- **Confirm destructive actions**: Double-check before deleting
- **Validate input**: Check profile IDs and file paths
- **Show feedback**: Confirm success/failure of operations
- **Handle errors gracefully**: Provide recovery options
- **Educate users**: Explain what profiles are and why they're useful

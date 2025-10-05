# /save-profile Task

When this command is used, execute the following task:

<!-- Powered by BMAD™ Core -->

# Save Project Profile

## Purpose

This task packages the current project's project profile configuration into a reusable profile. Profiles can be loaded in future projects to skip the elicitation process.

## When to Use

- After creating project profile for a project
- When you want to reuse your preferences in future similar projects
- To share team standards with other developers
- After customizing an existing profile

## Workflow

1. **Validate profile exists** - Check for `.ai/profiles/` files
2. **Read templates manifest** - Determine what templates were used
3. **Extract configuration** - Parse generated files for variable values
4. **Prompt for metadata** - Get profile name and description
5. **Save profile** - Write to `~/.bmad-profiles/`
6. **Confirm success** - Show location and usage instructions

## Step 1: Validate Profile Exists

Check for required files:

```javascript
const fs = require('fs');
const path = require('path');

const profilesDir = path.join(process.cwd(), '.ai', 'profiles');
const manifestPath = path.join(process.cwd(), '.ai', 'templates-manifest.json');

if (!fs.existsSync(profilesDir)) {
  console.error('❌ No project profile found in this project.');
  console.error('Run /init-profile first.');
  return;
}
```

If no profile exists:

```
❌ No project profile found in this project.

To create project profile first, run:
/init-profile

Or if you have existing profile files, ensure they are in:
.ai/profiles/
```

## Step 2: Read Templates Manifest

Load the manifest to understand what templates were used:

```javascript
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

console.log(`📋 Context created from templates:`);
manifest.templates_used.forEach((t) => console.log(`  - ${t}`));
```

Example output:

```
📋 Context created from templates:
  - base/coding-style-base
  - languages/python/coding-style-python
  - frameworks/django/django-context

Original profile used: my-django-profile (if applicable)
Generated: 2025-10-01
```

## Step 3: Extract Configuration

Parse the generated markdown files to extract variable values:

```javascript
// Read generated context files
const files = ['coding-standards.md', 'comment-guidelines.md', 'experience-levels.md'];

const conversationResults = {};
const renderedSections = {};

files.forEach((file) => {
  const filePath = path.join(contextDir, file);
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');
    renderedSections[file] = content;

    // Extract key-value pairs from markdown
    // This is a simplified extraction - actual implementation
    // would parse based on template structure
    extractVariables(content, conversationResults);
  }
});
```

Show extracted configuration:

```
📊 Configuration Summary:
Python:
  - Version: 3.12+
  - Formatter: Ruff
  - Linter: Ruff
  - Type Checker: mypy
  - Docstring Format: Google

Django:
  - Version: 5.x
  - View Style: CBV-Primary
  - Test Framework: pytest
  - Admin Usage: Moderate

[... more settings ...]
```

## Step 4: Prompt for Metadata

Ask user for profile details:

```
💾 Save as Profile

Enter profile ID (lowercase, hyphens for spaces):
Examples: my-django-setup, python-ml-project, cpp-game-dev

Profile ID:
> _
```

After receiving ID:

```
Enter profile name (human-readable):
> My Django Setup

Enter description (optional):
> Django 5.0 project with Ruff linting, mypy type checking, and pytest

Tags (optional, comma-separated):
> python, django, web, backend
```

### Validation

Check if profile ID already exists:

```javascript
const profileManager = require('../../tools/lib/profile-manager');
const existingProfile = profileManager.getProfile(profileId);

if (existingProfile) {
  // Prompt for overwrite
}
```

If profile exists:

```
⚠️ Profile "my-django-setup" already exists

Existing profile:
- Name: My Django Setup
- Created: 2025-09-15
- Description: Django project with Ruff and pytest

Options:
1. Overwrite existing profile
2. Save as new profile with different ID
3. Cancel

Select 1-3:
```

## Step 5: Save Profile

Use the profile manager to save:

```javascript
const profileData = {
  profile: {
    id: profileId,
    name: name,
    description: description,
    tags: tags.split(',').map((t) => t.trim()),
    created: new Date().toISOString(),
    based_on: manifest.templates_used,
    version: '1.0',
    bmad_version: manifest.bmad_version || '2.0.0',
  },
  conversation_results: conversationResults,
  rendered_sections: renderedSections,
  metadata: {
    original_project: path.basename(process.cwd()),
    saved_from_profile: manifest.profile_used || null,
  },
};

const success = profileManager.saveProfile(profileId, profileData);
```

## Step 6: Confirm Success

Display success message with next steps:

```
✅ Profile saved successfully!

📁 Location: ~/.bmad-profiles/my-django-setup.yaml
📝 Name: My Django Setup
🏷️  Tags: python, django, web, backend

This profile includes:
  ✓ Coding standards (Ruff, mypy)
  ✓ Comment guidelines
  ✓ Experience levels
  ✓ Django-specific patterns

To use this profile in another project:
1. cd /path/to/new-project
2. /init-profile
3. Select "Use profile: my-django-setup"

To share with your team:
npx bmad-method profile export my-django-setup

To view all profiles:
/manage-profiles
```

## Edge Cases

### No Templates Manifest

If `.ai/templates-manifest.json` doesn't exist:

```
⚠️ No templates manifest found

This usually means the context was created manually.
We can still save a profile, but it won't include template information.

Options:
1. Continue saving profile (without template tracking)
2. Re-create context with /init-profile first
3. Cancel

Select 1-3:
```

### Partial Context Files

If some expected files are missing:

```
⚠️ Incomplete context found

Expected files:
✓ coding-standards.md (found)
✗ comment-guidelines.md (missing)
✗ experience-levels.md (missing)

Options:
1. Save profile with available files only
2. Complete context setup first
3. Cancel

Select 1-3:
```

### Modified from Original Profile

If context was loaded from a profile and modified:

```
📋 Original profile: my-django-profile
🔧 Modifications detected

You've modified the context since loading the profile.

Options:
1. Save as new profile (recommended)
2. Overwrite original profile
3. View differences
4. Cancel

Select 1-4:
```

If user selects "View differences":

```
Changes from original "my-django-profile":

Modified settings:
  - line_length: 88 → 100
  - test_framework: unittest → pytest
  + Added: type_hints_level: Required-All

New sections:
  + Custom error handling patterns
```

## Validation Rules

Before saving, validate:

1. **Profile ID format:**
   - Lowercase letters, numbers, hyphens only
   - No spaces or special characters
   - Not empty

2. **Name not empty:**
   - Must provide a human-readable name

3. **Valid YAML:**
   - Ensure generated profile is valid YAML

4. **Required fields:**
   - At least one context file must exist

Example validation:

```javascript
function validateProfileId(id) {
  if (!id || id.length === 0) {
    return { valid: false, error: 'Profile ID cannot be empty' };
  }

  if (!/^[a-z0-9-]+$/.test(id)) {
    return {
      valid: false,
      error: 'Profile ID must contain only lowercase letters, numbers, and hyphens',
    };
  }

  return { valid: true };
}
```

## Examples

### Example 1: First-Time Save

```
User: /save-context-profile

Agent: Reading current project profile...

📊 Configuration Summary:
TypeScript + React Project
  - TypeScript: 5.3
  - Formatter: Prettier
  - Linter: ESLint (Airbnb)
  - Testing: Vitest + React Testing Library
  - State: Zustand
  - Styling: Tailwind CSS

💾 Save as Profile

Profile ID:
User: react-ts-tailwind

Name:
User: React TypeScript with Tailwind

Description:
User: Modern React setup with TypeScript, Tailwind, Vitest, and Zustand

Tags:
User: react, typescript, tailwind, frontend

Agent: ✅ Profile saved successfully!

📁 Location: ~/.bmad-profiles/react-ts-tailwind.yaml
```

### Example 2: Overwriting Existing

```
User: /save-context-profile

Agent: Profile ID:
User: my-django-setup

Agent: ⚠️ Profile "my-django-setup" already exists
Created: 2025-09-15

Options:
1. Overwrite existing profile
2. Save as new profile
3. Cancel

User: 1

Agent: ⚠️ This will permanently replace the existing profile.
Proceed? (yes/no)

User: yes

Agent: ✅ Profile "my-django-setup" updated successfully!
```

## Integration Points

This task uses:

- `.ai/profiles/` - Source of context files
- `.ai/templates-manifest.json` - Template tracking
- `tools/lib/profile-manager.js` - Profile storage
- `~/.bmad-profiles/` - Profile directory

## Notes for AI Agents

- **Preserve all context**: Don't lose any configuration during extraction
- **Validate input**: Check profile ID format before saving
- **Provide feedback**: Show what's being saved
- **Handle errors gracefully**: Offer recovery options
- **Explain the value**: Help users understand why profiles are useful

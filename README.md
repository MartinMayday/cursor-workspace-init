# Cursor Workspace Templates

A collection of templates for initializing Cursor workspace configurations tailored to specific project types, languages, and frameworks.

## Purpose

This repository contains template files used by the `/init-cursorworkspace` slash command to generate project-specific Cursor IDE workspace files. These templates use placeholder syntax to be populated with project context extracted from codebase analysis.

## Template Structure

```
.
├── .cursorrules.template              # Main cursor rules template
├── source_list.json.template          # Knowledge base source list template
├── init-cursorworkspace.sh           # Shell script wrapper for the command
└── .cursor/
    ├── AGENTS.md.template             # Agent configuration template
    ├── rules/
    │   ├── level1-core.mdc.template              # Core rules (always loaded)
    │   ├── level2-architecture.mdc.template     # Architecture rules
    │   ├── level3-project-type.mdc.template      # Project type rules
    │   ├── level4-language.mdc.template          # Language-specific rules
    │   ├── level5-framework.mdc.template          # Framework-specific rules
    │   └── rules_manifest.json.template          # Rules manifest
    └── commands/
        ├── init-cursorworkspace.mdc              # Slash command file
        ├── commands_manifest.json.template       # Commands manifest
        ├── test-commands.mdc.template           # Test command templates
        ├── build-commands.mdc.template          # Build command templates
        ├── deploy-commands.mdc.template         # Deploy command templates
        └── docker-commands.mdc.template         # Docker command templates
```

## Placeholder Format

Templates use the following placeholder syntax:

```
<PLACEHOLDER: VARIABLE_NAME>
```

Example placeholders:
- `<PLACEHOLDER: PROJECT_NAME>` - Project name
- `<PLACEHOLDER: PRIMARY_LANGUAGE>` - Primary programming language
- `<PLACEHOLDER: FRAMEWORK>` - Framework name
- `<PLACEHOLDER: TECHNOLOGIES>` - Technology stack

## Conditional Placeholders

Templates support conditional blocks:

```
<PLACEHOLDER: IF_PYTHON>
... content for Python projects ...
<PLACEHOLDER: ENDIF_PYTHON>
```

## Usage

### Using the Slash Command

The `/init-cursorworkspace` slash command can be used directly in Cursor IDE. The command file (`.cursor/commands/init-cursorworkspace.mdc`) is included in this repository and should be copied to your project's `.cursor/commands/` directory.

### Using the Shell Script

Alternatively, you can use the `init-cursorworkspace.sh` shell script:

```bash
./init-cursorworkspace.sh
```

With options:
```bash
./init-cursorworkspace.sh --no-analyze          # Skip analysis if projectFile.md exists
./init-cursorworkspace.sh --skip-validation     # Skip validation step
./init-cursorworkspace.sh --project-root /path  # Specify project root
```

### Workflow

The initialization process:

1. Analyzes the codebase (or loads existing `projectFile.md`)
2. Creates/updates `projectFile.md` with project context
3. Pulls templates from this repository
4. Populates placeholders with project-specific values
5. Generates `.cursor/` workspace files
6. Validates the generated workspace
7. Generates a comprehensive report

## Template Updates

When updating templates:

1. Maintain placeholder format consistency
2. Test with various project types
3. Ensure all placeholders have corresponding context variables
4. Update this README if adding new templates

## License

These templates are provided as-is for use with Cursor IDE workspace initialization.

# Registry Schema

This file defines the canonical registry structure for the project scaffolding workflow.

## Purpose
The registry is the source of truth for:
- base templates
- optional packs
- dependencies and conflicts
- placeholder substitutions
- post-steps
- verification commands

## Top-level shape

```json
{
  "stack_defaults": {
    "kmp": {
      "auth_provider": "clerk",
      "theme_preset": "neutral"
    }
  },
  "packs": []
}
```

## Entry schema

```yaml
id: kmp_base
stack: kmp
kind: base # base | feature | infra
source: /absolute/path/or/git-url
requires: []
conflicts_with: []
owns:
  - composeApp/**
  - shared/**
placeholder_map:
  project_name: MyApp
  package_name: com.example.myapp
  package_path: com/example/myapp
  kmp_auth_include: ""
post_steps:
  - ./gradlew :shared:build
  - ./gradlew :composeApp:build
verify:
  - test -f local.properties || printf 'sdk.dir=/path/to/sdk\n' > local.properties
  - ./gradlew :shared:build
  - ./gradlew :composeApp:build
```

## Registry rules
- One base per scaffold.
- Packs must declare all files they own.
- `owns` is a list of relative glob patterns from the source root; the script only copies matching files.
- Packs must declare all required dependencies.
- Conflicts must be explicit.
- Verification commands must be runnable from the project root.
- All placeholders must be deterministic and documented.
- `placeholder_map` keys are generic: `{{key}}` can be used in file contents and copied relative paths.
- Keep optional include placeholders blank in the base entry and let selected packs fill them.
- The registry should not contain prose-only advice; keep it machine-readable.

## Suggested stack entries

### KMP base
- `kmp_base`
- `kmp_auth`
- `kmp_ui_theme`
- `kmp_room`
- `kmp_github`
- `kmp_ci`

### Next.js base
- `nextjs_base`
- `nextjs_auth`
- `nextjs_ui_theme`
- `nextjs_github`
- `nextjs_ci`

## Naming conventions
- Use snake_case for registry ids.
- Use lower-case stack names.
- Keep placeholder names stable across stacks.
- Keep verification commands minimal and deterministic.

## Next step
Create the resolver script that reads this registry and returns the ordered scaffold plan.

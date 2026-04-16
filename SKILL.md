---
name: project-scaffolding-with-skills-and-mcp
description: Design or implement reusable project-scaffolding workflows for KMP or Next.js using Skills, MCP, template registries, and deterministic module packs. Use when creating a project factory that copies/clones a base repo and optional modules like auth, UI/theming, Room, GitHub, or CI without reinventing structure.
---

# Project Scaffolding with Skills and MCP

Use this skill when building a project factory that must stay fast, deterministic, and easy for weaker models to operate.

## Core model
- Skill = routing and policy
- MCP = external tools/data integration
- Registry = source of truth for available templates/modules
- Script = deterministic copy/rename/verify execution

## Default architecture
1. Keep one thin router skill.
2. Keep stack/module truth in a registry.
3. Keep code structure in canonical templates.
4. Use scripts for file operations and validation.
5. Use MCP only for real integrations like filesystem, GitHub, or remote registries.

## Rules
- One stack per command path.
- One default auth provider per generated project.
- One default theme preset per generated project.
- Optional packs must be explicit flags.
- Never let the model invent structure from scratch if a template or module exists.
- Never hide a large opaque workflow behind one mega-tool.
- Build verification is mandatory before handoff.

## Recommended module packs
- Base KMP template
- Base Next.js template
- Auth pack
- UI/theming pack
- Room/data pack
- GitHub/CI pack

## Implementation order
1. Define the registry schema and canonical template locations.
2. Add deterministic resolver and pack-applier scripts.
3. Add build/test verification gates for KMP and Next.js.
4. Wire the thin skill to the registry and scripts.
5. Add GitHub/CI integrations behind explicit flags.
6. Verify the full flow end-to-end on both starter projects.

Deterministic script layer:
- `scripts/scaffold.py` resolves, applies, or creates a scaffold end-to-end
- `templates/` holds clean local scaffold roots when the live starter repo needs base-vs-pack separation
- `references/command-grammar.md` documents the supported CLI shape
- `references/example-registry.json` provides a machine-readable registry seed
- `references/local-starter-registry.json` points the same registry shape at the current local KMP and Next.js starter roots
- Scripts only substitute explicit `{{...}}` placeholders in file contents and copied relative paths; do not globally replace bare env names or prose tokens

See the implementation plan note in Obsidian: [[skills-mcp-project-scaffolding-implementation-plan]].

## Registry fields to define
- id
- stack
- kind (base, feature, infra)
- source
- requires
- conflicts_with
- owns
- placeholder_map
- post_steps
- verify

## Scaffolding flow
1. Parse stack and flags.
2. Resolve base template.
3. Resolve optional packs.
4. Apply in fixed order.
5. Replace placeholders.
6. Run build/test.
7. Stop on failure.
8. If requested, create/push GitHub repo and add CI.
9. Return a short status summary.

## Good defaults
- KMP: auth, UI, Room, CI as separate packs
- Next.js: auth, UI, CI as separate packs
- Theme should use tokens/constants, not hardcoded colors.
- Auth should use one provider implementation behind an interface.
- Room/data should stay isolated from UI.

## Validation
A scaffold is only done if:
- expected files exist
- names are correct
- build passes
- selected packs are wired
- GitHub/CI steps succeeded if requested

Portable Android SDK detection (KMP):
- `apply_plan()` automatically finds the Android SDK via `resolve_android_sdk()` (env vars: `ANDROID_HOME`, `ANDROID_SDK_ROOT`, `ANDROID_SDK`, then common macOS/Linux paths).
- If `local.properties` does not already exist, it is written with `sdk.dir=<detected_path>`.
- This makes the scaffold portable across developer machines without hardcoding SDK paths.
- CI systems that generate their own `local.properties` (e.g., via `android-sdk` action) take precedence because the script never overwrites an existing file.
- Registry `verify` entries for KMP base no longer need a `printf`/`test` step for `local.properties` — that is handled automatically.

Portable source path resolution (for use by other agents):
- Registry `source` entries support four path formats:
  - **Absolute paths** — used as-is (e.g., `/Users/mahdi/base-next-project/starter`).
  - **`$ENV_VAR`** — resolved from an environment variable (e.g., `$NEXTJS_TEMPLATE_ROOT`). The env var must be set at runtime.
  - **`templates/<path>`** — resolved relative to the skill base (e.g., `templates/kmp/base`). KMP pack sources always use this format so they travel with the skill.
  - **Relative paths** — resolved relative to the registry's parent directory (fallback for non-standard layouts).
- `apply_plan()` infers the skill base by walking up from the registry path: `<skill>/references/<registry>` → `<skill>`.
- This means the entire skill (templates + registry) is copy-paste portable to any machine. No hardcoded `/Users/mahdi` paths leak into the registry.
- For Next.js templates that live outside the skill dir, set `NEXTJS_TEMPLATE_ROOT` env var before running scaffold.

Real-world pitfalls discovered:
- Keep optional packs in a sibling pack workspace when authoring them, but import/copy that workspace into the target git repo before committing if the repo itself is the deliverable.
- Registry `source` paths should point at concrete pack roots.
- `owns` globs must match the final on-disk package layout exactly; a mismatch can silently produce nested duplicate package folders.
- For KMP packs, prefer compile-safe commonMain code only. Avoid JVM-only APIs in common code unless you provide expect/actual or platform-specific source sets.
- A successful `resolve` does not guarantee the pack sources compile; always run `create` and a real build on the generated scaffold.
- When the main repo is clean and the work lives in a sibling non-git workspace, create a feature branch in the parent repo first, import the workspace there, then verify with a build before commit.
- Template code should stay self-documenting; avoid memo-style comments unless the API contract is genuinely non-obvious.

## Anti-patterns
- Free-form rewrite of project structure
- Multiple auth providers by default
- Theme values scattered across screens
- Room mixed into UI logic
- One tool that does everything invisibly
- Skills that duplicate template content instead of referencing it

## References
- Keep long module registries, naming rules, and examples in linked files.
- Keep this skill short and focused on decision rules and workflow.

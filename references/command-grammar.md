# Command Grammar

The scaffold workflow uses a small explicit grammar. The skill routes these commands; the scripts do the deterministic work.

## Create

```bash
scaffold.py create <stack> <name> \
  [--registry PATH] \
  [--dest PATH] \
  [--package-prefix com.example] \
  [--bundle-prefix com.example] \
  [--auth-provider PROVIDER] \
  [--theme-preset PRESET] \
  [--room] [--github] [--ci] \
  [--no-auth] [--no-theme] \
  [--plan-out plan.json] \
  [--run-verify]
```

## Resolve

```bash
scaffold.py resolve <stack> <name> [same flags as create]
```

Outputs the resolved plan as JSON.

## Apply

```bash
scaffold.py apply --plan plan.json --dest PATH [--force] [--run-verify]
```

## Defaults

- `stack`: `kmp` or `nextjs`
- `package-prefix`: `com.example`
- `auth-provider`: registry stack default, else `clerk`
- `theme-preset`: registry stack default, else `neutral`
- auth/theme packs are included by default unless explicitly disabled

## Convention

Pack ids are derived from the stack name:
- `kmp_base`, `kmp_auth`, `kmp_ui_theme`, `kmp_room`, `kmp_github`, `kmp_ci`
- `nextjs_base`, `nextjs_auth`, `nextjs_ui_theme`, `nextjs_room`, `nextjs_github`, `nextjs_ci`

Registry entries should keep that naming pattern unless there is a strong reason not to.

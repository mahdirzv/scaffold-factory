#!/usr/bin/env python3
"""Deterministic scaffold resolver/applier for KMP and Next.js.

Usage examples:
  scaffold.py resolve --registry registry.json --stack kmp --name MyApp
  scaffold.py create --registry registry.json --stack kmp --name MyApp --dest ./MyApp
  scaffold.py apply --plan plan.json --dest ./MyApp --run-verify
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from fnmatch import fnmatchcase

KIND_ORDER = {"base": 0, "feature": 1, "infra": 2}
SKIP_DIRS = {
    ".git",
    ".gradle",
    ".idea",
    ".kotlin",
    ".next",
    ".run",
    ".sisyphus",
    ".swiftpm",
    "build",
    "coverage",
    "DerivedData",
    "dist",
    "node_modules",
    "xcuserdata",
}


def resolve_android_sdk() -> str | None:
    """Detect Android SDK path. Searches ANDROID_HOME, ANDROID_SDK_ROOT, then common locations."""
    # Environment variables first
    for env_var in ("ANDROID_HOME", "ANDROID_SDK_ROOT", "ANDROID_SDK"):
        sdk = os.environ.get(env_var)
        if sdk and Path(sdk).is_dir():
            return sdk

    # Common platform locations
    candidates = [
        Path.home() / "Library" / "Android" / "sdk",
        Path.home() / "Android" / "Sdk",
        Path("/usr/local/android-sdk"),
        Path("/opt/android-sdk"),
        Path("/usr/lib/android-sdk"),
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return str(candidate)

    return None


def resolve_source_path(raw_source: str, registry_base: Path) -> Path:
    """Resolve a source path to an absolute Path.

    Resolution order:
    1. Absolute paths are used as-is.
    2. Paths beginning with '$' are read from environment variables.
    3. Paths starting with 'templates/' are resolved relative to the skill base
       (assumes registry lives at <skill>/references/).
    4. All other relative paths are resolved relative to the registry base.
    """
    # Case 1: env-var reference
    if raw_source.startswith("$"):
        env_var = raw_source[1:]
        resolved = os.environ.get(env_var, "").strip()
        if not resolved:
            fail(f"source {raw_source!r} references env var ${env_var} which is not set")
        return Path(resolved).expanduser().resolve()

    # Case 2: absolute
    p = Path(raw_source)
    if p.is_absolute():
        return p.expanduser().resolve()

    # Case 3: skill-internal template (starts with templates/)
    if raw_source.startswith("templates/"):
        return (registry_base / raw_source).expanduser().resolve()

    # Case 4: relative to registry base
    return (registry_base / raw_source).expanduser().resolve()


def fail(message: str, code: int = 1) -> "NoReturn":
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug:
        fail(f"cannot slugify project name: {value!r}")
    return slug


def humanize(value: str) -> str:
    if re.search(r"[-_ ]", value):
        parts = [p for p in re.split(r"[-_ ]+", value.strip()) if p]
        return " ".join(part[:1].upper() + part[1:] for part in parts)
    return value.strip()


def compact_identifier(value: str) -> str:
    compact = re.sub(r"[^a-z0-9]+", "", value.lower())
    if not compact:
        fail(f"cannot build compact identifier from {value!r}")
    return compact


def load_registry(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            fail(f"YAML registry requires PyYAML: {exc}")
        data = yaml.safe_load(raw)
    else:
        data = json.loads(raw)

    if isinstance(data, list):
        data = {"packs": data}
    if not isinstance(data, dict):
        fail("registry must be a JSON/YAML object or a list of pack entries")
    data.setdefault("packs", [])
    data.setdefault("stack_defaults", {})
    return data


def validate_entry(entry: dict[str, Any]) -> None:
    required = ["id", "stack", "kind", "source"]
    missing = [field for field in required if field not in entry]
    if missing:
        fail(f"registry entry missing required fields: {missing} in {entry!r}")
    if entry["kind"] not in KIND_ORDER:
        fail(f"registry entry {entry['id']!r} has invalid kind {entry['kind']!r}")
    if not isinstance(entry.get("requires", []), list):
        fail(f"registry entry {entry['id']!r} requires must be a list")
    if not isinstance(entry.get("conflicts_with", []), list):
        fail(f"registry entry {entry['id']!r} conflicts_with must be a list")
    if not isinstance(entry.get("placeholder_map", {}), dict):
        fail(f"registry entry {entry['id']!r} placeholder_map must be a map")
    if not isinstance(entry.get("owns", []), list):
        fail(f"registry entry {entry['id']!r} owns must be a list")


def index_registry(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for entry in entries:
        validate_entry(entry)
        entry_id = entry["id"]
        if entry_id in indexed:
            fail(f"duplicate registry id: {entry_id}")
        indexed[entry_id] = entry
    return indexed


def stack_defaults(registry: dict[str, Any], stack: str) -> dict[str, Any]:
    defaults = registry.get("stack_defaults", {}).get(stack, {})
    if not isinstance(defaults, dict):
        fail(f"stack_defaults for {stack!r} must be a map")
    return dict(defaults)


def build_identifiers(stack: str, name: str, package_prefix: str, bundle_prefix: str | None) -> dict[str, str]:
    slug = slugify(name)
    display = humanize(name)
    compact = compact_identifier(slug)
    package_name = f"{package_prefix}.{compact}"
    package_path = package_name.replace(".", "/")
    bundle_id = f"{bundle_prefix or package_prefix}.{compact}"
    repo_name = slug
    return {
        "stack": stack,
        "stack_upper": stack.upper(),
        "project_name": display,
        "project_slug": slug,
        "package_name": package_name,
        "package_path": package_path,
        "bundle_id": bundle_id,
        "repo_name": repo_name,
        "folder_name": slug,
    }


def collect_selected_ids(args: argparse.Namespace) -> list[str]:
    base = [f"{args.stack}_base"]
    if not args.no_auth:
        base.append(f"{args.stack}_auth")
    if not args.no_theme:
        base.append(f"{args.stack}_ui_theme")
    if args.room:
        base.append(f"{args.stack}_room")
    if args.github:
        base.append(f"{args.stack}_github")
    if args.ci:
        base.append(f"{args.stack}_ci")
    base.extend(args.pack or [])
    deduped: list[str] = []
    seen: set[str] = set()
    for item in base:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def select_entries(indexed: dict[str, dict[str, Any]], stack: str, selected_ids: list[str]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    base_id = f"{stack}_base"
    if base_id not in indexed:
        fail(f"missing base entry: {base_id}")
    base = indexed[base_id]
    if base["stack"] != stack:
        fail(f"base entry {base_id} has mismatched stack {base['stack']!r}")

    selected: list[dict[str, Any]] = [base]
    for entry_id in selected_ids:
        if entry_id == base_id:
            continue
        if entry_id not in indexed:
            fail(f"unknown registry id: {entry_id}")
        entry = indexed[entry_id]
        if entry["stack"] != stack:
            fail(f"entry {entry_id} belongs to stack {entry['stack']!r}, expected {stack!r}")
        selected.append(entry)

    ordered = sorted(selected[1:], key=lambda e: (KIND_ORDER[e["kind"]], e["id"]))
    return base, ordered


def validate_dependencies(indexed: dict[str, dict[str, Any]], entries: list[dict[str, Any]]) -> None:
    selected_ids = {entry["id"] for entry in entries}
    for entry in entries:
        for dep in entry.get("requires", []):
            if dep not in selected_ids:
                fail(f"entry {entry['id']!r} requires {dep!r} but it was not selected")
        for conflict in entry.get("conflicts_with", []):
            if conflict in selected_ids:
                fail(f"entry {entry['id']!r} conflicts with {conflict!r}")


def merged_placeholders(registry: dict[str, Any], base: dict[str, Any], packs: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, str]:
    values: dict[str, str] = {}
    values.update(stack_defaults(registry, args.stack))
    values.update(base.get("placeholder_map", {}))
    for pack in packs:
        values.update(pack.get("placeholder_map", {}))
    values.update(build_identifiers(args.stack, args.name, args.package_prefix, args.bundle_prefix))
    values["auth_provider"] = args.auth_provider or values.get("auth_provider", "clerk")
    values["theme_preset"] = args.theme_preset or values.get("theme_preset", "neutral")
    values["package_prefix"] = args.package_prefix
    values["bundle_prefix"] = args.bundle_prefix or args.package_prefix
    values["stack"] = args.stack
    return {str(k): str(v) for k, v in values.items()}


def replacement_pairs(placeholders: dict[str, str]) -> list[tuple[str, str]]:
    pairs = {f"{{{{{key}}}}}": value for key, value in placeholders.items()}
    return sorted(pairs.items(), key=lambda item: len(item[0]), reverse=True)


def apply_replacements(text: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in pairs:
        text = text.replace(old, new)
    return text


def ignore_fn(_dir: str, names: list[str]) -> set[str]:
    return {name for name in names if name in SKIP_DIRS or name in {".DS_Store"}}


def matches_owned_path(relative_path: str, patterns: list[str]) -> bool:
    if not patterns or patterns in (["**/*"], ["*"]):
        return True
    for pattern in patterns:
        if fnmatchcase(relative_path, pattern):
            return True
    return False


def copy_entry_assets(src: Path, dest: Path, owns: list[str], pairs: list[tuple[str, str]]) -> None:
    if not src.exists():
        fail(f"source path does not exist: {src}")
    if src.is_file():
        target = dest / apply_replacements(src.name, pairs)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        return

    for path in src.rglob("*"):
        if any(part in SKIP_DIRS or part == ".DS_Store" for part in path.parts):
            continue
        if not path.is_file():
            continue
        relative = path.relative_to(src).as_posix()
        if not matches_owned_path(relative, owns):
            continue
        target = dest / apply_replacements(relative, pairs)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def copy_source_tree(src: Path, dest: Path) -> None:
    if not src.exists():
        fail(f"source path does not exist: {src}")
    if src.is_file():
        fail(f"source path must be a directory: {src}")
    shutil.copytree(src, dest, dirs_exist_ok=True, ignore=ignore_fn)


def rewrite_tree(dest: Path, pairs: list[tuple[str, str]]) -> tuple[int, int]:
    changed_files = 0

    for path in sorted(dest.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_file():
            try:
                original = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            rewritten = apply_replacements(original, pairs)
            if rewritten != original:
                path.write_text(rewritten, encoding="utf-8")
                changed_files += 1

    return changed_files, 0


def gather_steps(entries: list[dict[str, Any]], key: str) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for entry in entries:
        for step in entry.get(key, []):
            if step not in seen:
                ordered.append(step)
                seen.add(step)
    return ordered


def run_commands(commands: list[str], cwd: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for command in commands:
        print(f"$ {command}")
        proc = subprocess.run(command, cwd=cwd, shell=True, text=True, capture_output=True)
        if proc.stdout:
            print(proc.stdout, end="")
        if proc.stderr:
            print(proc.stderr, end="", file=sys.stderr)
        results.append({"command": command, "returncode": proc.returncode})
        if proc.returncode != 0:
            fail(f"verification command failed: {command}")
    return results


def resolve_plan(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_registry(Path(args.registry))
    indexed = index_registry(registry["packs"])
    selected_ids = collect_selected_ids(args)
    base, packs = select_entries(indexed, args.stack, selected_ids)
    validate_dependencies(indexed, [base] + packs)
    placeholders = merged_placeholders(registry, base, packs, args)
    verify = gather_steps([base] + packs, "verify")
    post_steps = gather_steps([base] + packs, "post_steps")
    plan = {
        "stack": args.stack,
        "name": args.name,
        "destination": str(Path(args.dest).expanduser()) if args.dest else None,
        "base": base,
        "packs": packs,
        "placeholder_map": placeholders,
        "verify": verify,
        "post_steps": post_steps,
        "selected_ids": [base["id"], *[entry["id"] for entry in packs]],
        # Used by apply_plan to resolve relative source paths
        "_registry_path": str(Path(args.registry).expanduser().resolve()),
    }
    return plan


def emit_plan(plan: dict[str, Any], json_only: bool = False) -> None:
    payload = json.dumps(plan, indent=2, sort_keys=True)
    if json_only:
        print(payload)
        return
    print(payload)


def apply_plan(plan: dict[str, Any], dest: Path, force: bool = False, run_verify: bool = False) -> dict[str, Any]:
    dest = dest.expanduser()
    if dest.exists() and any(dest.iterdir()) and not force:
        fail(f"destination already exists and is not empty: {dest}")
    dest.mkdir(parents=True, exist_ok=True)

    # Resolve source paths relative to the registry's skill base
    registry_base = Path(plan["_registry_path"]).resolve().parent
    if registry_base.name == "references":
        registry_base = registry_base.parent

    entries = [plan["base"], *plan.get("packs", [])]
    copied = 0
    pairs = replacement_pairs(plan["placeholder_map"])
    for entry in entries:
        source = resolve_source_path(entry["source"], registry_base)
        copy_entry_assets(source, dest, list(entry.get("owns", [])), pairs)
        copied += 1

    changed_files, renamed_paths = rewrite_tree(dest, pairs)

    # Inject local.properties for KMP stacks using auto-detected SDK path
    if plan["stack"] == "kmp":
        sdk_path = resolve_android_sdk()
        if sdk_path:
            lp_path = dest / "local.properties"
            # Only write if not present, so CI-generated files take precedence
            if not lp_path.exists():
                lp_path.write_text(f"sdk.dir={sdk_path}\n", encoding="utf-8")
                print(f"[scaffold] wrote local.properties with sdk.dir={sdk_path}")
            else:
                print(f"[scaffold] local.properties already exists, not overwriting")

    verify_results: list[dict[str, Any]] = []
    if run_verify:
        verify_results = run_commands(plan.get("verify", []), cwd=dest)

    return {
        "destination": str(dest),
        "copied_entries": copied,
        "changed_files": changed_files,
        "renamed_paths": renamed_paths,
        "verify_results": verify_results,
    }


def add_common_scaffold_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("stack", choices=["kmp", "nextjs"])
    parser.add_argument("name")
    parser.add_argument("--registry", default="registry.json")
    parser.add_argument("--package-prefix", default="com.example")
    parser.add_argument("--bundle-prefix")
    parser.add_argument("--auth-provider")
    parser.add_argument("--theme-preset")
    parser.add_argument("--room", action="store_true")
    parser.add_argument("--github", action="store_true")
    parser.add_argument("--ci", action="store_true")
    parser.add_argument("--no-auth", action="store_true")
    parser.add_argument("--no-theme", action="store_true")
    parser.add_argument("--pack", action="append", default=[])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic scaffold resolver/applier")
    sub = parser.add_subparsers(dest="command", required=True)

    resolve = sub.add_parser("resolve", help="Resolve a scaffold plan and print JSON")
    add_common_scaffold_args(resolve)
    resolve.add_argument("--dest")

    apply = sub.add_parser("apply", help="Apply a saved plan JSON to a destination")
    apply.add_argument("--plan", required=True, help="Path to a plan JSON file or '-' for stdin")
    apply.add_argument("--dest", required=True)
    apply.add_argument("--force", action="store_true")
    apply.add_argument("--run-verify", action="store_true")

    create = sub.add_parser("create", help="Resolve and apply in one pass")
    add_common_scaffold_args(create)
    create.add_argument("--dest", required=True)
    create.add_argument("--force", action="store_true")
    create.add_argument("--run-verify", action="store_true")
    create.add_argument("--plan-out", help="Optional path to write the resolved plan JSON")

    return parser


def load_plan(path: str) -> dict[str, Any]:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    args = build_parser().parse_args()

    if args.command == "resolve":
        plan = resolve_plan(args)
        emit_plan(plan, json_only=True)
        return 0

    if args.command == "apply":
        plan = load_plan(args.plan)
        result = apply_plan(plan, Path(args.dest), force=args.force, run_verify=args.run_verify)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if args.command == "create":
        plan = resolve_plan(args)
        if args.plan_out:
            Path(args.plan_out).expanduser().write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")
        result = apply_plan(plan, Path(args.dest), force=args.force, run_verify=args.run_verify)
        print(json.dumps({"plan": plan, "result": result}, indent=2, sort_keys=True))
        return 0

    fail(f"unsupported command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, json, subprocess, argparse

OLD_PREFIX = "plasma_welcome_settings"
NEW_PREFIX = "kiss"
LOG_FILE = "rename_kiss_log.csv"

# Default directory = project root / needles
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../needles")

def is_json_file(p):
    return p.lower().endswith(".json")

def starts_with_old_prefix(name):
    return name.startswith(OLD_PREFIX)

def build_new_name(name):
    return NEW_PREFIX + name[len(OLD_PREFIX):]

def safe_target_path(dst):
    # Avoid overwriting existing files, add _conflictN if needed
    if not os.path.exists(dst):
        return dst
    base, ext = os.path.splitext(dst)
    n = 1
    while True:
        candidate = f"{base}_conflict{n}{ext}"
        if not os.path.exists(candidate):
            return candidate
        n += 1

def rename_file(src, dst, use_git, dry_run):
    if dry_run:
        print(f"[DRY-RUN] rename: {src} -> {dst}")
        return True
    if use_git:
        try:
            subprocess.run(["git", "mv", src, dst], check=True)
            return True
        except subprocess.CalledProcessError:
            os.rename(src, dst)
            return True
    else:
        os.rename(src, dst)
        return True

def rewrite_json_tags(path, dry_run):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[WARN] skip {path} (parse error: {e})")
        return False

    changed = False
    if isinstance(data.get("tags"), list):
        new_tags = []
        for t in data["tags"]:
            if isinstance(t, str) and t.startswith(OLD_PREFIX):
                new_tags.append(NEW_PREFIX + t[len(OLD_PREFIX):])
                changed = True
            else:
                new_tags.append(t)
        if changed:
            data["tags"] = new_tags

    if changed:
        if dry_run:
            print(f"[DRY-RUN] rewrite tags in {path}")
            return True
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        return True
    return False

def append_log(rows):
    if not rows:
        return
    header_needed = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        if header_needed:
            f.write("old_path,new_path,content_changed\n")
        for old_p, new_p, changed in rows:
            f.write(f"{old_p},{new_p},{changed}\n")

def process_dir(root, use_git, dry_run):
    rows_for_log = []
    for name in sorted(os.listdir(root)):
        src = os.path.join(root, name)
        if not os.path.isfile(src):
            continue
        if starts_with_old_prefix(name):
            new_name = build_new_name(name)
            target = safe_target_path(os.path.join(root, new_name))
            rename_file(src, target, use_git, dry_run)

            content_changed = False
            if is_json_file(target):
                content_changed = rewrite_json_tags(target, dry_run)
            rows_for_log.append((src, target, content_changed))
    append_log(rows_for_log)

def main():
    parser = argparse.ArgumentParser(description="Rename plasma_welcome_settings* -> kiss* and update JSON tags (in ./needles).")
    parser.add_argument("--git", action="store_true", help="Use git mv to rename")
    parser.add_argument("--dry-run", action="store_true", help="Print actions only")
    args = parser.parse_args()

    if not os.path.isdir(ROOT):
        print(f"[ERROR] needles directory not found: {ROOT}")
        sys.exit(1)

    print(f"[INFO] Scanning directory: {ROOT}")
    process_dir(ROOT, args.git, args.dry_run)
    print(f"[INFO] Done. Log file: {LOG_FILE}")

if __name__ == "__main__":
    main()

import os
import re
import time
from pathlib import Path
import pgembed

print("Starting embedded PostgreSQL...")
pg_server = pgembed.get_server("local_pg_data")
db_uri = pg_server.get_uri()

# 1. Dynamically locate the repository root
script_dir = Path(__file__).resolve().parent
repo_root = script_dir.parent  # Assumes script is in /scripts/ or root

# Define the list of relative paths to the env files you want to update
target_env_files = [
    "backend/.env",
    ".env",
    # "frontend/.env.local", # Uncomment or add others as needed
]

print(f"Database running on: {db_uri}")
print("─" * 60)

# Process each file in the list
for rel_path in target_env_files:
    target_file = repo_root / rel_path
    # Look for an example file in the same directory as the target
    env_example = target_file.parent / ".env.example"

    print(f"Processing: {target_file}")

    # 2. If the target file does not exist, copy from .env.example or create a new one
    if not target_file.exists():
        if env_example.exists():
            print(f"  Creating {target_file.name} from {env_example.name}...")
            content = env_example.read_text(encoding="utf-8")
        else:
            print(f"  {target_file.name} not found. Creating a new one...")
            content = ""
    else:
        content = target_file.read_text(encoding="utf-8")

    # 3. Update or Append DATABASE_URL (handles spaces like DATABASE_URL = ...)
    pattern = r"^\s*DATABASE_URL\s*=.*$"
    replacement = f"DATABASE_URL={db_uri}"

    if re.search(pattern, content, flags=re.MULTILINE):
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    else:
        new_content = content.rstrip() + f"\n{replacement}\n"

    # 4. Write and force flush to disk
    target_file.write_text(new_content, encoding="utf-8")

    # 5. Verification check
    read_back = target_file.read_text(encoding="utf-8")
    matching_lines = [
        line for line in read_back.splitlines() if "DATABASE_URL" in line
    ]

    print(f"  Verified line in {target_file.name}:")
    for line in matching_lines:
        print(f"    -> {line}")
    print("─" * 60)

print("Press Ctrl+C to shut down.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down PostgreSQL...")
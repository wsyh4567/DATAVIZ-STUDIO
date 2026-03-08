import subprocess

result = subprocess.run(
    ["python", "app.py"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)

print("--- STDOUT ---")
print(result.stdout)
print("--- STDERR ---")
print(result.stderr)

import os

total = 0
for root, dirs, files in os.walk('.'):
    for f in files:
        try:
            total += os.path.getsize(os.path.join(root, f))
        except Exception:
            pass

mb = total / 1024 / 1024
gb = total / 1024 / 1024 / 1024
print(f"Bytes: {total}")
print(f"MB: {mb:.2f}")
print(f"GB: {gb:.4f}")

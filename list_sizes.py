import os
from collections import defaultdict

files = []
for root, dirs, filenames in os.walk('.'):
    for f in filenames:
        try:
            p = os.path.join(root, f)
            s = os.path.getsize(p)
            files.append((s, p))
        except Exception:
            pass

files.sort(reverse=True)
print('Top 40 files:')
for s, p in files[:40]:
    print(f"{s:>12}  {s/1024/1024:8.2f} MB  {p}")

# directory sizes
dir_sizes = defaultdict(int)
for s, p in files:
    d = os.path.dirname(p)
    while d.startswith('.'):
        dir_sizes[d] += s
        if d == '.' or d == '' or d == '\\':
            break
        d = os.path.dirname(d)

print('\nTop directories:')
for d, s in sorted(dir_sizes.items(), key=lambda x: x[1], reverse=True)[:40]:
    print(f"{s:>12}  {s/1024/1024:8.2f} MB  {d}")

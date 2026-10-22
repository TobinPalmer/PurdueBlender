import json
from pathlib import Path

manifest = json.loads(Path('renders/renders_manifest.json').read_text())
print(f"Total rendered buildings in manifest: {len(manifest)}")
for k, v in manifest.items():
    file_path = Path(v['file'])
    exists = file_path.exists()
    size_kb = file_path.stat().st_size // 1024 if exists else 0
    cam = v.get('camera', 'Hero')
    print(f"{k:<26} | Exists: {str(exists):<5} | Size: {size_kb:>5} KB | Camera: {cam}")

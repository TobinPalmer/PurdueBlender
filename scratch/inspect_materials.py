import json, os
from pathlib import Path

queue_file = Path('materials/review/detailed_queue.json')
queue = json.loads(queue_file.read_text())
print(f"Total in detailed_queue: {len(queue)}")
for item in queue:
    b_path = Path('modular') / item['file']
    print(f"{item['id']}: exists={b_path.exists()} size={b_path.stat().st_size if b_path.exists() else 0}")

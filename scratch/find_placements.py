import bpy, json
from pathlib import Path

placements = {}
for o in bpy.data.objects:
    if o.name.startswith('Placement_'):
        placements[o.name] = {
            'location': list(o.location),
            'rotation': list(o.rotation_euler),
            'scale': list(o.scale)
        }

print(f"Total placements found: {len(placements)}")
Path('scratch/placements.json').write_text(json.dumps(placements, indent=2))

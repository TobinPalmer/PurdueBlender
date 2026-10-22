import bpy
import json
from pathlib import Path
from collections import Counter

scene = bpy.context.scene
libraries = []
for library in bpy.data.libraries:
    path = Path(bpy.path.abspath(library.filepath)).resolve()
    libraries.append((library.filepath, path.exists()))
markers = [o for o in scene.objects if o.name.startswith("Placement_")]
result = {
    "scene": scene.name,
    "scene_objects": len(scene.objects),
    "library_count": len(libraries),
    "missing_libraries": [p for p, exists in libraries if not exists],
    "placement_markers": len(markers),
    "marker_sample": [{"name": m.name, "type": m.instance_type,
                       "collection": m.instance_collection.name if m.instance_collection else None,
                       "visible": m.visible_get(), "hide_viewport": m.hide_viewport,
                       "hide_render": m.hide_render,
                       "library": m.instance_collection.library.filepath if m.instance_collection and m.instance_collection.library else None}
                      for m in markers[:3]],
}
print(json.dumps(result))

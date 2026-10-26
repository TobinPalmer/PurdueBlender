import bpy
import mathutils

blend_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"

candidates = [
    "Mathematical Sciences Building (MATH)",
    "R. B. Wetherill Laboratory of Chemistry (WTHR)",
    "Grissom Hall",
    "Haas (Felix) Hall (HAAS)",
    "Rawls Hall",
    "Brown Laboratory of Chemistry (BRWN)",
    "Union Club Hotel",
    "Student Health Center (PUSH)",
    "Schleman Hall (SCHM)",
    "Knoy Hall (KNOY)"
]

massing_col = bpy.data.collections.get("02_Campus_Buildings_Massing")

for name in candidates:
    obj = bpy.data.objects.get(name)
    if obj:
        # compute world bounding box
        bbox_corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
        min_x = min(c.x for c in bbox_corners)
        max_x = max(c.x for c in bbox_corners)
        min_y = min(c.y for c in bbox_corners)
        max_y = max(c.y for c in bbox_corners)
        min_z = min(c.z for c in bbox_corners)
        max_z = max(c.z for c in bbox_corners)
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        center_z = (min_z + max_z) / 2
        dim_x = max_x - min_x
        dim_y = max_y - min_y
        dim_z = max_z - min_z
        print(f"[{name}]")
        print(f"  Center: ({center_x:.2f}, {center_y:.2f}, {center_z:.2f})")
        print(f"  Bounds X: [{min_x:.2f}, {max_x:.2f}] (width: {dim_x:.2f}m)")
        print(f"  Bounds Y: [{min_y:.2f}, {max_y:.2f}] (length: {dim_y:.2f}m)")
        print(f"  Bounds Z: [{min_z:.2f}, {max_z:.2f}] (height: {dim_z:.2f}m)")
        print(f"  Mesh vertices: {len(obj.data.vertices)}")
        print()

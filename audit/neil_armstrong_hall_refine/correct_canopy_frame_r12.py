import bpy, hashlib, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET=ROOT/"modular/buildings/neil_armstrong_hall.blend"
AUDIT=ROOT/"audit/neil_armstrong_hall_refine"
EXPECTED="c339f8509d65073b0f9badec0125af794b41ef9cc83f25bd3457827e22524b65"
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
if sha(ASSET)!=EXPECTED: raise RuntimeError("Asset changed after R12 canopy save")
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
obj=bpy.data.objects["ARMS_Cantilever_Canopy_Deck"]
if len(obj.data.vertices)!=368: raise RuntimeError("Unexpected R12 canopy mesh; expected 8 original + 360 canopy vertices")
inv=obj.matrix_world.inverted()
# First eight vertices are the original local-space entry canopy. Newly added
# canopy coordinates were authored in the asset frame; convert only those to
# the mesh object's local coordinates under its preserved parent transform.
for v in list(obj.data.vertices)[8:]:
    world=Vector(v.co)
    v.co=inv@world
obj.data.update()
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
newsha=sha(ASSET)

evpath=AUDIT/"evidence_r12.json"
ev=json.loads(evpath.read_text(encoding="utf-8"))
ev["sha256_after"]=newsha
ev["coordinate_frame_correction"]={
 "applied":"New canopy vertices converted from building asset coordinates into the existing mesh object local frame using matrix_world.inverted(); original lower canopy vertices and its parent transform were preserved.",
 "object_matrix_world_before_correction":[[round(float(x),9) for x in row] for row in obj.matrix_world],
 "validation":"Reopen validation records final world-space bounds and confirms planned ortho coordinates."
}
pts=[obj.matrix_world@v.co for v in obj.data.vertices]
ev["new_geometry"]["mesh_bounds"]={"min":[round(min(p[i] for p in pts),3) for i in range(3)],"max":[round(max(p[i] for p in pts),3) for i in range(3)],"verts":len(obj.data.vertices),"polygons":len(obj.data.polygons)}
ev["validation_pending"]="Reopen the saved asset, verify the final world-space geometry bounds and collection inventory, then render source-matched sides and roof."
evpath.write_text(json.dumps(ev,indent=2),encoding="utf-8")
print(json.dumps({"sha256":newsha,"matrix_world":[[round(float(x),9) for x in row] for row in obj.matrix_world],"bounds":ev["new_geometry"]["mesh_bounds"]},indent=2))

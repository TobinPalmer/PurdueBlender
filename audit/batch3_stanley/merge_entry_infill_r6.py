"""Join the entry masonry infills into the facade mesh for matched brick scale."""
import bpy,bmesh,hashlib,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/stanley_coulter_hall.blend';AUDIT=ROOT/'audit/batch3_stanley'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
wall=bpy.data.objects['SC_Brick_Masonry_Exterior_Walls']
asset=bpy.data.collections['Asset_stanley_coulter_hall']
if wall.data.materials[0].name!='Purdue_Red_Brick_Procedural':raise RuntimeError('Brick facade material mismatch')
panels=[bpy.data.objects[n] for n in ('SC_R6_Entry_Brick_Infill_Left','SC_R6_Entry_Brick_Infill_Right')]
bm=bmesh.new();bm.from_mesh(wall.data);inv=wall.matrix_world.inverted()
newfaces=0;added=[]
for panel in panels:
    world=[panel.matrix_world@v.co for v in panel.data.vertices]
    # Panel mesh ordering is the two faces and four sides from the source infill.
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    vmap=[bm.verts.new(inv@p) for p in world]
    for face_ids in faces:
        try:f=bm.faces.new([vmap[i] for i in face_ids])
        except ValueError:continue
        f.material_index=0;newfaces+=1
    added.append({'name':panel.name,'world_bounds':[[min(p[i] for p in world) for i in range(3)],[max(p[i] for p in world) for i in range(3)]]})
    bpy.data.objects.remove(panel,do_unlink=True)
bm.to_mesh(wall.data);wall.data.update();bm.free()
wall['R6_entry_infill']='Two brick piers flanking the modeled stone main portal close unmodeled view-through gaps. Faces are part of the shared exterior brick mesh so its world-scaled procedural texture matches.'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
result={'asset':str(ASSET),'sha256':sha,'wall_object':'SC_Brick_Masonry_Exterior_Walls','new_facade_faces':newfaces,'joined_panels':added,'new_object_count':0,'wall_material':'Purdue_Red_Brick_Procedural','note':'Brick infill polygons are now part of the original full-building brick mesh; generated-coordinate shader scale remains consistent with the facade.'}
(AUDIT/'entry_infill_r6.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

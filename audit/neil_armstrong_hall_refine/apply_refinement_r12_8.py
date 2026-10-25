"""R12.8 evidence-led cleanup/refinement for Neil Armstrong Hall only."""
import bpy, hashlib, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/neil_armstrong_hall.blend'
EXPECTED='a85ef78d82e5c50b09fcd4fb7bc191798fad0132a9a89b84297203186f2ae549'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(ASSET)!=EXPECTED: raise RuntimeError('Asset changed since R12.7; refusing to overwrite: '+sha(ASSET))
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections['Asset_neil_armstrong_hall']
deck=bpy.data.objects['ARMS_Cantilever_Canopy_Deck']
if len(col.objects)!=445 or len(deck.data.vertices)!=379 or len(deck.data.polygons)!=363:
    raise RuntimeError('Unexpected R12.7 inventory; refusing geometry rewrite')

# R12.5 appended the original low entrance deck to a mesh that already kept
# the same six box faces. Identify and remove only exact world-space duplicate
# faces; retain the first copy and then discard its now-loose duplicate verts.
src=deck.data
world_coords=[deck.matrix_world@v.co for v in src.vertices]
face_keys={}
keep=[]; duplicate_faces=[]
for p in src.polygons:
    key=tuple(sorted(tuple(round(float(c),5) for c in world_coords[i]) for i in p.vertices))
    if key in face_keys:
        duplicate_faces.append(p.index)
    else:
        face_keys[key]=p.index
        keep.append((tuple(p.vertices),int(p.material_index)))
duplicate_low=0; duplicate_shell=0
for i in duplicate_faces:
    p=src.polygons[i]
    if p.material_index==0: duplicate_low+=1
    elif p.material_index==1: duplicate_shell+=1
if len(duplicate_faces)!=21 or len(keep)!=342 or duplicate_low!=6 or duplicate_shell!=15:
    raise RuntimeError(f'Unexpected duplicated faces: total={len(duplicate_faces)}, low={duplicate_low}, shell={duplicate_shell}')
used=sorted({i for face,_ in keep for i in face})
remap={old:new for new,old in enumerate(used)}
verts=[tuple(src.vertices[i].co) for i in used]
faces=[(tuple(remap[i] for i in f),mi) for f,mi in keep]
mesh=bpy.data.meshes.new('ARMS_R12_8_Canopy_Mesh')
for m in src.materials: mesh.materials.append(m)
mesh.from_pydata(verts,[],[f for f,_ in faces]); mesh.update(calc_edges=True)
for p,(_,mi) in zip(mesh.polygons,faces): p.material_index=mi
oldmesh=deck.data; deck.data=mesh

# Thin the inferred high wing shell from 0.30 m to 0.18 m. The orthophoto
# perimeter/inner traces stay in the exact same XY locations; only the underside
# offset changes. The first 8 verts are the retained lobby deck; R12 roof grid
# is next (360 alternating upper/lower vertices), then the 3-point dark notch.
if len(mesh.vertices)!=371 or len(mesh.polygons)!=342: raise RuntimeError(f'Unexpected post-dedup mesh inventory: {len(mesh.vertices)} verts / {len(mesh.polygons)} faces')
inv=deck.matrix_world.inverted()
for i in range(9,368,2):
    top=deck.matrix_world@mesh.vertices[i-1].co
    bottom=deck.matrix_world@mesh.vertices[i].co
    bottom.z=top.z-0.18
    mesh.vertices[i].co=inv@bottom
mesh.update()

# The original shared blue-gray Sea Wolf ACM made the photographed red-metal
# roof soffit render charcoal. Use a dedicated muted red-brown finish only for
# the high canopy's downward-facing shell. Preserve the lobby deck material and
# the small dark photographic notch.
soffit=bpy.data.materials.get('ARMS_R12_8_Wing_Soffit_ACM') or bpy.data.materials.new('ARMS_R12_8_Wing_Soffit_ACM')
soffit.use_nodes=True
bsdf=next(n for n in soffit.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bsdf.inputs['Base Color'].default_value=(0.115,0.030,0.018,1.0)
bsdf.inputs['Metallic'].default_value=0.14
bsdf.inputs['Roughness'].default_value=0.48
soffit.diffuse_color=(0.115,0.030,0.018,1.0)
if soffit.name not in [m.name for m in mesh.materials]: mesh.materials.append(soffit)
soffit_i=list(mesh.materials).index(soffit)
counts={'soffit_faces':0,'low_deck_faces_preserved':0}
for p in mesh.polygons:
    pts=[deck.matrix_world@mesh.vertices[i].co for i in p.vertices]
    cz=sum(v.z for v in pts)/len(pts)
    if p.material_index==0 and cz>10.0:
        p.material_index=soffit_i; counts['soffit_faces']+=1
    elif p.material_index==0:
        counts['low_deck_faces_preserved']+=1
if counts['soffit_faces']<100 or counts['low_deck_faces_preserved']!=6:
    raise RuntimeError('Unexpected material assignment counts: '+json.dumps(counts))

deck['R12_8_duplicate_cleanup']='Removed six exact duplicate faces from the low entrance canopy appended in R12.5 and 15 exact overlapping duplicate roof-shell faces at segment seams; retained one copy of each surface.'
deck['R12_8_canopy_profile']='Orthophoto-traced roof/eaves XY preserved. Inferred shell thickness reduced from 0.30 m to 0.18 m to better match the photographed thin folded ACM edge; this is visual inference, not measured construction data.'
deck['R12_8_soffit_finish']='Dedicated muted red-brown ACM assigned to high canopy underside only, matching the red ACM visible in 2016 source photographs. Lobby entrance deck remains on its original material.'

bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({'revision':'R12.8','asset':str(ASSET),'sha256':sha(ASSET),'objects':len(col.objects),'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'duplicate_faces_removed':len(duplicate_faces),'duplicate_classes':{'entrance_deck':duplicate_low,'roof_shell_seams':duplicate_shell},'vertex_count_after_dedup':len(used),'material_counts':counts,'material_slots':[m.name if m else None for m in mesh.materials],'canopy_bounds_m':{'min':[round(min((deck.matrix_world@v.co)[i] for v in mesh.vertices),3) for i in range(3)],'max':[round(max((deck.matrix_world@v.co)[i] for v in mesh.vertices),3) for i in range(3)]}},indent=2))

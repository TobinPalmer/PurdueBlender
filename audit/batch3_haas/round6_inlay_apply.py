import bpy, json
from pathlib import Path
f=bpy.data.filepath
c=bpy.data.collections['Asset_felix_haas_hall']
# Remove prior round-six details so the script is safe to rerun.
for o in list(c.objects):
    if o.name.startswith('HAAS_R6_'):
        bpy.data.objects.remove(o, do_unlink=True)
# A warm, low-gloss Bedford limestone field. Preserve the existing shared detail material.
stone=bpy.data.materials.get('HAAS_Photo_Limestone')
if stone:
    stone.diffuse_color=(0.73,0.61,0.45,1)
    for n in stone.node_tree.nodes:
        if n.type=='BSDF_PRINCIPLED':
            n.inputs['Base Color'].default_value=(0.73,0.61,0.45,1)
            n.inputs['Roughness'].default_value=0.82
# The large entrance face is the limestone field; source-visible brick is placed as inlaid panel rings.
face=bpy.data.objects['HAAS_Photo_Entrance_Limestone_Facade']
face.data.materials.clear(); face.data.materials.append(stone)
face['round6_material_note']='Warm Bedford limestone field based on the Purdue exterior photograph; detailed extents inferred from perspective.'
# Build a restrained red brick inlay material from the established Purdue brick shader.
base=bpy.data.materials.get('Purdue_Red_Brick.001')
brick=base.copy(); brick.name='HAAS_R6_Red_Brick_Inlay'
brick.diffuse_color=(0.24,0.047,0.018,1)
for n in brick.node_tree.nodes:
    if n.type=='TEX_BRICK':
        n.inputs['Color1'].default_value=(0.25,0.055,0.022,1)
        n.inputs['Color2'].default_value=(0.17,0.028,0.010,1)
        n.inputs['Mortar'].default_value=(0.12,0.035,0.018,1)
# Each ring is built as four brick panels, leaving a clear central opening. Rings remain flush to the facade.
verts=[]; faces=[]
def rect(y0,y1,z0,z1,x=13.024):
    i=len(verts)
    verts.extend([(x,y0,z0),(x,y1,z0),(x,y1,z1),(x,y0,z1)])
    faces.append((i,i+1,i+2,i+3))
def ring(cy, inner_w, outer_w, zi0, zi1, zo0, zo1):
    ilo,ihi=cy-inner_w/2,cy+inner_w/2
    olo,ohi=cy-outer_w/2,cy+outer_w/2
    rect(olo,ilo,zi0,zi1)
    rect(ihi,ohi,zi0,zi1)
    rect(ilo,ihi,zo0,zi0)
    rect(ilo,ihi,zi1,zo1)
# Lower arched side openings: brick backing/rings sit behind the stone arch and jambs.
for cy in (-7.65,7.65):
    ring(cy,2.70,4.05,1.52,4.50,1.02,5.18)
# Three upper-level window groupings: two side bays and the central window above the entrance.
for cy,iw,ow in [(-7.65,3.20,4.25),(0.0,3.56,4.55),(7.65,3.20,4.25)]:
    ring(cy,iw,ow,6.78,8.62,6.30,9.10)
mesh=bpy.data.meshes.new('HAAS_R6_FacadeInlayMesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(brick); mesh.update()
o=bpy.data.objects.new('HAAS_R6_EastFacade_Inlaid_Brick_Rings',mesh); c.objects.link(o)
o['evidence_basis']='Purdue exterior reference: pale limestone field with red-brick inlay around openings. Panel widths/locations are approximate from perspective; no measured elevation is available.'
o['source_url']='https://events.purdue.edu/felix_haas_hall'
o['round6_count']=20
# Keep a compact machine-readable change record adjacent to the model.
bpy.ops.wm.save_as_mainfile(filepath=f)
Path('audit/batch3_haas/round6_changes.json').write_text(json.dumps({'façade':'Changed entrance field from red-brown brick to warm Bedford limestone and added five inlaid red-brick border rings around the two lower arched side openings and three upper windows. The stone/brick pattern is photo-supported; panel dimensions are perspective estimates.','GIS':'Preserved shell, source origin, and placement.','interior':'Interior geometry remains schematic; round-six plan render will use softer fill lighting and preserve explicit plan-versus-estimate legend.','new_mesh_faces':len(faces),'export_objects':len(c.objects),'limitations':'No measured elevations or metric interior plan are available; window openings and room dimensions remain estimates.'},indent=2),encoding='utf-8')
print('R6_DONE',len(c.objects),len(faces),f)

import bpy, json
from pathlib import Path
c=bpy.data.collections['Asset_felix_haas_hall']
archive=bpy.data.collections.get('Reference_Incompatible_Geometry_felix_haas_hall')
# Remove the round-six detached inlay mesh; rebuild the pattern flush with the GIS east facade.
for name in ['HAAS_R6_EastFacade_Inlaid_Brick_Rings','HAAS_R7_EastFacade_Inlaid_Brickwork']:
    o=bpy.data.objects.get(name)
    if o:bpy.data.objects.remove(o,do_unlink=True)
# Transfer the large photo facade skin to the hidden reference archive. The GIS wall itself gets the facade material.
skin=bpy.data.objects.get('HAAS_Photo_Entrance_Limestone_Facade')
if skin and archive:
    for col in list(skin.users_collection):col.objects.unlink(skin)
    archive.objects.link(skin);skin.name='HAAS_R6_Entrance_Facade_Skin_ARCHIVE'
# Warm neutral stone color based on qualitative Purdue photo; all dimensions remain source/estimate bounded.
stone=bpy.data.materials.get('HAAS_Photo_Limestone')
if stone:
    stone.diffuse_color=(0.86,0.77,0.62,1)
    for n in stone.node_tree.nodes:
        if n.type=='BSDF_PRINCIPLED':
            n.inputs['Base Color'].default_value=(0.86,0.77,0.62,1)
            n.inputs['Roughness'].default_value=0.86
# Reassign only outward-facing polygons of the east GIS wall. Shell geometry and bounds are untouched.
wall=bpy.data.objects['HAAS_Brick_Wall_East']
stone_idx=next(i for i,m in enumerate(wall.data.materials) if m and m.name=='HAAS_Photo_Limestone')
face_count=0
for p in wall.data.polygons:
    n=wall.matrix_world.to_3x3()@p.normal; center=wall.matrix_world@p.center
    if n.x>0.95 and -12.0<=center.y<=12.8 and center.z>=0.35:
        p.material_index=stone_idx;face_count+=1
wall['east_front_masonry']='Outward east wall GIS faces are limestone; brick inlay rings sit 6 mm proud of the shell face.'
# Suppress the overly projecting stone grid and move its bases closer to the GIS shell.
for o in list(c.objects):
    nm=o.name
    if nm.startswith('HAAS_Photo_Pier_') or nm.startswith('HAAS_Photo_Capital_'):
        o.scale.x*=0.55;o.location.x-=0.075
    elif nm.startswith('HAAS_Photo_Band_'):
        o.scale.x*=0.60;o.location.x-=0.05
    elif nm.startswith('HAAS_Photo_LintelSill') or nm.startswith('HAAS_Photo_ArchedTrim') or nm=='HAAS_Photo_Main_Entry_Arch':
        o.scale.x*=0.62;o.location.x-=0.04
# A warmer red brick shader with visible coursing; leave other campus brick materials unchanged.
brick=bpy.data.materials.get('HAAS_R6_Red_Brick_Inlay')
if brick:
    brick.diffuse_color=(0.36,0.075,0.03,1)
    for n in brick.node_tree.nodes:
        if n.type=='TEX_BRICK':
            n.inputs['Color1'].default_value=(0.42,0.095,0.038,1)
            n.inputs['Color2'].default_value=(0.29,0.055,0.018,1)
            n.inputs['Mortar'].default_value=(0.17,0.05,0.025,1)
# Rebuild repeated inlay rings around the two arched windows, three upper windows, and main portal.
verts=[];faces=[]
def rect(y0,y1,z0,z1,x=12.987):
    i=len(verts);verts.extend([(x,y0,z0),(x,y1,z0),(x,y1,z1),(x,y0,z1)]);faces.append((i,i+1,i+2,i+3))
def ring(cy,inner_w,outer_w,zi0,zi1,zo0,zo1):
    il,ir=cy-inner_w/2,cy+inner_w/2;ol,orr=cy-outer_w/2,cy+outer_w/2
    rect(ol,il,zi0,zi1);rect(ir,orr,zi0,zi1);rect(il,ir,zo0,zi0);rect(il,ir,zi1,zo1)
for cy in (-7.65,7.65):ring(cy,2.70,4.30,1.52,4.50,1.00,5.18)
for cy,iw,ow in [(-7.65,3.20,4.45),(0.0,3.56,4.65),(7.65,3.20,4.45)]:ring(cy,iw,ow,6.78,8.62,6.30,9.10)
# Main door surround, with stone arch details in front of the brick inset.
ring(0.0,2.35,3.85,1.45,4.95,0.95,5.42)
# Small brick corner inlays flank limestone corner piers as in the photo composition.
rect(-11.96,-11.60,1.15,9.75);rect(11.60,11.96,1.15,9.75)
mesh=bpy.data.meshes.new('HAAS_R7_EastFacade_InlayMesh');mesh.from_pydata(verts,[],faces);mesh.materials.append(brick);mesh.update()
o=bpy.data.objects.new('HAAS_R7_EastFacade_Inlaid_Brickwork',mesh);c.objects.link(o)
o['evidence_basis']='Qualitative red-brick inlay around limestone openings/corners follows Purdue exterior photo; extents are perspective estimates. Geometry is flush to the GIS east wall.'
o['source_url']='https://events.purdue.edu/felix_haas_hall'
# Remove unsupported uniform doors. The nondimensional plan does not document room entry doors or swings.
for name in ['HAAS_Plan_R6_Estimated_Door_Leaves','HAAS_Plan_R6_Estimated_Door_Frames']:
    o=bpy.data.objects.get(name)
    if o:bpy.data.objects.remove(o,do_unlink=True)
# Replace legend language so schematic gaps are not mistaken for surveyed door locations.
legend=bpy.data.objects.get('HAAS_Plan_Evidence_Legend_Text')
if legend:
    legend.data.body='PLAN: room names and broad adjacency\nESTIMATE: room sizes, wall heights and furnishings\nOPENINGS: schematic; door positions and swings unavailable'
    legend['evidence_basis']='Purdue first-floor plan; metric room registration and door layout are not shown.'
# Archive hidden geometry stays hidden.
if archive:archive.hide_render=True;archive.hide_viewport=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
Path('audit/batch3_haas/round7_changes.json').write_text(json.dumps({'east_wall_limestone_faces':face_count,'detached_skin_archived':bool(skin and archive),'brick_inlay_faces':len(faces),'inlay_groups':'Two lower arches, three upper windows, central entrance, two corner strips.','doors_removed':True,'interior_evidence':'Purdue nondimensional plan has room names/adjacency but does not document door positions or swing directions; the 47 inferred leaves/frames were removed.','GIS_shell_geometry_untouched':True},indent=2),encoding='utf-8')
print('ROUND7_INTEGRATED',face_count,len(faces),len(c.objects))

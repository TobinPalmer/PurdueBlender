"""Build a review candidate with a continuous GIS-derived Parker Hall shell."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/winifred_parker_hall.blend'
AUDIT=ROOT/'audit/winifred_parker_hall'
shell=json.loads((AUDIT/'gis_shell_geometry_candidate.json').read_text())
origin=tuple(shell['origin_campus_xy_m'])

# Reopen pristine source then alter only this candidate.
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections['Asset_winifred_parker_hall']
root=bpy.data.objects['AssetRoot_winifred_parker_hall']
brick=bpy.data.materials['Parker_Purdue_Red_Brick']
removed=[]
structural={'Parker_EastWing_MainMass','Parker_EastWing_MainMass_North','Parker_EastWing_MainMass_South','Parker_EastWing_MainMass_Upper','Parker_SouthWing_MainMass','Parker_NorthWing_MainMass','Parker_CenterFinger_MainMass'}
for name in list(structural):
    o=bpy.data.objects.get(name)
    if o:
        removed.append(name); bpy.data.objects.remove(o,do_unlink=True)
def mesh_object(name, verts, faces, mat):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.materials.append(mat); me.update()
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); ob.parent=root
    # Existing meshes use an inverse parent transform to retain a manifest-centered local frame.
    ob.matrix_parent_inverse=Matrix.Identity(4)
    return ob
def extrude(name, r, z0,z1, mat, top_tris=None):
    n=len(r); verts=[(x,y,z0) for x,y in r]+[(x,y,z1) for x,y in r]
    faces=[]
    faces.append(tuple(reversed(range(n))))
    for i in range(n):
        j=(i+1)%n; faces.append((i,j,j+n,i+n))
    if top_tris:
        faces += [tuple(i+n for i in t) for t in top_tris]
    else: faces.append(tuple(range(n,2*n)))
    return mesh_object(name,verts,faces,mat)
extrude('Parker_GIS_Continuous_Upper_Shell',shell['ring_local_xy_m'],4.2,20.2,brick)
for idx,g in enumerate(shell['ground_components']):
    extrude(f'Parker_GIS_Ground_Core_{idx}',g['ring'],0,4.2,brick,g['triangles'])
# Replace boxy roof plates with a triangulated slab cut exactly to the official outline.
roofmat=bpy.data.materials.get('Parker_Roof_Membrane')
if not roofmat: roofmat=brick
roof=mesh_object('Parker_GIS_Roof_Outline',[(x,y,20.16) for x,y in shell['ring_local_xy_m']]+[(x,y,20.32) for x,y in shell['ring_local_xy_m']],[],roofmat)
n=len(shell['ring_local_xy_m']); faces=[]
for i in range(n): j=(i+1)%n; faces.append((i,j,j+n,i+n))
faces.extend([tuple(n+i for i in t) for t in shell['roof_triangles']])
roof.data.clear_geometry()
roof.data.from_pydata([(x,y,20.16) for x,y in shell['ring_local_xy_m']]+[(x,y,20.32) for x,y in shell['ring_local_xy_m']],[],faces); roof.data.update()
# Delete old rectangular roof/water-table/beltcourse elements that no longer track the GIS perimeter.
for o in list(col.objects):
    if o.name.startswith('Parker_Roof_') and o.name not in ('Parker_Roof_Membrane',):
        if o.type=='MESH' and ('Penthouse' not in o.name):
            removed.append(o.name); bpy.data.objects.remove(o,do_unlink=True)
    elif o.name.startswith('Parker_Beltcourse_'):
        removed.append(o.name); bpy.data.objects.remove(o,do_unlink=True)
    elif o.name.startswith('Parker_Base_WaterTable_'):
        removed.append(o.name); bpy.data.objects.remove(o,do_unlink=True)
# Find source boundary edge intersections for facade alignment in campus coordinates.
def edge_x(y, side):
    xs=[]
    ring_c=[(x+origin[0],y+origin[1]) for x,y in shell['ring_local_xy_m']]
    for a,b in zip(ring_c,ring_c[1:]+ring_c[:1]):
        if min(a[1],b[1])-1e-4 <= y <= max(a[1],b[1])+1e-4:
            if abs(b[1]-a[1])<1e-7: xs.extend([a[0],b[0]])
            else: xs.append(a[0]+(y-a[1])/(b[1]-a[1])*(b[0]-a[0]))
    return (max(xs) if side=='east' else min(xs)) if xs else None
# East fenestration sits on the outline, rather than five metres beyond it.
east_updates=[]
for o in list(col.objects):
    if o.name.startswith(('Parker_Win_East_','Parker_Sill_East_','Parker_Curtain_East_')):
        y=o.matrix_world.translation.y+origin[1]
        ex=edge_x(y,'east')
        if ex is not None:
            old=o.matrix_world.translation.x+origin[0]
            delta=(ex+0.12)-old
            o.location.x+=delta
            east_updates.append({'object':o.name,'old_x':old,'new_x':ex+0.12,'campus_y':y})
# The official exterior photo shows tall, narrow punched windows with restrained sills.
# Reduce the earlier square-like glazing and oversized trim while preserving each bay center.
fenestration=[]
for o in list(col.objects):
    name=o.name
    if name.startswith('Parker_Win_'):
        axis='x' if ('South' in name or 'North' in name) else 'y'
        if axis=='x': o.scale.x*=0.68
        else: o.scale.y*=0.68
        o.scale.z*=1.12
        fenestration.append({'object':name,'plan_scale':0.68,'height_scale':1.12})
    elif name.startswith('Parker_Sill_'):
        axis='x' if ('South' in name or 'North' in name) else 'y'
        if axis=='x': o.scale.x*=0.68
        else: o.scale.y*=0.68
        o.scale.z*=0.5
    elif name.startswith('Parker_Spandrel_'):
        axis='x' if ('South' in name or 'North' in name) else 'y'
        if axis=='x': o.scale.x*=0.68
        else: o.scale.y*=0.68
        o.scale.z*=0.55
# West facade bays 0–3 are unsupported by the GIS outline. Remove them and align the remaining bays.
west_removed=[]; west_updates=[]
for o in list(col.objects):
    if o.name.startswith(('Parker_Win_West_','Parker_Sill_West_')):
        try: bay=int(o.name.split('_B')[1].split('_')[0])
        except Exception: continue
        y=o.matrix_world.translation.y+origin[1]
        if bay<4:
            west_removed.append(o.name); bpy.data.objects.remove(o,do_unlink=True); continue
        wx=edge_x(y,'west')
        if wx is not None:
            old=o.matrix_world.translation.x+origin[0]; new=wx-.12
            o.location.x += new-old; west_updates.append({'object':o.name,'old_x':old,'new_x':new,'campus_y':y})
# The easternmost north-facade bay is beyond the GIS boundary at this northward taper.
north_removed=[]
for o in list(col.objects):
    if o.name.startswith(('Parker_Win_North_','Parker_Sill_North_')) and '_B5' in o.name:
        north_removed.append(o.name); bpy.data.objects.remove(o,do_unlink=True)
# Save candidate. The source remains untouched.
out=AUDIT/'Winifred_Parker_R5_GIS_shell_candidate.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report={'candidate':str(out),'source_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'structural_replacements':removed,'new_upper_shell_area_m2':shell['footprint_area_m2'],'new_ground_core_area_m2':shell['ground_area_m2'],'east_windows_aligned':len(east_updates),'east_alignment_sample':east_updates[:8],'west_windows_removed':west_removed,'west_windows_aligned':len(west_updates),'north_windows_removed':north_removed,'fenestration_adjustments':len(fenestration),'technical_notes':['Upper-story structure preserves continuous facade over the Third Street retail zone.','Ground-floor structural core follows GIS outline north of existing storefront/entry datum.','Broad rectangular floor belts and boxy ground water-table bars were removed pending evidence-backed facade detailing.','Window shape and restrained sills are aligned with the official 2021 facade photograph.','Unsupported west and north facade bays removed.'],'new_objects':['Parker_GIS_Continuous_Upper_Shell']+[f'Parker_GIS_Ground_Core_{i}' for i in range(len(shell['ground_components']))]+['Parker_GIS_Roof_Outline']}
(AUDIT/'gis_candidate_change_record.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

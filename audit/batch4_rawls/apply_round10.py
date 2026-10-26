import bpy, math, re, json, shutil
from pathlib import Path
from mathutils import Vector
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
src=root/'modular/buildings/rawls_hall.blend'
candidate=root/'audit/batch4_rawls/rawls_hall_r10_candidate.blend'
shutil.copy2(src,candidate)
bpy.ops.wm.open_mainfile(filepath=str(candidate))
coll=bpy.data.collections['Asset_rawls_hall']
# Row assignment is inferred from the existing 42 desk labels (six groups of seven).
desks=sorted([o for o in bpy.data.objects if re.fullmatch(r'RAWL_2026_1086_Desk(?:\.\d{3})?',o.name)], key=lambda o:int(o.name.rsplit('.',1)[1]) if '.' in o.name else 0)
assert len(desks)==42, len(desks)
rows=[]
for r in range(6):
 row=desks[r*7:(r+1)*7]
 ctr=sum((o.matrix_world.translation for o in row),Vector())/len(row)
 # major row axis, estimated from the visible existing desk centers
 axis=(row[-1].matrix_world.translation-row[0].matrix_world.translation).normalized()
 rows.append((ctr,axis,row))
# Lift desks, chairs and their existing 4 legs per desk to a schematic stepped profile.
for idx,(desk,_) in enumerate(zip(desks,desks)):
 r=idx//7; lift=r*0.13
 desk.location.z += lift
 suffix=desk.name[len('RAWL_2026_1086_Desk'):]
 chair=bpy.data.objects.get('RAWL_2026_1086_Chair'+suffix)
 if chair: chair.location.z+=lift
 # Find legs nearest the unraised desk footprint; the grid has 4 legs per desk.
 orig=desk.matrix_world.translation.copy(); orig.z-=lift
 legs=[]
 for leg in [o for o in bpy.data.objects if o.name.startswith('RAWL_2026_DeskLeg')]:
  if (leg.location.xy-orig.xy).length < 0.75: legs.append(leg)
 for leg in legs:
  if not leg.get('rawl_r10_lifted'):
   leg.location.z+=lift; leg['rawl_r10_lifted']=True
# Add broad, low schematic carpeted step platforms under rows 1-5.
carpet=bpy.data.materials['RAWL_1086_Floor_CharcoalCarpet_Estimated']
wood=bpy.data.materials['RAWL_Interior_Wood']
metal=bpy.data.materials['RAWL_Dark_Bronze_Metal']
white=bpy.data.materials['RAWL_Interior_WarmWhite']
def cube_obj(name, loc, dims, mat, rot=0, bevel=0.03):
 bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
 o=bpy.context.object; o.name=name; o.dimensions=dims; o.rotation_euler[2]=rot
 bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
 for c in list(o.users_collection): c.objects.unlink(o)
 coll.objects.link(o)
 if mat:o.data.materials.append(mat)
 if bevel:
  mod=o.modifiers.new('Softened_edges_schematic','BEVEL'); mod.width=bevel; mod.segments=2
  mod2=o.modifiers.new('Weighted_corner_normals','WEIGHTED_NORMAL')
 o['evidence_status']='schematic classroom interior detail; not dimensioned by the cited plan'
 return o
for r,(ctr,axis,row) in enumerate(rows[1:],start=1):
 lift=r*0.13
 length=(row[-1].location-row[0].location).length+0.55
 angle=math.atan2(axis.y,axis.x)
 p=cube_obj(f'RAWL_1086_R10_Schematic_Tier_{r:02d}',(ctr.x,ctr.y,lift*0.5),(length,1.18,lift),carpet,angle,0.035)
 p['tier_rise_m_schematic']=lift
 p['source_note']='Tiered, fixed classroom tables are listed by Purdue; exact riser dimensions are unverified.'
# teaching wall / paired projection surfaces on the existing plan-derived east-side wall
wall=bpy.data.objects['RAWL_2026_Plan1086_01_00']
wall_center=wall.matrix_world.translation.copy(); rot=wall.rotation_euler.z
inward=Vector((-math.cos(rot+math.pi/2),-math.sin(rot+math.pi/2),0)) # intentional robust sign reset below
# Local wall normal is (-sin(rot), cos(rot)); room interior lies toward desks, negative-X side.
local_y=Vector((-math.sin(rot),math.cos(rot),0))
# choose inward direction from wall center towards seat centroid
seat_ctr=sum((d.matrix_world.translation for d in desks),Vector())/len(desks)
inward=(seat_ctr-wall_center).to_2d().normalized()
inward3=Vector((inward.x,inward.y,0))
wall_ctr=wall_center.copy(); wall_ctr += inward3*0.13
wall_ctr.z=2.42
# Two simple, paired matte projection panels aligned with the wall tangent; both are source-informed by official 1086 dual-projector equipment listing.
for i, offset in enumerate([-1.12,1.12],start=1):
 pos=wall_ctr.copy(); pos.x += math.cos(rot)*offset; pos.y += math.sin(rot)*offset
 panel=cube_obj(f'RAWL_1086_R10_Schematic_Projection_Surface_{i:02d}',pos,(1.95,0.045,1.30),white,rot,0.025)
 panel['source_note']='Equipment arrangement schematic; room listing supports dual projectors, but screen sizes/locations are not surveyed.'
 # narrow bronze rails frame the panel
 for zoff in [-0.68,0.68]:
  p=pos.copy(); p.z+=zoff
  cube_obj(f'RAWL_1086_R10_Screen_Frame_{i:02d}_{"top" if zoff>0 else "bottom"}',p,(2.03,0.07,0.055),metal,rot,0.012)
# lectern at the front teaching position, slightly offset from the sightline
lec_loc=wall_center.copy()+inward3*1.75
lec_loc.z=0.55
base=cube_obj('RAWL_1086_R10_Schematic_Lectern_Pedestal',lec_loc,(0.58,0.48,0.96),wood,rot,0.045)
# sloped reading top at waist height
head=lec_loc.copy(); head.z=1.08; head += inward3*0.04
cube_obj('RAWL_1086_R10_Schematic_Lectern_Top',head,(0.72,0.62,0.12),wood,rot,0.045)
base['source_note']='Lectern is a schematic teaching fixture. Official room materials list a lectern; exact model/location is not surveyed.'
# Label source-supported door openings as circulation endpoints and leave any beyond them schematic.
for nm in ['RAWL_2026_Plan1086_Jamb_03_A','RAWL_2026_Plan1086_Jamb_03_B','RAWL_2026_Plan1086_Jamb_05_A','RAWL_2026_Plan1086_Jamb_05_B']:
 obj=bpy.data.objects.get(nm)
 if obj: obj['evidence_note']='Opening placement follows the 2024 first-floor plan; onward route beyond the shown plan is not modeled as verified.'
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(candidate))
print(json.dumps({'candidate':str(candidate),'desks':len(desks),'tier_platforms':5,'lift_m':[r*.13 for r in range(6)],'interior_added':['paired schematic projection surfaces','lectern','front wall cues'],'object_count':len(bpy.context.scene.objects)},indent=2))

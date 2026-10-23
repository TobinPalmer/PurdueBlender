import bpy, math, json, re
from pathlib import Path
from mathutils import Matrix, Vector
C=bpy.data.collections['Asset_felix_haas_hall']; P=bpy.data.filepath
stone=bpy.data.materials['HAAS_Photo_Limestone']; brick=bpy.data.materials['Purdue_Red_Brick.001']; roof=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated']
source='Purdue Events exterior photo https://events.purdue.edu/felix_haas_hall; perspective reference only, dimensions/elevation schedule estimated.'
# Remove prior R5 objects for safe re-run.
for o in list(C.objects):
 if o.name.startswith('HAAS_R5_'):bpy.data.objects.remove(o,do_unlink=True)
# Retune warm brick to the darker red-brown seen in the Purdue reference; retain a legible small-format brick course.
brick.diffuse_color=(.18,.035,.015,1)
for n in brick.node_tree.nodes:
 if n.type=='TEX_BRICK':
  n.inputs['Color1'].default_value=(.18,.035,.015,1); n.inputs['Color2'].default_value=(.12,.020,.008,1); n.inputs['Mortar'].default_value=(.15,.085,.052,1)
# Deeper red clay roof, preserving readable roof courses and reducing copper/salmon appearance.
roof.diffuse_color=(.032,.005,.002,1)
for n in roof.node_tree.nodes:
 if n.type=='TEX_BRICK':
  n.inputs['Color1'].default_value=(.030,.0045,.0018,1);n.inputs['Color2'].default_value=(.017,.0022,.0008,1);n.inputs['Mortar'].default_value=(.007,.001,.0004,1)
  n.inputs['Brick Width'].default_value=.62;n.inputs['Row Height'].default_value=.25
 if n.type=='BUMP':n.inputs['Strength'].default_value=.12;n.inputs['Distance'].default_value=.0025
# The photo shows red-brown brick fields between Bedford-limestone piers; current facade base is a face plane.
facade=bpy.data.objects['HAAS_Photo_Entrance_Limestone_Facade']
facade.data.materials.clear();facade.data.materials.append(brick);facade['evidence']=source;facade['material_interpretation']='Brick field between pale limestone piers and opening surrounds, based on Purdue Events exterior photo.'
# Add two upper/lower window bays to each side wing on the otherwise blank east end wall by rotating existing side-bay assemblies.
# Side schedules here are inferred; positions stay on the corresponding GIS wall segments.
def clone_group(idx,target,tag):
 src=[o for o in C.objects if o.name.startswith('HAAS_Estimated_Side_') and re.search(r'_S_'+str(idx)+r'(?:_|$)',o.name) and 'Stone_Band' not in o.name]
 pivot=Vector((-22.8,-26.1,0)); dst=Vector((2.30,target,0)); rz=Matrix.Rotation(math.radians(90),4,'Z');t0=Matrix.Translation(-pivot);t1=Matrix.Translation(dst)
 count=0
 for o in src:
  q=o.copy();q.data=o.data.copy() if o.data else None;q.name='HAAS_R5_East_'+tag+'_'+o.name.split('_S_',1)[-1]
  C.objects.link(q);q.matrix_world=t1@rz@t0@o.matrix_world;q['evidence']=source+' East wing bay is inferred from the uninterrupted GIS wall; no measured east elevation located.';count+=1
 return count
n_south=clone_group(0,-18.8,'SouthWing');n_north=clone_group(0,19.4,'NorthWing')
def box(name,loc,dims,material,claim):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 C.objects.link(o);o.data.materials.clear();o.data.materials.append(material);o['evidence']=claim;return o
# Corner piers and repeated belt courses visually tie both exposed east wings to the long elevations.
for wing,y0,y1 in [('South',-25.98,-11.55),('North',12.64,26.76)]:
 yc=(y0+y1)/2; length=y1-y0
 for j,z,h in [(0,1.02,.22),(1,5.15,.18),(2,9.55,.22)]:box(f'HAAS_R5_East_{wing}_Belt_{j}',(2.30,yc,z),(.18,length-.55,h),stone,source+' Dimension estimated; preserves GIS shell.')
 for j,y in enumerate([y0+.25,y1-.25]):
  box(f'HAAS_R5_East_{wing}_Pier_{j}',(2.30,y,5.18),(.20,.48,8.35),stone,source+' Dimension estimated; preserves GIS shell.')
# Attach explicit evidence categories to plan-derived traces and inferred construction/furnishings.
for o in C.objects:
 if not o.name.startswith('HAAS_Plan_'):continue
 o['source_plan']='https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf'
 if any(k in o.name for k in ['Desk','Pedestal','ConferenceTable']):o['geometry_basis']='Illustrative furniture. It does not establish the room dimensions.'
 elif 'Partition' in o.name:o['geometry_basis']='Room boundary follows the nondimensional first-floor plan; metric size and wall height are estimates.'
 elif any(k in o.name for k in ['Stair','Lift','Label']):o['geometry_basis']='Room/core identity and broad adjacency follow the nondimensional plan; metric placement and size are estimates.'
 else:o['geometry_basis']='Inferred from the nondimensional first-floor plan; metric geometry is estimated.'
# Add an unambiguous on-render legend in the empty east notch outside the GIS footprint.
plate_mat=bpy.data.materials.get('HAAS_Plan_Label_Plate_estimated');ink=bpy.data.materials.get('HAAS_Plan_Label_Ink')
box('HAAS_Plan_Evidence_Legend_Plate',(10.15,-18.8,3.98),(16.4,2.25,.08),plate_mat,'Legend only; outside GIS footprint.')
cu=bpy.data.curves.new('HAAS_Plan_Evidence_Legend_Text','FONT');cu.body='PLAN: room names and broad adjacency from Purdue CS first-floor diagram\nESTIMATED: dimensions, placement, doors, wall heights and furniture';cu.size=.39;cu.extrude=.001
ob=bpy.data.objects.new('HAAS_Plan_Evidence_Legend_Text',cu);C.objects.link(ob);ob.location=(2.45,-19.32,4.03);cu.materials.append(ink);ob['source_plan']='https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf';ob['geometry_basis']='Labels source status; no dimensions are stated by the plan.'
C['interior_scope']='One nondimensional Purdue CS first-floor diagram modeled. Room names and broad adjacency are plan-derived. Metric registration/dimensions, wall heights, door placement, circulation widths, and furnishings are estimates; no upper-floor or measured plan verified.'
C['round5_entry_material']='Brick field with limestone pier and arch overlays now matches qualitative brick-and-Bedford-stone contrast in Purdue Events photo; face remains a shallow facade surface over GIS envelope.'
bpy.ops.wm.save_as_mainfile(filepath=P)
Path('audit/batch3_haas/round5_changes.json').write_text(json.dumps({'blank_wall':'added one upper/lower side-window assembly to each east end wing with limestone corner piers and three belt courses; inferred east elevation marked estimate','entrance':'changed facade base to red-brown brick field; retained source-based limestone piers/bands/opening surrounds','roof':'deepened to red-clay tone from salmon/copper, preserved 0.62x0.25m visible procedural courses','interior':'added visible plan-vs-estimate legend; tagged partitions, labels, stairs/lift and illustrative furniture with evidence basis','GIS':'footprint, marker, shell transforms unchanged','new_east_window_components':n_south+n_north,'limitations':'Window overlays do not create measured openings or hollow wall continuity; room dimensions remain estimates.'},indent=2))

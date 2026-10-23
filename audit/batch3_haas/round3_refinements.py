import bpy, math, json
from pathlib import Path
C=bpy.data.collections['Asset_felix_haas_hall'];P=bpy.data.filepath
def mat(n,c):
 m=bpy.data.materials.get(n)
 if not m:m=bpy.data.materials.new(n)
 m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1);return m
def box(name,loc,dims,material):
 old=bpy.data.objects.get(name)
 if old:bpy.data.objects.remove(old,do_unlink=True)
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 C.objects.link(o);o.data.materials.append(material);return o
stone=mat('HAAS_Photo_Limestone',(.82,.72,.52))
roof=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated']
roof.diffuse_color=(.009,.0012,.0004,1)
for n in roof.node_tree.nodes:
 if n.type=='TEX_BRICK':
  n.inputs['Color1'].default_value=(.015,.002,.0008,1);n.inputs['Color2'].default_value=(.008,.001,.0004,1);n.inputs['Mortar'].default_value=(.005,.0008,.0003,1)
# Repeated limestone piers and framed masonry bays on the near long elevation.
# The Purdue image supports the brick-and-stone rhythm; spacing and dimensions
# are estimates because the photograph is perspective and no elevation drawing exists.
for i,x in enumerate([-25.5,-17.25,-9.05,-.85,7.25,12.45]):
 ob=box('HAAS_Estimated_Long_Facade_Pier_%02d'%i,(x,-26.04,5.15),(.62,.24,8.65),stone)
 ob['source']='Purdue Felix Haas Hall exterior photo https://events.purdue.edu/felix_haas_hall; bay rhythm observed, spacing and dimensions estimated.'
 # Small block capitals and bases make each pier read as a limestone structural bay.
 for z,label in [(1.05,'Base'),(9.45,'Capital')]:
  b=box('HAAS_Estimated_Long_Facade_%s_%02d'%(label,i),(x,-26.04,z),(.90,.28,.34),stone)
  b['source']='Photo-derived architectural detail; dimensions estimated.'
# Room labels become short dark-on-pale cards above the schematic walls.
label_specs={
 'HAAS_Plan_Label_00':('STAIR 1\nWEST',-15.0,22.0,2.4),
 'HAAS_Plan_Label_01':('STAIR 2\nNORTH',-23.5,-16.5,2.7),
 'HAAS_Plan_Label_02':('STAIR 3\nENTRY',4.5,5.35,2.5),
 'HAAS_Plan_Label_03':('LIFT',-20.6,-21.0,1.5),
 'HAAS_Plan_Label_04':('RR 117',-8.7,-13.3,1.9),
 'HAAS_Plan_Label_05':('RR 119',-8.9,-17.8,1.9),
 'HAAS_Plan_Label_06':('CONF 111',-8.7,.8,2.5),
 'HAAS_Plan_Label_07':('CONF 101',10.7,7.4,2.5),
 'HAAS_Plan_Label_08':('STUDENT\nORG',-15.8,-8.0,2.4),
 'HAAS_Plan_Label_09':('TA OFFICES',-15.8,6.1,2.8)}
plate=mat('HAAS_Plan_Label_Plate_estimated',(.76,.68,.50))
ink=mat('HAAS_Plan_Label_Ink',(.025,.025,.022))
for name,(body,x,y,w) in label_specs.items():
 o=bpy.data.objects.get(name)
 if not o:continue
 o.data.body=body;o.data.size=.40;o.data.extrude=.002;o.location=(x-w/2+.12,y-.20,3.91)
 o.data.materials.clear();o.data.materials.append(ink)
 h=.78 if '\n' not in body else .92
 back=box(name+'_Plate',(x,y,3.84),(w,h,.055),plate)
 back['evidence']='Room label follows Purdue CS first-floor plan; plan has no scale and card is a visual annotation.'
 o['label_location']='approximate plan registration; room identity follows published diagram'
 # Thin dark border provides separation from the plan floor.
 for dx in [-w/2,w/2]:
  box(name+'_BorderX_'+str(dx),(x+dx,y,3.88),(.035,h+.07,.025),ink)
 for dy in [-h/2,h/2]:
  box(name+'_BorderY_'+str(dy),(x,y+dy,3.88),(w+.07,.035,.025),ink)
for name in ['HAAS_Plan_Label_10','HAAS_Plan_Label_11']:
 o=bpy.data.objects.get(name)
 if o:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=P)
Path('audit/batch3_haas/round3_refinements.json').write_text(json.dumps({
 'long_facade':'six repeated pale-stone piers with base/capital blocks on visible long elevation; spacing/dimensions estimated from Purdue exterior photo',
 'roof':'tile shader darkened and warmed; procedural brick texture retained',
 'labels':'ten room/core labels updated with contrasting plates; sourced to nondimensioned first-floor plan',
 'continuity':'entry stair top is 1.50m, same as raised door threshold; 17 tread slabs descend to grade; no survey dimensions',
 'limits':'No measured long elevation, side window schedule, roof survey, or scaled interior plan available.'
},indent=2))

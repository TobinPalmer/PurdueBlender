import bpy,json
from pathlib import Path
p=bpy.data.filepath;c=bpy.data.collections['Asset_felix_haas_hall'];stone=bpy.data.materials['HAAS_Photo_Limestone'];created=[]
def panel(name,y,z,w,h):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(13.005,y,z));o=bpy.context.object;o.name='HAAS_Photo_StonePanel_'+name;o.dimensions=(.045,w,h);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for col in list(o.users_collection):col.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(stone);o['evidence']='Purdue Felix Haas Hall exterior photo, https://events.purdue.edu/felix_haas_hall; dimensions estimated from photo and GIS facade.';created.append(o.name)
# Light limestone spandrels and bay returns on the photo-documented entrance elevation.
# Existing window trim and piers remain visible in front of these wall panels.
for center in [-7.65,0,7.65]:
 baylo=center-3.55;bayhi=center+3.55
 # upper floor window opening z 6.9..8.5
 panel('UpperLeft_'+str(center),(baylo+center-1.6)/2,7.7,(center-1.6-baylo),5.3)
 panel('UpperRight_'+str(center),(center+1.6+bayhi)/2,7.7,(bayhi-center-1.6),5.3)
 panel('UpperSill_'+str(center),center,5.8,7.1,2.2)
 panel('UpperLintel_'+str(center),center,9.3,7.1,1.6)
# Ground story side windows, z 1.5..4.7, on outer bays.
for center in [-7.65,7.65]:
 baylo=center-3.55;bayhi=center+3.55
 panel('LowerLeft_'+str(center),(baylo+center-1.5)/2,3.1,center-1.5-baylo,3.2)
 panel('LowerRight_'+str(center),(center+1.5+bayhi)/2,3.1,bayhi-center-1.5,3.2)
 panel('LowerSill_'+str(center),center,1.0,7.1,1.0)
 panel('LowerLintel_'+str(center),center,5.8,7.1,2.2)
# Central double-door bay: stone returns around the doorway and continuous panel above it.
panel('DoorLeft',-2.25,1.85,2.0,2.7);panel('DoorRight',2.25,1.85,2.0,2.7)
panel('DoorLintel',0,4.85,7.1,3.3)
# Align palette with the warm limestone visible in Purdue's entrance photo.
stone.diffuse_color=(.62,.57,.47,1)
if stone.use_nodes:stone.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.62,.57,.47,1)
bpy.ops.wm.save_as_mainfile(filepath=p)
Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/stone_panels.json').write_text(json.dumps({'added_panel_count':len(created),'objects':created,'source':'https://events.purdue.edu/felix_haas_hall','dimensions':'estimated from qualitative photo; GIS shell and wall footprint unchanged'},indent=2))

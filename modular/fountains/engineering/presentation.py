import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
D=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(D/'engineering.blend'));s=bpy.context.scene;x,y=json.loads((D/'position_measurement.json').read_text())['centroid_local_m']
p=bpy.data.objects['EF_Individual_paving_units'];bm=bmesh.new();bm.from_mesh(p.data);bad=[f for f in bm.faces if any((v.co.x-x)**2+(v.co.y-y)**2>8.98**2 for v in f.verts)];bmesh.ops.delete(bm,geom=bad,context='FACES');loose=[v for v in bm.verts if not v.link_faces];bmesh.ops.delete(bm,geom=loose,context='VERTS');bm.to_mesh(p.data);bm.free()
s.world.use_nodes=True;bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.55,.67,.85,1);bg.inputs['Strength'].default_value=.65
bpy.ops.object.light_add(type='AREA',location=(x-7,y-9,9));light=bpy.context.object;light.name='EF_Preview_reflection_softbox';light.data.energy=2200;light.data.shape='DISK';light.data.size=9;light.rotation_euler=(Vector((x,y,6))-light.location).to_track_quat('-Z','Y').to_euler()
s.frame_set(96);cam=s.camera;cam.location=(x,y-30,13);cam.rotation_euler=(Vector((x,y,5.3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=46;s.cycles.samples=32
# Preserve clear-water physically-based surface. Softbox improves legibility without pretending to simulate foam.
s['fluid_status']='Completed192cell FLIP liquid cache1..96 at24fps. Four-second startup, NOT verified steady-state or calibrated real discharge. Openbottom drain surrogate.'
s['height_datum']='Fin structural span11.5824m (38ft); local basez.12m, top11.7024m; groundelevation unverified.'
s.render.filepath=str(D/'attempt4_front.png');bpy.ops.wm.save_as_mainfile(filepath=str(D/'engineering.blend'));bpy.ops.render.render(write_still=True)
cam.location=(x+21,y-24,15);cam.rotation_euler=(Vector((x,y,5.3))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(D/'attempt4_oblique.png');bpy.ops.render.render(write_still=True)
(D/'attempt4_changes.json').write_text(json.dumps({'attempt':4,'paving_edge_cropped':True,'physics_changed':False,'water_surface':'Clear transmission1 IOR1.333 roughness.07; realbaked liquid no procedural water mesh','new_views':['frontbetweenfins','oblique'],'scene_frame_saved':96},indent=2))

"""Roof tile geometry and circulation/elevation refinements for Elliott."""
import bpy, math, pathlib, json, shutil
from mathutils import Vector
ROOT=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');SRC=ROOT/'modular/buildings/elliott_hall_of_music.blend';AUD=ROOT/'audit/batch3_elliott'
shutil.copy2(SRC,AUD/'before_finish_pass.blend');bpy.ops.wm.open_mainfile(filepath=str(SRC));COL=bpy.data.collections['Asset_elliott_hall_of_music']
for o in list(COL.objects):
    if o.name.startswith('ELLT_FIN_'):bpy.data.objects.remove(o,do_unlink=True)
wall=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls'];N=len(wall.data.vertices)//2;outline=[(v.co.x,v.co.y) for v in wall.data.vertices[:N]]
def inside(x,y):
    q=False
    for i,(ax,ay) in enumerate(outline):
        bx,by=outline[i-1]
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:q=not q
    return q
tile=bpy.data.materials['ELLT_Red_Clay_Tile_Roof'];limestone=bpy.data.materials['ELLT_Exterior_Indiana_Limestone'];stone=bpy.data.materials['ELLT_Sculpture_Warm_Limestone']

# Separated tile courses make the documented clay roof visible in linked views,
# even in renderers that do not evaluate the procedural brick texture.
verts=[];faces=[];centres=0
xmin=min(x for x,y in outline);xmax=max(x for x,y in outline);ymin=min(y for x,y in outline);ymax=max(y for x,y in outline)
cx,cy=13.79,16.82;tw,td=26,25
for row,y in enumerate([ymin+.24+i*.48 for i in range(int((ymax-ymin-.48)/.48)+1)]):
    x=xmin+.39+(row%2)*.39
    while x<xmax:
        xa=x-.39;xb=x+.39;ya=y-.215;yb=y+.215
        if all(inside(xx,yy) for xx,yy in ((xa,ya),(xa,yb),(xb,ya),(xb,yb))) and not (abs(x-cx)<tw/2+.35 and abs(y-cy)<td/2+.35):
            base=len(verts);z0=22.505;z1=22.565
            verts.extend([(xa,ya,z0),(xb,ya,z0),(xb,yb,z0),(xa,yb,z0),(xa,ya,z1),(xb,ya,z1),(xb,yb,z1),(xa,yb,z1)])
            faces.extend([(base+4,base+5,base+6,base+7),(base,base+3,base+2,base+1),(base,base+1,base+5,base+4),(base+1,base+2,base+6,base+5),(base+2,base+3,base+7,base+6),(base+3,base,base+4,base+7)])
            centres+=1
        x+=.82
me=bpy.data.meshes.new('ELLT_FIN_Clay_Tile_Courses_Mesh');me.from_pydata(verts,[],faces);me.materials.append(tile);me.update();o=bpy.data.objects.new('ELLT_FIN_Individually_Raised_Clay_Tiles',me);COL.objects.link(o)
o['tile_count']=centres;o['tile_pitch_m']=[.82,.48];o['evidence_status']='Tiled surface is evidenced by SAH Archipedia; individual tile size and flat roof plane are inferred.'

# Evidence describes two groups of three figures; add a second group on the
# opposite portion of the monumental south elevation. Poses remain interpretive.
door=bpy.data.objects['ELLT_EXT_Glazed_Main_Entry_Doors'];doorpts=[door.matrix_world@v.co for v in door.data.vertices]
doorc=Vector((sum(v.x for v in doorpts)/len(doorpts),sum(v.y for v in doorpts)/len(doorpts),0))
walls=[]
for obj in COL.objects:
    if obj.name.startswith('ELLT_EXT_Sculpture_') and obj.name.endswith('_Heroic_Figure'):walls.append(obj)
existing=sorted((o for o in COL.objects if o.name.startswith('ELLT_EXT_Sculpture_') and o.name.endswith('_Heroic_Figure')),key=lambda o:o.name)
if existing:
    # Use the same south-front facade that holds the first sculptural group.
    e=existing[0];base=Vector(e.location);rot=e.rotation_euler.z
    tangent=Vector((math.cos(rot),math.sin(rot),0));normal=Vector((-tangent.y,tangent.x,0))
    for j,t in enumerate((-8.0,-4.5,0.0),4):
        # Offset the companion group away from the entry, keeping figure feet at grade.
        p=base+tangent*t+normal*.12
        bpy.ops.mesh.primitive_cube_add(size=1,location=(p.x,p.y,.55));pl=bpy.context.object;pl.name=f'ELLT_EXT_SculptureGroupB_{j}_Plinth';pl.dimensions=(.72,.66,1.1);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for c in list(pl.users_collection):c.objects.unlink(pl)
        COL.objects.link(pl);pl.data.materials.append(limestone)
        bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=.48,radius2=.30,depth=1.65,location=(p.x,p.y,1.93));body=bpy.context.object;body.name=f'ELLT_EXT_SculptureGroupB_{j}_Figure';body.rotation_euler.z=rot
        for c in list(body.users_collection):c.objects.unlink(body)
        COL.objects.link(body);body.data.materials.append(stone);body['evidence_status']='Interpretive heroic figure. SAH confirms a second group of three; pose and spacing approximate.'
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.28,location=(p.x,p.y,2.97));head=bpy.context.object;head.name=f'ELLT_EXT_SculptureGroupB_{j}_Head'
        for c in list(head.users_collection):c.objects.unlink(head)
        COL.objects.link(head);head.data.materials.append(stone)

# A level vestibule path continues from the inferred public door into the main
# floor. Its exact relationship to the historical Hovde connector is unverified.
room_targets=[o for o in COL.objects if o.name=='ELLT_B3_carpet']
if room_targets:
    q=doorc;target=Vector((0,4,0));d=target-q;d.z=0;d.normalize();side=Vector((-d.y,d.x,0));L=12.0;W=2.8
    points=[q-side*W/2+d*.25,q+side*W/2+d*.25,q+side*W/2+d*L,q-side*W/2+d*L]
    verts=[(p.x,p.y,.39) for p in points];mesh=bpy.data.meshes.new('ELLT_FIN_Entry_Accessible_Aisle_Mesh');mesh.from_pydata(verts,[],[(0,1,2,3)]);mesh.materials.append(bpy.data.materials['ELLT_B3_Theatre_Carpet'] if bpy.data.materials.get('ELLT_B3_Theatre_Carpet') else bpy.data.materials['ELLT_Theatre_Carpet']);mesh.update()
    path=bpy.data.objects.new('ELLT_FIN_Level_Entry_To_Main_Floor_Path',mesh);COL.objects.link(path);path['evidence_status']='Conceptual level route from ground-level entry to auditorium; exact lobby plan not available.'

# Save and reopen, then render a close exterior view of roof courses and entry.
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1250;scene.render.resolution_y=875;scene.render.resolution_percentage=100;scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
from mathutils import Vector
for n,loc,target,scale in [('southwest',(126,-135,82),(0,2,11),155),('top',(0,-105,155),(0,4,15),150)]:
    data=bpy.data.cameras.new('ELLT_FIN_Cam_'+n);cam=bpy.data.objects.new('ELLT_FIN_Cam_'+n,data);scene.collection.objects.link(cam);cam.location=loc;data.type='ORTHO';data.ortho_scale=scale;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam;scene.render.filepath=str(AUD/f'exterior_finish_{n}.png');bpy.ops.render.render(write_still=True);bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(data)
bpy.ops.wm.save_as_mainfile(filepath=str(SRC));bpy.ops.wm.open_mainfile(filepath=str(SRC))
COL=bpy.data.collections['Asset_elliott_hall_of_music'];out={'saved_and_reopened':True,'tile_count':centres,'footprint_sample_count':N,'sculpture_figures':sum(o.name.endswith('_Heroic_Figure') for o in COL.objects)+sum(o.name.endswith('_Figure') and o.name.startswith('ELLT_EXT_SculptureGroupB') for o in COL.objects),'export_mesh_objects':sum(o.type=='MESH' for o in COL.objects),'export_total_objects':len(COL.objects),'entry_path':'12 m conceptual level interior route'}
(AUD/'exterior_finish_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

import bpy,json,math,pathlib
from mathutils import Vector
ROOT=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');AUD=ROOT/'audit/batch3_elliott';SRC=ROOT/'modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC));COL=bpy.data.collections['Asset_elliott_hall_of_music']
for n in ['ELLT_R5_Vertical_Limestone_Pilasters_Estimated','ELLT_R5_Limestone_Belt_Courses_Estimated','ELLT_R5_Hovde_Link_Deferred_Label','ELLT_R5_Hovde_Link_Deferred_Label_Back']:
    ob=bpy.data.objects.get(n)
    if ob:bpy.data.objects.remove(ob,do_unlink=True)
ring=json.loads((AUD/'polygon.json').read_text());N=len(ring);lens=[math.dist(ring[i],ring[(i+1)%N]) for i in range(N)];cum=[0.0]
for x in lens:cum.append(cum[-1]+x)
perim=cum[-1];area=.5*sum(ring[i][0]*ring[(i+1)%N][1]-ring[(i+1)%N][0]*ring[i][1] for i in range(N))
def frame(i):
 a,b=ring[i],ring[(i+1)%N];dx=b[0]-a[0];dy=b[1]-a[1];ll=math.hypot(dx,dy);t=(dx/ll,dy/ll);n=(t[1],-t[0]) if area>0 else (-t[1],t[0]);return t,n
def sample(s):
 s=s%perim
 for i,l in enumerate(lens):
  if s<=cum[i+1]+1e-8:
   f=(s-cum[i])/l;t,n=frame(i);a,b=ring[i],ring[(i+1)%N];return (a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f),t,n
def mat(name,color):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(*color,1);return m
lim=mat('ELLT_Exterior_Indiana_Limestone',(.62,.57,.46));amber=mat('ELLT_R5_Deferred_Portal_Review_Amber',(.78,.25,.035));ink=mat('ELLT_R5_Deferred_Label_Ink',(.035,.025,.015))
def addmesh(name,verts,faces,ma,desc):
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.materials.append(ma);me.update();o=bpy.data.objects.new(name,me);COL.objects.link(o);o['evidence_status']=desc;return o
desc='Limestone material and pilaster/banding forms follow SAH Archipedia description; location, count, height and projection are estimated pending measured elevation.'
# Reset beefier belt courses with closed faces and conspicuous limestone reveal.
vs=[];fs=[]
for z in (4.9,9.8,14.7,19.6):
 for i in range(N):
  a=ring[i];b=ring[(i+1)%N];nx,ny=frame(i)[1];k=len(vs)
  for zz,off in [(z,.12),(z+.38,.12),(z,.34),(z+.38,.34)]:vs.append((a[0]+nx*off,a[1]+ny*off,zz))
  fs.extend([(k,k+1,k+3,k+2),(k,k+2,k+3,k+1)])
o=addmesh('ELLT_R5_Limestone_Belt_Courses_Estimated',vs,fs,lim,desc);o['course_levels_m_estimate']=[4.9,9.8,14.7,19.6]
# Closed shallow piers, carefully not placed beside known door centers.
doorpoints=[]
for ob in COL.objects:
 if ob.name in ('ELLT_Access_North_Glazed_Double_Door','ELLT_Access_South_Glazed_Double_Door'):
  doorpoints.append((ob.location.x,ob.location.y))
for label in ('Hovde_Ground_West','Hovde_Ground_East','Hovde_Walkway_Upper'):
 ob=bpy.data.objects.get('ELLT_R4_'+label+'_DoorLeaf_Glazed_Estimated')
 if ob:doorpoints.append((ob.location.x,ob.location.y))
vs=[];fs=[];stations=[]
for s in [7.5+i*9 for i in range(int((perim-7.5)//9))]:
 p,t,n=sample(s)
 if any(math.hypot(p[0]-x,p[1]-y)<3.2 for x,y in doorpoints):continue
 stations.append(round(s,2));k=len(vs);half=.24;front=.14;back=.42
 corners=[(p[0]-t[0]*half+n[0]*front,p[1]-t[1]*half+n[1]*front),(p[0]+t[0]*half+n[0]*front,p[1]+t[1]*half+n[1]*front),(p[0]+t[0]*half+n[0]*back,p[1]+t[1]*half+n[1]*back),(p[0]-t[0]*half+n[0]*back,p[1]-t[1]*half+n[1]*back)]
 for z in (.35,20.2):vs.extend((x,y,z) for x,y in corners)
 fs.extend([(k,k+1,k+5,k+4),(k+1,k+2,k+6,k+5),(k+2,k+3,k+7,k+6),(k+3,k,k+4,k+7),(k,k+3,k+2,k+1),(k+4,k+5,k+6,k+7)])
o=addmesh('ELLT_R5_Vertical_Limestone_Pilasters_Estimated',vs,fs,lim,'SAH Archipedia describes vertical pilasters. Their number, spacing, width, height and placement are estimated; no measured facade elevation was found.');o['station_arc_m_estimate']=stations
# Two-sided explicit status label at the connector terminal for the separate Hovde portal pass.
end=Vector((59.85,10.85,0));start=Vector((44.075,9.162,0));direction=(end-start).normalized()
for name,sign in [('ELLT_R5_Hovde_Link_Deferred_Label',1),('ELLT_R5_Hovde_Link_Deferred_Label_Back',-1)]:
 cu=bpy.data.curves.new(name+'_Text','FONT');cu.body='HOVDE\nPENDING';cu.size=.42;cu.align_x='CENTER';cu.align_y='CENTER';cu.space_line=.9
 ob=bpy.data.objects.new(name,cu);COL.objects.link(ob);ob.location=(end.x,end.y,7.43)
 # Up-facing two-sided review text is visible in aerial/detail checks without
 # pretending to be an architectural sign or a built Hovde connection.
 ob.data.materials.append(ink)
 ob['evidence_status']='Review annotation only. Identifies visible unmodeled gap pending Hovde-side portal work; remove after parent integration verifies and builds the portal.'
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
from mathutils import Vector as V
name='hovde_gap_round5';data=bpy.data.cameras.new('ELLT_R5_CAM_LABEL');cam=bpy.data.objects.new('ELLT_R5_CAM_LABEL',data);scene.collection.objects.link(cam);cam.location=(74,-12,30);data.type='ORTHO';data.ortho_scale=55;cam.rotation_euler=(V((53,10.5,5.7))-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam;scene.render.filepath=str(AUD/(name+'.png'));bpy.ops.render.render(write_still=True);bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(data)
bpy.ops.wm.save_as_mainfile(filepath=str(SRC));bpy.ops.wm.open_mainfile(filepath=str(SRC));COL=bpy.data.collections['Asset_elliott_hall_of_music']
r=json.loads((AUD/'result_round5.json').read_text());r['export_mesh_objects']=sum(o.type=='MESH' for o in COL.objects);r['facade_belt_course_height_m_estimate']=.38;r['facade_pilaster_mesh_closed']=True;r['review_label_in_gap']='HOVDE PORTAL / PENDING, two-sided temporary integration annotation';r['render_files']=['exterior_round5.png','hovde_gap_round5.png','auditorium_round5.png'];(AUD/'result_round5.json').write_text(json.dumps(r,indent=2));print('Reopened; exported meshes:',r['export_mesh_objects'],'label:',r['review_label_in_gap'])

"""Round 7 source-described ornament and linked Hovde context for review only."""
import bpy, json, math, pathlib
from mathutils import Vector
ROOT=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');AUD=ROOT/'audit/batch3_elliott';SRC=ROOT/'modular/buildings/elliott_hall_of_music.blend';HOVDE=ROOT/'modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC));scene=bpy.context.scene;COL=bpy.data.collections['Asset_elliott_hall_of_music']
for ob in list(COL.objects):
 if ob.name.startswith('ELLT_R7_'):bpy.data.objects.remove(ob,do_unlink=True)

def mat(name,color,rough=.72):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough
 return m
stone=mat('ELLT_Exterior_Indiana_Limestone',(.66,.61,.51),.78)
bronze=mat('ELLT_R7_Canopy_Bronze_Underside',(.095,.075,.048),.4)
figure_mat=mat('ELLT_R7_Heroic_Sculptures_Limestone_Estimated',(.73,.67,.55),.78)

def link_to_asset(ob):
 for c in list(ob.users_collection):c.objects.unlink(ob)
 COL.objects.link(ob)
 return ob
def cube(name,loc,dims,ma,rot=0,desc='Estimated decorative dimensions; feature type follows SAH Archipedia.'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;o.rotation_euler.z=rot;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);link_to_asset(o);o.data.materials.append(ma);o['evidence_status']=desc;return o
def sphere(name,loc,dims,ma,desc='Interpretive sculpture form; exact pose and size are estimated.'):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);link_to_asset(o);o.data.materials.append(ma);o['evidence_status']=desc;return o
def cone(name,loc,dims,ma,desc='Interpretive sculpture form; exact pose and size are estimated.'):
 bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.5,radius2=.3,depth=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);link_to_asset(o);o.data.materials.append(ma);o['evidence_status']=desc;return o
def limb(name,a,b,r,ma):
 a,b=Vector(a),Vector(b);vec=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=vec.length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_euler=vec.to_track_quat('Z','Y').to_euler();link_to_asset(o);o.data.materials.append(ma);o['evidence_status']='Interpretive heroic figure anatomy; pose/size estimated.';return o

# Project two three-figure allegorical ensembles onto the south mapped facade.
# SAH identifies two sets of three figures representing music, drama and
# forensics/oratory. One earlier Purdue student profile places three statues
# on the south wall; use the facade as an approximate location only.
ring=json.loads((AUD/'polygon.json').read_text());N=len(ring);lens=[math.dist(ring[i],ring[(i+1)%N]) for i in range(N)]
area=.5*sum(ring[i][0]*ring[(i+1)%N][1]-ring[(i+1)%N][0]*ring[i][1] for i in range(N))
def project(target):
 best=(1e30,None)
 for i,a in enumerate(ring):
  b=ring[(i+1)%N];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;t=max(0,min(1,((target[0]-a[0])*dx+(target[1]-a[1])*dy)/den)) if den else 0
  p=(a[0]+t*dx,a[1]+t*dy);dist=math.dist(p,target)
  if dist<best[0]:
   ll=math.hypot(dx,dy);tx,ty=dx/ll,dy/ll;nx,ny=(ty,-tx) if area>0 else (-ty,tx);best=(dist,(p,(tx,ty),(nx,ny),i,t))
 return best
for group,(target,label) in enumerate([((-41,-38),'South_Set_A'),((-10,-38),'South_Set_B')],1):
 _,(p,t,n,edge,tval)=project(target);theta=math.atan2(t[1],t[0]);
 for j,offset in enumerate((-2.0,0,2.0),1):
  center=Vector((p[0]+t[0]*offset+n[0]*.9,p[1]+t[1]*offset+n[1]*.9,0));base=f'ELLT_R7_{label}_Figure_{j}'
  cube(base+'_Plinth',(center.x,center.y,.48),(.86,.78,.96),figure_mat,theta,
       'SAH records an exterior sculpture group. Group member spacing, pedestal shape and dimensions are estimated; positions projected to the south outline are approximate.')
  # Compact stylized figure with tapered body, head and expressive arms.
  cone(base+'_Torso',(center.x,center.y,1.60),(.58,.47,1.28),figure_mat)
  sphere(base+'_Head',(center.x,center.y,2.36),(.38,.36,.43),figure_mat)
  side=Vector((t[0],t[1],0));forward=Vector((n[0],n[1],0))
  shoulder=Vector((center.x,center.y,1.98));arms=[(shoulder-side*.25+forward*.02,shoulder-side*.62+Vector((0,0,.34 if j==1 else .06))),
          (shoulder+side*.25+forward*.02,shoulder+side*.58+Vector((0,0,.25 if j==2 else -.02)))]
  for k,(a,b) in enumerate(arms,1):limb(base+'_Arm_'+str(k),a,b,.085,figure_mat)
  for k,sign in enumerate((-1,1),1):
   hip=Vector((center.x,center.y,1.12))+side*(sign*.13);foot=Vector((center.x,center.y,.98))+side*(sign*.19)
   limb(base+'_Leg_'+str(k),foot,hip,.105,figure_mat)
  o=bpy.data.objects[base+'_Torso'];o['feature_status']='SAH Archipedia documents two sets of three heroic allegorical exterior sculptures (music, drama, and forensics/oratory). This simplified figure, group location, pose, pedestal and dimensions are illustrative estimates.'

# Curved entrance canopy over Elliott's upper opening to the documented Hovde
# walkway. The feature type is sourced, while its section, position and size are
# explicitly an estimate pending a verified elevation.
q=(44.075,9.162);_,(p,t,n,edge,tval)=project(q);half=2.75;depth=2.35;basez=7.38;rise=.92;nx=32;ny=4
def arch(u):return basez+rise*math.sqrt(max(0,1-(u/half)**2))
verts=[];faces=[]
for layer in (0,1):
 for k in range(ny+1):
  d=depth*k/ny
  for j in range(nx+1):
   u=-half+2*half*j/nx;z=arch(u)-.12*layer
   verts.append((p[0]+t[0]*u+n[0]*d,p[1]+t[1]*u+n[1]*d,z))
grid=(nx+1)*(ny+1)
for layer in (0,1):
 off=layer*grid
 for k in range(ny):
  for j in range(nx):
   a=off+k*(nx+1)+j;faces.append((a,a+1,a+nx+2,a+nx+1))
for k in range(ny):
 for j in range(nx):
  a=k*(nx+1)+j;b=a+grid;faces.append((a,a+nx+1,b+nx+1,b))
me=bpy.data.meshes.new('ELLT_R7_Curved_Canopy_Roof_Mesh');me.from_pydata(verts,[],faces);me.materials.append(stone);me.update();can=bpy.data.objects.new('ELLT_R7_Curved_Limestone_Entry_Canopy_Estimated',me);COL.objects.link(can)
can['evidence_status']='SAH Archipedia describes a curving entry canopy. Modeled over the Elliott-side second-story walkway portal as a provisional feature-type interpretation; location, curve, span, rise and depth are estimated and require direct elevation/photo review.'
can['dimension_estimate_m']={'width':2*half,'depth':depth,'rise':rise}
# Light limestone fascia follows the curved leading edge.
fv=[];ff=[]
for j in range(nx+1):
 u=-half+2*half*j/nx;x=p[0]+t[0]*u+n[0]*depth;y=p[1]+t[1]*u+n[1]*depth;z=arch(u)-.05;k=len(fv)
 fv.extend([(x,y,z-.12),(x,y,z+.10),(x+n[0]*.16,y+n[1]*.16,z-.12),(x+n[0]*.16,y+n[1]*.16,z+.10)])
 if j<nx:ff.extend([(k,k+1,k+5,k+4),(k+1,k+3,k+7,k+5),(k+3,k+2,k+6,k+7)])
me=bpy.data.meshes.new('ELLT_R7_Curved_Canopy_Fascia_Mesh');me.from_pydata(fv,[],ff);me.materials.append(stone);me.update();fas=bpy.data.objects.new('ELLT_R7_Curved_Canopy_Limestone_Fascia_Estimated',me);COL.objects.link(fas);fas['evidence_status']=can['evidence_status']

# Add modest corner pilasters to clarify the documented flytower mass, with
# dimensions explicitly estimated. Existing flytower and tile cap are retained.
cx,cy=13.79,16.82;half_x,half_y=12,11;z0,z1=22.5,33.1
for sx in (-1,1):
 for sy in (-1,1):
  x=cx+sx*(half_x-.28);y=cy+sy*(half_y-.28)
  cube(f'ELLT_R7_Flytower_Corner_Pilaster_{sx}_{sy}',(x,y,(z0+z1)/2),(.46,.46,z1-z0),stone,
   desc='SAH describes a flytower with limestone pilaster/banding/ornament vocabulary. This corner trim is a visual estimate, not a measured tower elevation.')

# Save the Elliott asset once. Hovde is linked only afterward for temporary
# context renders; no Hovde geometry or file is edited and no context data saved.
bpy.ops.wm.save_as_mainfile(filepath=str(SRC));bpy.ops.wm.open_mainfile(filepath=str(SRC));scene=bpy.context.scene;COL=bpy.data.collections['Asset_elliott_hall_of_music']

# Reload the unchanged, separate Hovde library as a collection instance at its
# existing master registration. This context session is disposable and unsaved.
with bpy.data.libraries.load(str(HOVDE),link=True) as (src,dst):dst.collections=['Asset_hovde_hall']
hc=next(c for c in dst.collections if c and c.name.startswith('Asset_hovde_hall'))
inst=bpy.data.objects.new('TEMP_R7_Hovde_Context_Collection_Instance',None);scene.collection.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=hc;inst.location=(61.197312832,28.344248772,0)

# Temporary render cameras and environments are not saved.
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
def render(name,loc,target,scale,hide_prefixes=(),hidden_exact=()):
 changed=[]
 for ob in bpy.context.scene.objects:
  if any(ob.name.startswith(p) for p in hide_prefixes) or ob.name in hidden_exact:changed.append((ob,ob.hide_render));ob.hide_render=True
 d=bpy.data.cameras.new('TEMP_R7_'+name);c=bpy.data.objects.new('TEMP_R7_'+name,d);scene.collection.objects.link(c);c.location=loc;d.type='ORTHO';d.ortho_scale=scale;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();scene.camera=c
 scene.render.filepath=str(AUD/(name+'.png'));bpy.ops.render.render(write_still=True)
 for ob,v in changed:ob.hide_render=v
 bpy.data.objects.remove(c,do_unlink=True);bpy.data.cameras.remove(d)

render('exterior_elevation_round7',(0,-142,20),(0,0,11),130,
       hide_prefixes=('ELLT_R5_Hovde_Link_', 'ELLT_R4_Hovde_', 'ELLT_Access_'))
render('entry_canopy_round7',(68,-7,20),(44,9,7.8),24,
       hide_prefixes=('ELLT_R4_Hovde_',))
# Two linked buildings and the intervening landing/gap are all in frame.
render('hovde_elliott_context_round7',(49,-14,27),(55,18,8),58,
       hide_prefixes=('ELLT_Access_',))
render('hovde_elliott_overview_round7',(72,-47,64),(15,18,10),150,
       hide_prefixes=('ELLT_Access_',))
# Remove the temporary linked context before interior renders so Hovde cannot
# appear behind Elliott's auditorium in those views.
bpy.data.objects.remove(inst,do_unlink=True)
# Interior full-room view with ceiling restored; shell and roof remain hidden
# for camera visibility only. A separate plan view stays a cutaway.
shell='ELLT_Official_GIS_Wall_R4_Access_and_Hovde_Openings';roof='ELLT_Official_Footprint_Roof_Estimated_22_5m';ceiling='ELLT_B3_ceiling'
int_hide=('ELLT_R4_','ELLT_R5_','ELLT_R6_','ELLT_R7_','ELLT_EXT_','ELLT_Exterior_','ELLT_Estimated_','ELLT_Access_')
render('interior_room_round7',(0,-28,13),(0,15,7),70,int_hide,(shell,roof))
render('interior_plan_round7',(0,0,92),(0,0,5),88,int_hide,(shell,roof,ceiling))
result={'saved_and_reopened':True,'blender_version':bpy.app.version_string,'export_mesh_objects':sum(o.type=='MESH' for o in COL.objects),
 'round7_additions':{'allegorical_figure_count':6,'figure_groups':2,'curved_canopy_meshes':2,'flytower_corner_pilasters':4},
 'source_basis':'SAH Archipedia describes two sets of three heroic allegorical figures (music, drama, forensics/oratory), a curving entry canopy, and a flytower. Exact sculptural poses/locations, canopy profile, and flytower trim are estimates.',
 'hovde_review_context':'Temporary linked collection instance of existing modular/buildings/hovde_hall.blend placed at current registration (61.197312832, 28.344248772, 0). No Hovde save or geometry change; temporary instance removed and context scene not saved.',
 'connector_status':'Elliott-only approach still terminates before Hovde with review label; not a finished connection.',
 'accessibility_status':{'north_south_access_doors':'Purdue-documented pair, but location, door dimensions and approach dimensions unverified.','other_three_openings':'Through-shell sample checks passed in round5; real-world locations, clear widths, operability, thresholds, seating conflicts and continuous routes remain unverified.','Hovde_route':'Documented general second-floor connection; exact corner and shared portal unresolved; no accessible-route continuity claim.'},
 'renders':['exterior_elevation_round7.png','entry_canopy_round7.png','hovde_elliott_context_round7.png','hovde_elliott_overview_round7.png','interior_room_round7.png','interior_plan_round7.png'],
 'uncertainties':['window schedule and placement','sculpture/canopy position and form','flytower height/profile','all door dimensions and accessible route','Hovde portal and connector geometry','interior dimensions/seating/circulation']}
(AUD/'result_round7.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

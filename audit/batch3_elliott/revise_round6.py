"""Repair Elliott belt course mesh, add brick bond shader, render interior and detail views."""
import bpy,json,math,pathlib
from mathutils import Vector
ROOT=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');AUD=ROOT/'audit/batch3_elliott';SRC=ROOT/'modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC));scene=bpy.context.scene;COL=bpy.data.collections['Asset_elliott_hall_of_music']
wall=bpy.data.objects['ELLT_Official_GIS_Wall_R4_Access_and_Hovde_Openings']
ring=json.loads((AUD/'polygon.json').read_text());N=len(ring);lens=[math.dist(ring[i],ring[(i+1)%N]) for i in range(N)]
area=.5*sum(ring[i][0]*ring[(i+1)%N][1]-ring[(i+1)%N][0]*ring[i][1] for i in range(N))

# Correct the previous malformed courses: continuous rectangular belts follow
# the full length of every footprint edge, not isolated marks at vertices.
old=bpy.data.objects.get('ELLT_R5_Limestone_Belt_Courses_Estimated')
if old:bpy.data.objects.remove(old,do_unlink=True)
lim=bpy.data.materials['ELLT_Exterior_Indiana_Limestone']
verts=[];faces=[]
for z in (4.9,9.8,14.7,19.6):
 for i in range(N):
  a,b=ring[i],ring[(i+1)%N];dx=b[0]-a[0];dy=b[1]-a[1];ll=math.hypot(dx,dy);tx,ty=dx/ll,dy/ll
  nx,ny=(ty,-tx) if area>0 else (-ty,tx)
  k=len(verts);h=.56;outer=.50;inner=.12
  for p,off,zz in [(a,outer,z),(b,outer,z),(b,outer,z+h),(a,outer,z+h),
                   (a,inner,z),(b,inner,z),(b,inner,z+h),(a,inner,z+h)]:
   verts.append((p[0]+nx*off,p[1]+ny*off,zz))
  faces.extend([(k,k+1,k+2,k+3),(k+4,k+7,k+6,k+5),(k,k+4,k+5,k+1),
                (k+1,k+5,k+6,k+2),(k+2,k+6,k+7,k+3),(k+3,k+7,k+4,k)])
me=bpy.data.meshes.new('ELLT_R6_Continuous_Limestone_Belts_Mesh');me.from_pydata(verts,[],faces);me.materials.append(lim);me.update()
belts=bpy.data.objects.new('ELLT_R6_Continuous_Limestone_Belt_Courses_Estimated',me);COL.objects.link(belts)
belts['evidence_status']='SAH Archipedia describes Indiana limestone banding. These full-perimeter horizontal belts make that feature legible. Four elevations, 0.56 m face height, and 0.50 m projection are visual estimates; no measured elevation was found.'
belts['levels_m_estimate']=[4.9,9.8,14.7,19.6]

# Replace flat noise-only facade color with an approximate meter-scale brick
# bond and shallow mortar relief. The material family is sourced; bond module
# and color variation are visual estimates, not an exact masonry specification.
brick=wall.data.materials[0];brick.name='ELLT_Exterior_Red_Brick_Bond_Estimated'
nt=brick.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
coord=next((n for n in nt.nodes if n.type=='TEX_COORD'),None) or nt.nodes.new('ShaderNodeTexCoord')
bricktex=nt.nodes.new('ShaderNodeTexBrick');bricktex.name='Estimated_250x70mm_Brick_Bond'
bricktex.inputs['Scale'].default_value=3.7
bricktex.inputs['Brick Width'].default_value=.93
bricktex.inputs['Row Height'].default_value=.26
bricktex.inputs['Mortar Size'].default_value=.018
bricktex.inputs['Mortar Smooth'].default_value=.12
bricktex.inputs['Color1'].default_value=(.40,.095,.055,1)
bricktex.inputs['Color2'].default_value=(.53,.16,.105,1)
bricktex.inputs['Mortar'].default_value=(.19,.12,.085,1)
# Map each facade face by perimeter distance and elevation so bricks stay
# horizontal on all bearings of the rounded footprint.
uv=wall.data.uv_layers.get('FacadeCourseUV') or wall.data.uv_layers.new(name='FacadeCourseUV')
seg=[math.dist(ring[i],ring[(i+1)%N]) for i in range(N)];arc=[0.0]
for d in seg:arc.append(arc[-1]+d)
def closest_edge(x,y):
 best=(1e30,0)
 for i,a in enumerate(ring):
  b=ring[(i+1)%N];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy
  t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/den)) if den else 0
  dist=(x-(a[0]+dx*t))**2+(y-(a[1]+dy*t))**2
  if dist<best[0]:best=(dist,i)
 return best[1]
for poly in wall.data.polygons:
 xy=[wall.data.vertices[wall.data.loops[li].vertex_index].co for li in poly.loop_indices]
 edge=closest_edge(sum(v.x for v in xy)/len(xy),sum(v.y for v in xy)/len(xy));a,b=ring[edge],ring[(edge+1)%N]
 dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
 for li,v in zip(poly.loop_indices,xy):
  t=max(0,min(1,((v.x-a[0])*dx+(v.y-a[1])*dy)/den)) if den else 0
  uv.data[li].uv=(arc[edge]+t*seg[edge],v.z)
uvnode=nt.nodes.new('ShaderNodeUVMap');uvnode.uv_map='FacadeCourseUV'
nt.links.new(uvnode.outputs['UV'],bricktex.inputs['Vector'])
nt.links.new(bricktex.outputs['Color'],bs.inputs['Base Color'])
bump=next((n for n in nt.nodes if n.type=='BUMP'),None) or nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.26;bump.inputs['Distance'].default_value=.008
nt.links.new(bricktex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
wall['texture_status']='Purdue/SAH support red brick; procedural Brick Texture suggests 0.25 x 0.07 m units and mortar relief for readability. Actual brick size, bond, and color schedule are unverified.'

# Make the deliberately deferred endpoint annotation readable in the detail view.
for n in ('ELLT_R5_Hovde_Link_Deferred_Label','ELLT_R5_Hovde_Link_Deferred_Label_Back'):
 ob=bpy.data.objects.get(n)
 if ob and ob.type=='FONT':
  ob.data.body='HOVDE\nPORTAL PENDING';ob.data.size=.36;ob.data.align_x='CENTER';ob.data.align_y='CENTER';ob.location.z=7.48

# Exterior elevation/detail render with shader materials enabled.
scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=24
scene.view_settings.view_transform='AgX'
world=bpy.data.worlds.get('ELLT_R6_Render_World') or bpy.data.worlds.new('ELLT_R6_Render_World');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.17,.19,.21,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7;scene.world=world
light_data=bpy.data.lights.new('ELLT_R6_Sun','SUN');light_data.energy=2.5
light=bpy.data.objects.new('ELLT_R6_Sun',light_data);scene.collection.objects.link(light);light.rotation_euler=(math.radians(24),math.radians(-30),math.radians(-28))
def render(name,loc,target,scale,hide_prefixes=(),hidden_exact=()):
 changed=[]
 for ob in scene.objects:
  if any(ob.name.startswith(p) for p in hide_prefixes) or ob.name in hidden_exact:
   changed.append((ob,ob.hide_render));ob.hide_render=True
 camdata=bpy.data.cameras.new('ELLT_R6_Camera_'+name);cam=bpy.data.objects.new('ELLT_R6_Camera_'+name,camdata);scene.collection.objects.link(cam)
 cam.location=loc;camdata.type='ORTHO';camdata.ortho_scale=scale;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
 scene.render.filepath=str(AUD/(name+'.png'));bpy.ops.render.render(write_still=True)
 for ob,val in changed:ob.hide_render=val
 bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(camdata)

render('exterior_elevation_round6',(0,-142,16),(0,0,10),130,
       hide_prefixes=('ELLT_R5_Hovde_Link_', 'ELLT_R4_Hovde_', 'ELLT_Access_'))
render('hovde_gap_round6',(73,-8,27),(59.6,10.8,6.2),27,
       hide_prefixes=('ELLT_R4_Hovde_',))

# A clean, genuinely interior stage-to-seating view. Exterior shell/roof are
# hidden for this render only and restored immediately; no render-only flags
# are written into the source asset.
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
scene.display.shading.background_type='WORLD'
render('interior_round6',(27,-4,13),(-18,0,7),60,
       hide_prefixes=('ELLT_R5_','ELLT_R4_','ELLT_EXT_','ELLT_Access_','ELLT_Exterior_','ELLT_Estimated_'),
       hidden_exact=('ELLT_Official_GIS_Wall_R4_Access_and_Hovde_Openings','ELLT_Official_Footprint_Roof_Estimated_22_5m','ELLT_B3_ceiling','ELLT_Estimated_Raised_Clay_Tile_Courses'))
# Plan render of the seats with the same outer shell and roof excluded.
render('interior_plan_round6',(0,0,95),(0,0,5),72,
       hide_prefixes=('ELLT_R5_','ELLT_R4_','ELLT_EXT_','ELLT_Access_','ELLT_Exterior_','ELLT_Estimated_'),
       hidden_exact=('ELLT_Official_GIS_Wall_R4_Access_and_Hovde_Openings','ELLT_Official_Footprint_Roof_Estimated_22_5m','ELLT_B3_ceiling','ELLT_Estimated_Raised_Clay_Tile_Courses'))

# Persist geometry/material changes but keep all working render visibility restored.
bpy.ops.wm.save_as_mainfile(filepath=str(SRC));bpy.ops.wm.open_mainfile(filepath=str(SRC))
COL=bpy.data.collections['Asset_elliott_hall_of_music']
result={'saved_and_reopened':True,'blender_version':bpy.app.version_string,'export_collection':'Asset_elliott_hall_of_music',
 'export_mesh_objects':sum(o.type=='MESH' for o in COL.objects),'continuous_limestone_courses':4,
 'course_face_height_m_estimate':.56,'course_projection_m_estimate':.50,
 'brick_texture':'Procedural staggered brick/mortar pattern; 0.25 x 0.07 m nominal units estimated, not measured.',
 'interior_views':['interior_round6.png','interior_plan_round6.png'],
 'exterior_views':['exterior_elevation_round6.png','hovde_gap_round6.png'],
 'hovde_connection':'Still deferred; no Hovde-side geometry edited. Review-only visible gap marker remains.',
 'uncertainties':['Facade window count/positions','exact brick size/bond/color','limestone course/pilaster layout','five opening positions/sizes','Hovde endpoint and bridge geometry','interior plan dimensions/seating/circulation','vertical envelope dimensions']}
(AUD/'result_round6.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

import bpy, json
from pathlib import Path
from mathutils import Vector
base=Path(r'audit/batch3_stanley').resolve()
bpy.ops.wm.open_mainfile(filepath=str(Path(r'modular/buildings/stanley_coulter_hall.blend').resolve()))
s=bpy.context.scene
for o in list(bpy.data.objects): o.hide_render=True
source=json.loads((base/'source_gis_fid56_r3.json').read_text(encoding='utf-8'))
asset=json.loads((base/'asset_foundation_vertices_r3.json').read_text(encoding='utf-8'))
origin=asset['placement_origin_xy_m'];ring=source['feature']['rings_xy_m'][0][:-1]
gis=[(p[0]-origin[0],p[1]-origin[1],0.10) for p in ring]
low=min(v['local_xyz_m'][2] for v in asset['vertices'])
plinth=[(v['local_xyz_m'][0],v['local_xyz_m'][1],0.24) for v in asset['vertices'] if abs(v['local_xyz_m'][2]-low)<1e-5]
def emission(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True;ns=m.node_tree.nodes;ns.clear();em=ns.new('ShaderNodeEmission');em.inputs['Color'].default_value=color;out=ns.new('ShaderNodeOutputMaterial');m.node_tree.links.new(em.outputs[0],out.inputs['Surface']);return m
def line(name,pts,mat,bevel):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=bevel;c.bevel_resolution=2
 sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
 for a,p in zip(sp.points,pts):a.co=(*p,1)
 sp.use_cyclic_u=True;o=bpy.data.objects.new(name,c);s.collection.objects.link(o);c.materials.append(mat);o.hide_render=False;return o
gold=emission('Official GIS amber',(0.98,0.43,0.055,1));cyan=emission('Foundation cyan',(0.0,0.60,0.72,1));ink=emission('Overlay label ink',(0.04,0.07,0.10,1))
line('FID56 official full foundation ring',gis,gold,0.11)
# Draw the matching asset outline as short cyan dashes above the GIS stroke so the near-exact overlap remains visible.
def dashed_segments(points,step=1.1,gap=0.45):
 segs=[]
 for idx,a in enumerate(points):
  b=points[(idx+1)%len(points)];dx=b[0]-a[0];dy=b[1]-a[1];length=(dx*dx+dy*dy)**0.5;d=0.0
  while d<length:
   e=min(d+step,length);p0=(a[0]+dx*d/length,a[1]+dy*d/length,0.24);p1=(a[0]+dx*e/length,a[1]+dy*e/length,0.24);segs.append((p0,p1));d=e+gap
 return segs
for i,(a,b) in enumerate(dashed_segments(plinth)):
 c=bpy.data.curves.new(f'Asset dashed outline {i}','CURVE');c.dimensions='3D';c.bevel_depth=0.065;c.bevel_resolution=2;sp=c.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1);o=bpy.data.objects.new(f'Asset outline dash {i}',c);s.collection.objects.link(o);c.materials.append(cyan);o.hide_render=False
def label(body,loc,size):
 cu=bpy.data.curves.new('Label '+body,'FONT');cu.body=body;cu.size=size;cu.extrude=0.0;o=bpy.data.objects.new('Label '+body,cu);s.collection.objects.link(o);o.location=loc;cu.materials.append(ink);o.hide_render=False
label('FID 56  |  STANLEY COULTER HALL  |  FULL PLAN OUTLINE',(-27,-30,0.22),1.20)
label('AMBER: OFFICIAL PURDUE GIS    CYAN DASHES: ASSET FOUNDATION',(-26,-32,0.22),0.82)
# North arrow and scale bar communicate orientation and approximate project metres.
line('North arrow shaft',[(-31,21,0.18),(-31,26,0.18)],ink,0.09);line('North arrow head left',[(-31,26,0.18),(-31.8,24.5,0.18)],ink,0.09);line('North arrow head right',[(-31,26,0.18),(-30.2,24.5,0.18)],ink,0.09);label('N',(-31.6,27,0.2),1.2)
line('10m scale',[(17,-31,0.18),(27,-31,0.18)],ink,0.08);line('scale left tick',[(17,-31.5,0.18),(17,-30.5,0.18)],ink,0.08);line('scale right tick',[(27,-31.5,0.18),(27,-30.5,0.18)],ink,0.08);label('10 m',(20,-33,0.2),0.9)
camdata=bpy.data.cameras.new('R3_Footprint_Overlay_Camera');cam=bpy.data.objects.new('R3_Footprint_Overlay_Camera',camdata);s.collection.objects.link(cam);cam.location=(0,0,100);cam.rotation_euler=(0,0,0);camdata.type='ORTHO';camdata.ortho_scale=68;s.camera=cam
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.film_transparent=False;s.world.color=(0.88,0.90,0.92);s.render.filepath=str(base/'SC_footprint_overlay_r3.png');bpy.ops.render.render(write_still=True)
print('Saved registered full-polygon overlay.')

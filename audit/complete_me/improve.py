import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/complete_me'; c=bpy.data.collections['Asset_mechanical_engineering']
report={'changes':[], 'limitations':['Floor elevations estimated, interior partitions and furniture not reconstructed without measured plans.','Google Maps fetch unavailable; geographic placement relies on cached official GIS.','Exterior openings and wing heights remain unverified.']}
def material(name,color,rough):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;return m
brick=material('ME_MeterMapped_RedBrick',(.28,.095,.045),.8);n=brick.node_tree.nodes;l=brick.node_tree.links;p=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord');b=n.new('ShaderNodeTexBrick');b.inputs['Scale'].default_value=1;b.inputs['Brick Width'].default_value=.215;b.inputs['Row Height'].default_value=.075;b.inputs['Mortar Size'].default_value=.008;b.inputs['Color1'].default_value=(.27,.075,.035,1);b.inputs['Color2'].default_value=(.4,.16,.07,1);b.inputs['Mortar'].default_value=(.32,.29,.24,1);l.new(tc.outputs['UV'],b.inputs['Vector']);l.new(b.outputs['Color'],p.inputs['Base Color']);bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.003;bump.inputs['Strength'].default_value=.25;l.new(b.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
roof=material('ME_Roof_Membrane',(.11,.12,.13),.9);floor=material('ME_Interior_Concrete_Estimated',(.49,.48,.44),.75)
for o in list(c.all_objects):
 if o.type!='MESH':continue
 if 'Structural_Envelope' in o.name:
  o.data.materials.clear();o.data.materials.append(brick)
  uv=o.data.uv_layers.new(name='Meters_Tangent_Z') if not o.data.uv_layers else o.data.uv_layers.active
  for poly in o.data.polygons:
   norm=poly.normal;t=Vector((-norm.y,norm.x,0));t.normalize()
   for li in poly.loop_indices:
    v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v.dot(t),v.z)
  # Save the original filled shell as disabled reference; replace exported solid with inward wall surfaces.
  ref=o.copy();ref.data=o.data.copy();rc=bpy.data.collections.get('ME_Previous_Solid_Reference')
  if not rc:rc=bpy.data.collections.new('ME_Previous_Solid_Reference');bpy.context.scene.collection.children.link(rc);rc.hide_render=True;rc.hide_viewport=True
  rc.objects.link(ref)
  import bmesh
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if abs(f.normal.z)>.5],context='FACES');bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free()
  mod=o.modifiers.new('Inward masonry thickness 280mm estimate','SOLIDIFY');mod.thickness=.28;mod.offset=-1
  o['interior_status']='Hollow exterior with estimated floor slabs; partition plan unverified'
  report['changes'].append(o.name+' hollowed and tangent/vertical meter UV mapped')
 elif '_Roof' in o.name:
  o.data.materials.clear();o.data.materials.append(roof)
  # Reuse exact official roof topology for floor plates. Floor positions are explicitly estimates.
  for z in [0,4.5,9,13.5]:
   fo=o.copy();fo.data=o.data.copy();fo.name=o.name.replace('Roof','Estimated_Floor_'+str(z));c.objects.link(fo)
   for v in fo.data.vertices:v.co.z=z+(v.co.z-18.5)*.8
   fo.data.materials.clear();fo.data.materials.append(floor);fo['accuracy']='estimated slab elevation; official outline only'
  report['changes'].append(o.name+' roof material; four estimated floor slabs')
c['completion_status']='Improved shell and procedural texture; full architectural interior incomplete'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'modular/buildings/mechanical_engineering.blend'))
bpy.ops.wm.open_mainfile(filepath=str(R/'modular/buildings/mechanical_engineering.blend'))
c=bpy.data.collections['Asset_mechanical_engineering'];report['reopened']=True;report['objects']=len(c.all_objects);report['missing_images']=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file];(D/'changes.json').write_text(json.dumps(report,indent=2))
sc=bpy.context.scene;ca=bpy.data.cameras.new('MEReview');cam=bpy.data.objects.new('MEReview',ca);sc.collection.objects.link(cam);cam.location=(150,-170,145);cam.rotation_euler=(Vector((0,0,5))-cam.location).to_track_quat('-Z','Y').to_euler();ca.type='ORTHO';ca.ortho_scale=180;sc.camera=cam;sc.render.engine='BLENDER_EEVEE';sc.world.color=(.5,.5,.5);sunD=bpy.data.lights.new('ReviewSun','SUN');sunD.energy=3;sun=bpy.data.objects.new('ReviewSun',sunD);sc.collection.objects.link(sun);sun.rotation_euler=(.4,-.5,-.4);sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.filepath=str(D/'after.png');bpy.ops.render.render(write_still=True)

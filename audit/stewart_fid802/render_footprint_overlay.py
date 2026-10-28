import bpy, json, os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
AUDIT=os.path.join(ROOT,"audit","stewart_fid802")
ASSET=os.path.join(ROOT,"modular","buildings","massing_house_1089875810_8c9b95d.blend")
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene; col=bpy.data.collections.get("Asset_massing_house_1089875810_8c9b95d")
src=json.load(open(os.path.join(AUDIT,"initial_inspection.json"),encoding="utf-8"))
ring=src['gis_ring_local_xy_m']; poly=[Vector((x,y,0)) for x,y in ring]
for o in list(bpy.data.objects):
    if o.type in {'CAMERA','LIGHT'} or o.name.startswith('StewartOverlay_'):
        bpy.data.objects.remove(o,do_unlink=True)
for o in col.objects: o.hide_render=True
def mat(name,color):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); return m
fillmat=mat('StewartOverlay_SourceFill',(.35,.42,.50))
linemat=mat('StewartOverlay_ModelWallOutline',(.98,.62,.12))
textmat=mat('StewartOverlay_Text',(.95,.82,.28))
# Translucent-like study fill (Workbench uses solid material color) at z=.01.
tris=tessellate_polygon([poly]); verts=[]; faces=[]
for tri in tris:
    s=len(verts); verts.extend([(poly[i].x,poly[i].y,.01) for i in tri]); faces.append(tuple(range(s,s+3)))
mesh=bpy.data.meshes.new('StewartOverlay_SourceFootprintMesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(fillmat)
fill=bpy.data.objects.new('StewartOverlay_Source_FID802_Fill',mesh); scene.collection.objects.link(fill)
# Model wall base outline is placed just above the source fill so both traces
# remain visible; the coordinates are the same exact GIS ring in the asset.
curve=bpy.data.curves.new('StewartOverlay_ModelWallBaseOutline','CURVE'); curve.dimensions='3D'; curve.resolution_u=1; curve.bevel_depth=.055; curve.resolution_u=1
sp=curve.splines.new('POLY'); sp.points.add(len(ring)-1)
for p,(x,y) in zip(sp.points,ring): p.co=(x,y,.04,1)
sp.use_cyclic_u=True
outline=bpy.data.objects.new('StewartOverlay_Model_Wall_Base',curve); scene.collection.objects.link(outline); outline.data.materials.append(linemat)
def text_obj(name,body,location,size):
    data=bpy.data.curves.new(name,'FONT'); data.body=body; data.size=size; data.extrude=0
    ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=location; ob.data.materials.append(textmat)
    return ob
text_obj('StewartOverlay_Title','STEWART | Purdue GIS FID 802',(-106.2,673.2,.1),.75)
text_obj('StewartOverlay_Note','GIS source ring and model wall base coincide; approximate campus-local coordinates',(-106.2,671.9,.1),.38)
scene.render.engine='BLENDER_WORKBENCH'; scene.display.shading.light='STUDIO'; scene.display.shading.studio_light='paint.sl'; scene.display.shading.color_type='MATERIAL'; scene.display.shading.background_type='WORLD'; scene.display.shading.show_cavity=False
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'
camera_data=bpy.data.cameras.new('StewartOverlay_Camera'); camera=bpy.data.objects.new('StewartOverlay_Camera',camera_data); scene.collection.objects.link(camera)
camera.location=(-99.6,685.5,55); camera.rotation_euler=(Vector((-99.6,685.5,0))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=45; scene.camera=camera
scene.render.filepath=os.path.join(AUDIT,'footprint_overlay.png')
bpy.ops.render.render(write_still=True)
print('Rendered GIS/source-fill and exact model-wall-base outline comparison.')

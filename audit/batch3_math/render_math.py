import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
SRC=ROOT/"modular/buildings/math_sciences.blend"
OUT=ROOT/"audit/batch3_math"
bpy.ops.wm.open_mainfile(filepath=str(SRC))
asset=bpy.data.collections["Asset_math_sciences"]

def setup_scene(name):
    sc=bpy.data.scenes.new(name)
    sc.render.engine='CYCLES'; sc.cycles.samples=24
    sc.render.resolution_x=1100; sc.render.resolution_y=1100; sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG'
    sc.view_settings.view_transform='AgX'
    sc.view_settings.look='AgX - Medium High Contrast'
    sc.view_settings.exposure=.8
    sc.world=bpy.data.worlds.new(name+"World")
    sc.world.use_nodes=True
    sc.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.48,.50,.52,1)
    sc.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.75
    return sc
def aim(obj, point):
    obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()
def camera(sc,name,loc,target,ortho):
    d=bpy.data.cameras.new(name); d.type='ORTHO'; d.ortho_scale=ortho
    o=bpy.data.objects.new(name,d); sc.collection.objects.link(o); o.location=loc; aim(o,target); sc.camera=o
def sun(sc,name,loc,target,energy,size):
    d=bpy.data.lights.new(name,'AREA'); d.energy=energy; d.shape='DISK'; d.size=size
    o=bpy.data.objects.new(name,d); sc.collection.objects.link(o); o.location=loc; aim(o,target)

ext=setup_scene('Math Exterior Review')
ext.collection.children.link(asset)
# Directional daylight gives the brick and pale reveals readable, neutral color.
sd=bpy.data.lights.new('MathExteriorSun','SUN'); sd.energy=2.5; sd.angle=.18
so=bpy.data.objects.new('MathExteriorSun',sd); ext.collection.objects.link(so); so.rotation_euler=(.35,-.45,-.5)
fill=bpy.data.lights.new('MathExteriorFill','AREA'); fill.energy=8500; fill.shape='DISK'; fill.size=55
fo=bpy.data.objects.new('MathExteriorFill',fill); ext.collection.objects.link(fo); fo.location=(60,-35,75); aim(fo,(0,0,16))
def plane_mat():
    m=bpy.data.materials.new('Math Exterior Neutral Ground'); m.diffuse_color=(.38,.40,.41,1); m.use_nodes=True
    n=next(x for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED'); n.inputs['Base Color'].default_value=(.38,.40,.41,1); n.inputs['Roughness'].default_value=.9
    return m
groundmesh=bpy.data.meshes.new('MathReviewGroundMesh'); groundmesh.from_pydata([(-150,-150,-.08),(150,-150,-.08),(150,150,-.08),(-150,150,-.08)],[],[(0,1,2,3)])
ground=bpy.data.objects.new('MathReviewGround',groundmesh); ext.collection.objects.link(ground); ground.data.materials.append(plane_mat())
camera(ext,'MathExteriorCamera',(105,-65,48),(0,-2,16.5),84)
ext.render.filepath=str(OUT/'exterior_after.png')
bpy.context.window.scene=ext; bpy.ops.render.render(write_still=True)

# Four orthographic documentation angles make every modeled elevation easy to inspect.
for face,loc,target in [
    ('east',(110,0,41),(0,0,16)),('west',(-110,0,41),(0,0,16)),
    ('north',(0,110,41),(0,0,16)),('south',(0,-110,41),(0,0,16))]:
    sc=bpy.data.scenes.new('Math '+face.title()+' Elevation')
    sc.render.engine='CYCLES'; sc.cycles.samples=12; sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Medium High Contrast'; sc.view_settings.exposure=.8
    sc.world=ext.world; sc.collection.children.link(asset); sc.collection.objects.link(so); sc.collection.objects.link(fo); sc.collection.objects.link(ground)
    sc.render.resolution_x=900; sc.render.resolution_y=900; sc.render.resolution_percentage=100
    camera(sc,'Math_'+face.title()+'_Camera',loc,target,82)
    sc.render.image_settings.file_format='PNG'; sc.render.filepath=str(OUT/f'exterior_{face}_after.png')
    bpy.context.window.scene=sc; bpy.ops.render.render(write_still=True)

# Close neutral-daylight crop verifies the physically sized brick courses,
# mortar, glazing, and limestone reveal without enlarging their scale in the
# campus-distance hero render.
detail=bpy.data.scenes.new('Math East Facade Brick Detail')
detail.render.engine='CYCLES'; detail.cycles.samples=32
detail.view_settings.view_transform='AgX'; detail.view_settings.look='AgX - Medium High Contrast'; detail.view_settings.exposure=.8
detail.world=ext.world; detail.collection.children.link(asset)
detail.collection.objects.link(so); detail.collection.objects.link(fo)
detail.render.resolution_x=1200; detail.render.resolution_y=1200; detail.render.resolution_percentage=100
camera(detail,'Math_Brick_Detail_Camera',(60,-1,18),(17.3,-1,18),11.5)
detail.render.image_settings.file_format='PNG'; detail.render.filepath=str(OUT/'brick_detail_after.png')
bpy.context.window.scene=detail; bpy.ops.render.render(write_still=True)

inside=setup_scene('Math Third Floor Library Review')
sel=bpy.data.collections.new('Math Interior Review Objects'); inside.collection.children.link(sel)
for o in asset.all_objects:
    if ((o.name.startswith('MATH_Lib_') and o.name!='MATH_Lib_Ceiling') or o.name.startswith('MATH_2026_Library_')
        or o.name.startswith('MATH_2026_Inferred_Group_Room_') or o.name.startswith('MATH_2026_Library_2022_')
        or o.name.startswith('MATH_2026_Testing_Room_') or o.name.startswith('MATH_2026_Third_Floor_')):
        sel.objects.link(o)
camera(inside,'MathLibraryCamera',(0,12.0,44),(0,12.0,11.8),26)
inside.view_settings.exposure=0.0
inside.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.72
sun(inside,'MathLibraryKey',(0,16,39),(0,16,11),2600,30)
inside.render.resolution_x=1600; inside.render.resolution_y=1400
inside.camera.location=(.5,17.1,44); aim(inside.camera,(.5,17.1,11.8)); inside.camera.data.ortho_scale=22
inside.render.filepath=str(OUT/'library_after.png')
bpy.context.window.scene=inside
bpy.ops.render.render(write_still=True)

# Plan-reading image: a shadow-free top view makes the room walls, open gaps,
# shelves and group-room furniture easy to compare with the 2022 plan overlay.
diagram=bpy.data.scenes.new('Math Third Floor Plan Readability')
diagram.collection.children.link(sel); diagram.world=inside.world
diagram.render.engine='BLENDER_WORKBENCH'
diagram.display.shading.light='STUDIO'
diagram.display.shading.color_type='MATERIAL'
diagram.display.shading.show_shadows=False
diagram.display.shading.show_cavity=False
diagram.display.shading.show_specular_highlight=False
diagram.display.shading.background_type='WORLD'
camera(diagram,'MathLibraryPlanCamera',(.5,17.1,44),(.5,17.1,11.8),22)
diagram.render.resolution_x=1600; diagram.render.resolution_y=1400
diagram.render.image_settings.file_format='PNG'
diagram.render.filepath=str(OUT/'library_plan_diagram.png')
bpy.context.window.scene=diagram
bpy.ops.render.render(write_still=True)

# A wider third-floor context frame includes room 352 and the south core, which
# lie beyond the library room's own plan bounds.
core=setup_scene('Math Third Floor Library and Core Review')
core.collection.children.link(sel); core.world=inside.world
core.view_settings.exposure=0.0
sun(core,'MathCoreKey',(0,16,39),(0,16,11),2600,30)
camera(core,'MathThirdFloorCamera',(.5,12.5,48),(.5,12.5,11.8),38)
core.render.resolution_x=1600; core.render.resolution_y=1600
core.render.filepath=str(OUT/'third_floor_core_after.png')
bpy.context.window.scene=core; bpy.ops.render.render(write_still=True)
print('WROTE exterior four sides, close brick detail, library renders and plan diagram')

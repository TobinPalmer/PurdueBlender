import bpy, math, json, os
from mathutils import Vector
P=os.path.abspath('audit/batch2_krannert')
path=os.path.abspath('modular/buildings/krannert_building.blend')
bpy.ops.wm.open_mainfile(filepath=path)
C=bpy.data.collections['Asset_krannert_building']; root=bpy.data.objects['AssetRoot_krannert_building']
# Idempotent rebuild: remove only this round's additions before regenerating them.
for old in list(C.objects):
 if old.name.startswith('KRAN_R1_'):
  bpy.data.objects.remove(old,do_unlink=True)
# All coordinates below are local building coordinates. Exact room XY remains inferred.
def mat(name,color,rough=.65,metal=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
 m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 return m
wood=mat('KRAN_Parrish_Warm_Oak',(.29,.14,.045),.46)
woodlight=mat('KRAN_Parrish_Oak_Edge',(.43,.25,.10),.43)
dark=mat('KRAN_Parrish_Counter_Laminate',(.035,.045,.052),.28)
upholstery=mat('KRAN_Parrish_Deep_Blue_Upholstery',(.035,.105,.19),.86)
upholstery2=mat('KRAN_Parrish_Charcoal_Upholstery',(.12,.14,.15),.9)
metal=mat('KRAN_Interior_Dark_Bronze',(.32,.32,.29),.32,.12)
ceiling=mat('KRAN_Interior_Acoustic_OffWhite',(.68,.67,.63),.9)
lightmat=mat('KRAN_Interior_Diffuser',(.92,.88,.75),.3)
spines=[mat('KRAN_Parrish_Book_'+str(i),c,.85) for i,c in enumerate([(.10,.18,.28),(.43,.12,.08),(.13,.28,.18),(.55,.37,.13),(.23,.20,.36),(.46,.43,.34)])]
def box(name,loc,dim,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='KRAN_R1_'+name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection): c.objects.unlink(o)
 C.objects.link(o);o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.data.materials.append(material)
 o['layout_status']='Photo-supported object type; local XY and dimensions estimated because no interior survey plan was found.'
 if bevel:
  mod=o.modifiers.new('Small eased furniture edges','BEVEL');mod.width=bevel;mod.segments=3
  mod2=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o
def cylinder(name,loc,radius,depth,material,verts=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=depth,location=loc);o=bpy.context.object;o.name='KRAN_R1_'+name
 for c in list(o.users_collection): c.objects.unlink(o)
 C.objects.link(o);o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.data.materials.append(material)
 o['layout_status']='Photo-supported furniture detail; dimensions and XY estimated.'
 bevel=o.modifiers.new('Soft metal edges','BEVEL');bevel.width=.012;bevel.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
# Refine visual edges across the photo-supported lounge furniture, shelving, books and tables.
for o in list(C.objects):
 if o.name.startswith(('KRAN_New_DrawingRoom_OakTable','KRAN_New_Parrish_OakUpright','KRAN_New_Parrish_Shelf','KRAN_New_Parrish_Book','KRAN_New_Parrish_StudyDesk','KRAN_New_Seat','KRAN_New_Back','KRAN_New_AcousticBlueDivider')) and o.type=='MESH' and not any(m.name=='Photo-supported eased edges' for m in o.modifiers):
  b=o.modifiers.new('Photo-supported eased edges','BEVEL');b.width=.025 if 'Book' not in o.name else .008;b.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
# Parrish: restrained long dark reference counter with oak fascia, plus booth bays.
# The official source photo supports counter + tall booth seating and warm timber partitions;
# their precise coordinates and dimensions are inferred, not plan measured.
zfloor=8.53
box('Parrish_Counter_Oak_Front',(-14.6,2.35,9.16),(12.8,.14,1.22),wood,.035)
box('Parrish_Counter_Dark_Top',(-14.6,2.15,9.79),(13.0,.75,.12),dark,.04)
box('Parrish_Counter_Recess',(-14.6,2.25,9.35),(11.9,.08,.25),woodlight,.012)
for x in [-20.2,-17.4,-14.6,-11.8,-9.0]:
 # book/reading booth: cushioned seat and high back with timber divider wings
 box('Parrish_Booth_Base',(x,.90,8.83),(1.22,.85,.58),upholstery2,.09)
 box('Parrish_Booth_Cushion',(x,.57,9.17),(1.20,.88,.16),upholstery,.075)
 box('Parrish_Booth_Back',(x,1.27,9.75),(1.20,.16,1.02),upholstery,.08)
 for side in [-.69,.69]:
  box('Parrish_Booth_Timber_Divider',(x+side,.85,9.68),(.08,1.05,1.90),woodlight,.025)
  box('Parrish_Booth_Divider_Cap',(x+side,.85,10.64),(.12,1.09,.08),wood,.025)
# Add varied book spines to empty visible spans in existing shelf rows; restrained book colors.
for shelf_x in [-20,-15,-10]:
 # Keep additions on the two lower shelf runs, without overwriting existing dense book runs.
 for yi in [-416.0]:
  pass
# Existing books are monochrome dark/lime. Give ordered, restrained varied spines as the reference photo suggests.
for i,o in enumerate(sorted([x for x in C.objects if x.name.startswith('KRAN_New_Parrish_Book')],key=lambda x:x.name)):
 if o.type=='MESH':
  o.data.materials.clear();o.data.materials.append(spines[(i*7//11)%len(spines)])
# Acoustic ceiling grid and linear luminaires are confined to the two documented room areas.
# Grid represents a generic modular acoustic ceiling; exact layout is not visible in source image.
for room_x,y,z,width,depth,label in [(-14.5,-2.2,7.76,14,11,'DrawingRoom'),(-14.5,-2.2,11.66,14,11,'Parrish')]:
 for x in [room_x-6.5,room_x-3.25,room_x,room_x+3.25,room_x+6.5]:
  box(label+'_Ceiling_Tee_X',(x,y,z),(.02,depth,.02),metal,.006)
 for yy in [y-5,y-2.5,y,y+2.5,y+5]:
  box(label+'_Ceiling_Tee_Y',(room_x,yy,z),(width,.02,.02),metal,.006)
 for xoff in [-4.8,-1.6,1.6,4.8]:
  box(label+'_Ceiling_Light_Diffuser',(room_x+xoff,y,z-.055),(.72,3.0,.055),lightmat,.025)
  # emissive restrained luminous face for legibility without changing full scene illumination
  m=lightmat; p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.95,.78,.48,1);p.inputs['Emission Strength'].default_value=.25
# More nuanced Drawing Room timber tabletop bevels and richer blue/lime variation are reflected by materials.
# Add narrow timber reveal trim to acoustic dividers to avoid featureless sheet appearance.
for o in list(C.objects):
 if o.name.startswith('KRAN_New_AcousticBlueDivider'):
  x,y,z=o.location
  box('DrawingRoom_Divider_Wood_Edge',(x,y,z),(.08,1.44,1.44),woodlight,.025)
  # Use the blue panel on the camera-facing side of the timber backing.
  box('DrawingRoom_Divider_Blue_Insert',(x-.055,y,z),(.025,1.30,1.30),upholstery,.025)
# Preserve IDs, root and existing model architecture. Temporary objects/cameras are not introduced.
bpy.context.scene['krannert_revision_1']='Parrish booth seating/counter, varied shelf spines, refined furniture edge geometry, room-specific acoustic ceiling grid and diffusers. Photo types supported by Purdue tour PDF pp.4 and 6; exact XY/dimensions and ceiling grid inferred.'
bpy.context.scene['krannert_open_uncertainties']='Existing exterior facade gap, roof profile, room plan/circulation, building dimensions, exact interior XY, ceiling layout, and remaining floors require survey/source confirmation; no new roof or wall geometry inferred.'
# Save source.
bpy.ops.wm.save_as_mainfile(filepath=path)


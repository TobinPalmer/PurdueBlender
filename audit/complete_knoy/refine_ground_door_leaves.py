import bpy, json, os

ROOT = r'C:\Users\Tobin\Documents\Blender\PurdueMap'
BLEND = ROOT + r'\modular\buildings\knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene
asset = bpy.data.collections.get('Asset_knoy_hall')

# The low-resolution first-floor source shows door swings/openings but does not
# establish glazing or leaf construction. Replace the former blue glass proxy with
# a neutral opaque leaf estimate and explicitly preserve its evidence status.
old = bpy.data.materials.get('KNOY_Illustrative_Door_Glazing')
mat = bpy.data.materials.get('KNOY_Illustrative_Door_Leaf_Estimate')
if mat is None:
    mat = bpy.data.materials.new('KNOY_Illustrative_Door_Leaf_Estimate')
mat.diffuse_color=(0.38,0.34,0.28,1)
mat.use_nodes=True
bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Base Color'].default_value=(0.38,0.34,0.28,1)
bs.inputs['Metallic'].default_value=0.05
bs.inputs['Roughness'].default_value=0.78
doors=sorted([o for o in bpy.data.objects if o.name.startswith('KNOY_Illustrative_Door_')],key=lambda o:o.name)
for door in doors:
    door.data.materials.clear();door.data.materials.append(mat)
    door['material_status']='Opaque neutral leaf finish used as a visual estimate; the source plan does not specify door material or glazing.'
    door['source_status']='Door opening is approximate from the 1984-era thesis plan raster; width and leaf details are not surveyed.'
scene['ground_door_status']='12 estimated leaves retained where they fit unambiguously within the traced ground-plan gaps. Six remaining candidate gaps (IDs 09, 13, 17, 18, 20, 24) remain open because the candidate leaf meshes intersect crossing plan traces and the low-resolution raster does not independently resolve a door swing there.'
scene['ground_door_material_status']='All illustrative door leaves use an opaque neutral estimated finish; no glazing or swing direction is claimed.'
if old and old.users==0:
    bpy.data.materials.remove(old)
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('Saved opaque neutral finish on',len(doors),'illustrative ground-floor leaves; asset child collection:',asset.name if asset else None)

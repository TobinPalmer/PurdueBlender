import bpy,os,json
from mathutils import Vector
asset=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=asset)
scene=bpy.context.scene
# Suppress comparison-only outlines and details without deleting reviewable source geometry.
for nm in ['SC_Official_GIS_Footprint_Overlay_Ribbon']:
    o=bpy.data.objects.get(nm)
    if o: o.hide_render=True; o.hide_set(True); o['display_note']='Comparison-only GIS overlay; disabled for presentation render.'
for o in bpy.data.objects:
    if o.name.startswith('SC_Dormer_'):
        o.hide_render=True; o.hide_set(True); o['display_note']='Dormer form is unverified; omitted from presentation pending current elevation evidence.'
    if 'Keystone' in o.name and o.name.startswith('SC_Win_'):
        o.hide_render=True; o.hide_set(True); o['display_note']='Protruding window keystone omitted; not visible in available Purdue exterior references.'
# Remove visibly unsupported large rooftop plant block while preserving the source geometry as hidden review data.
for nm in ['SC_HVAC_Screen_North','SC_HVAC_Unit_1','SC_HVAC_Unit_2']:
    o=bpy.data.objects.get(nm)
    if o: o.hide_render=True; o.hide_set(True); o['display_note']='Rooftop equipment configuration unverified in available imagery.'
# Make limestone and pavement visibly warm, matching the Purdue exterior photograph.
for mn,color in [('Bedford_Indiana_Limestone',(0.52,0.40,0.29,1)),('Limestone_WaterTable',(0.52,0.40,0.29,1)),('Paving_Concrete',(0.32,0.30,0.27,1))]:
    m=bpy.data.materials.get(mn)
    if m:
        m.diffuse_color=color
        if m.use_nodes:
            bs=m.node_tree.nodes.get('Principled BSDF')
            if bs:
                bs.inputs['Base Color'].default_value=color
                bs.inputs['Roughness'].default_value=0.78
# Main door leaves are modeled in bronze-framed glass; keep the physical frame subdued.
for nm in ['SC_Main_Door_Left','SC_Main_Door_Right']:
    o=bpy.data.objects.get(nm)
    if o and o.type=='MESH':
        o.data.materials.clear();o.data.materials.append(bpy.data.materials['Architectural_Glazing'])
# Retain an interior view camera in the source scene so the schematic layout is reviewable.
cam_coll=bpy.data.collections.get('00_Inspection_Cameras')
cam=bpy.data.objects.get('Cam_SC_06_Interior_Schematic')
if cam is None:
    data=bpy.data.cameras.new('Cam_SC_06_Interior_Schematic_Data');cam=bpy.data.objects.new('Cam_SC_06_Interior_Schematic',data);cam_coll.objects.link(cam)
cam.location=(49,-7,10);cam.data.lens=36;cam.rotation_euler=(Vector((21.5,-7,2.65))-cam.location).to_track_quat('-Z','Y').to_euler()
# No persistent hide state on exterior or portico; this camera is only a saved review aid.
scene.camera=cam
scene['SC presentation warning']='Interior room layout is schematic, derived from stated uses only. Existing 2022 floor plans are historical; no current room-by-room plan was available.'
bpy.ops.wm.save_as_mainfile(filepath=asset)
print('SAVED',asset,'asset_objects',len(bpy.data.collections['Asset_stanley_coulter_hall'].all_objects),'camera_objects',len(cam_coll.objects),'hidden dormer parts',sum(o.name.startswith('SC_Dormer_') and o.hide_render for o in bpy.data.objects),'hidden keystones',sum('Keystone' in o.name and o.name.startswith('SC_Win_') and o.hide_render for o in bpy.data.objects))

import bpy, json, os
p = os.path.normcase(os.path.abspath(bpy.data.filepath))
expected = os.path.normcase(os.path.abspath('modular/buildings/mccutcheon_hall.blend'))
if p != expected:
    raise RuntimeError(f'Unexpected file: {p}')
asset = bpy.data.collections.get('Asset_mccutcheon_hall')
if asset is None:
    raise RuntimeError('Missing expected export collection')
overlay = bpy.data.objects.get('MCUT_Official_Footprint_Overlay')
if overlay is None:
    raise RuntimeError('Expected official GIS diagnostic outline missing')
if overlay.type != 'CURVE':
    raise RuntimeError(f'Expected diagnostic curve, got {overlay.type}')
# This is a diagnostic GIS trace, not building geometry. Keep it visible in the
# viewport for footprint comparison but exclude its emissive green line from renders.
overlay.hide_render = True
overlay['purpose'] = 'Diagnostic GIS footprint trace; viewport only, excluded from architectural renders.'
overlay['source_fid'] = 57
overlay['source_url'] = 'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0'
bpy.ops.wm.save_as_mainfile(filepath=expected)
print('MCUT_SAVE_R1=' + json.dumps({'file':p,'export_collection':asset.name,'objects':len(asset.all_objects),'overlay_hide_render':overlay.hide_render,'overlay_hide_viewport':overlay.hide_viewport,'overlay_type':overlay.type,'save':'ok'}))

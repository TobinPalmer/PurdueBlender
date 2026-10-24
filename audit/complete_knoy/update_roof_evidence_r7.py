import bpy

ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET = ROOT + r'/modular/buildings/knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=ASSET)

pv = bpy.data.objects.get('KNOY_Roof_PV_28Panel_Array_R6')
assert pv is not None and pv.type == 'MESH'
pv['historical_panel_count'] = 28
pv['historical_panel_count_source'] = 'Purdue Polytechnic 2017 Knoy rooftop solar installation article'
pv['layout_status'] = 'Schematic 4x7 display; exact array layout and dimensions are not source-measured.'
pv['current_roof_presence_status'] = (
    'State of Indiana 2023 orthophoto shows a panel-like installation in a '
    'south roof region. This does not register the modeled PV mesh transform; '
    'exact panel count and layout are not legible enough to verify.'
)
pv['current_persistence_status'] = (
    'Presence is supported for the 2023 imagery capture only; 2026 '
    'persistence is unverified.'
)
pv['current_roof_imagery_source'] = (
    'https://di-ingov.img.arcgis.com/arcgis/rest/services/'
    'DynamicWebMercator/Indiana_Current_Imagery/ImageServer'
)
scene = bpy.context.scene
scene['knoy_roof_imagery_status'] = (
    '2023 Indiana orthophoto identifies panel-like roof equipment on Knoy; '
    'module count/layout and 2026 persistence remain unverified.'
)

notes = bpy.data.texts.get('EVIDENCE_AND_INTERIOR_NOTES.txt')
assert notes is not None
text = notes.as_string()
old = (
    'Purdue Polytechnic\'s May 2017 report documents 28 PV panels installed on the roof on April 18, replacing an older 24-panel array. This model uses 28 modules. A State of Indiana 2023 orthophoto shows a panel-like roof installation in the same south roof zone, supporting roof-array presence in that capture. The 4 x 7 arrangement, exact position, orientation, tilt and rack dimensions remain estimates; the 2023 image does not make module count reliably legible, and 2026 persistence remains unverified.'
)
new = (
    'Purdue Polytechnic\'s May 2017 report documents 28 PV panels installed on the roof on April 18, replacing an older 24-panel array. This model uses 28 modules. A State of Indiana 2023 orthophoto shows a panel-like installation in a south roof region, supporting roof-array presence in that capture. This observation does not register the modeled PV mesh to the image. The 4 x 7 arrangement, exact position, orientation, tilt and rack dimensions remain estimates; the 2023 image does not make module count reliably legible, and 2026 persistence remains unverified.'
)
assert old in text, 'Expected round-6 solar note was not found; refusing to replace blindly.'
notes.clear()
notes.write(text.replace(old, new))
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print('Saved Knoy round-7 source metadata; no mesh geometry changed.')

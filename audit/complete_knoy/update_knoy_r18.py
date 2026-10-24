import bpy
from pathlib import Path

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET = ROOT / 'modular/buildings/knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))

glass = bpy.data.objects['KNOY_Fenestration_Ribbon_Glass']
mullions = bpy.data.objects['KNOY_Fenestration_Bronze_Mullions']
spandrels = bpy.data.objects['KNOY_Facade_Brick_Spandrels_R17']
walls = bpy.data.objects['KNOY_Exterior_Masonry_Walls']

facade_status = (
    'Schematic qualitative interpretation only. The 1.40 m L1-L4 glass height '
    'is not a measured dimension. Purdue Archives photo record 75 shows narrow, '
    'interrupted slit-like ribbons within large brick fields on visible faces, '
    'but it is uncalibrated and does not register the image to this GIS footprint. '
    'The current repeated ribbon cadence around the model is not verified for all elevations.'
)
for obj in (glass, mullions, spandrels, walls):
    obj['r18_facade_status'] = facade_status
glass['r18_dimension_caveat'] = '1.40 m is a visual proxy inherited from R17; no dimensioned elevation supports it.'
glass['r18_cadence_caveat'] = 'Do not infer continuous or uniform glazing around every elevation from the archival photo.'
spandrels['r18_cadence_caveat'] = 'The current bands preserve inherited schematic openings. Photo shows interrupted ribbons; face registration is unresolved.'

roof = bpy.data.objects.get('KNOY_Roof_Slabs') or bpy.data.objects.get('KNOY_Roof_Deck')
if roof:
    roof['r18_evidence_status'] = (
        '2018 3DEP DSM minus approximate bare-earth reference gives a broad roof-like '
        'surface distribution, not a measured roof slab or occupied-floor height. '
        'GIS 48 ft attribute conflicts; L5/roof status and penthouse dimensions remain unresolved.'
    )
for obj in bpy.data.objects:
    if 'Penthouse' in obj.name or 'penthouse' in obj.name.lower():
        obj['r18_evidence_status'] = (
            'Schematic placeholder only. 2018 DSM upper-percentile cells do not spatially '
            'coincide with the current candidate bbox; they may include edge artifacts, trees, '
            'or equipment. No fit/alignment or exact dimensions are asserted.'
        )

notes = bpy.data.texts.get('EVIDENCE_AND_INTERIOR_NOTES.txt')
if notes is None:
    notes = bpy.data.texts.new('EVIDENCE_AND_INTERIOR_NOTES.txt')
notes.write(
    '\n\nROUND 18 — REVIEW DISAGREEMENT AND LIMITS\n'
    '------------------------------------------------------------\n'
    'Two independent R17 reviews scored the full building 7.8/10 and 7.9/10. '
    'Both identified the same main exterior limitation: the archival Purdue photo '
    'shows narrow, visibly interrupted glazing slits within large brick fields, '
    'while the saved model repeats continuous bands around the shell. The R17 1.40 m '
    'band height is a qualitative visual proxy only; it is not a measured dimension, '
    'and the photograph cannot register the cadence to individual GIS faces. The '
    'reviews do not establish that the interrupted pattern applies to every elevation. '
    'No facade geometry was changed in R18 because the available photo is uncalibrated '
    'and face registration is unresolved; adding interruptions to selected segments '
    'would imply a correspondence the evidence does not support.\n\n'
    'Roof check: the local 2018 Indiana 3DEP DSM comparison has 1,126 valid footprint '
    'cells, with AGL p50 59.88 ft, p75 60.12 ft, p90 63.90 ft, p95 71.81 ft, p99 '
    '75.36 ft, and max 88.90 ft against the prior approximate 621.06 ft bare-earth '
    'reference. High cells cluster at the footprint edge and do not fall inside the '
    'current schematic penthouse bbox. These are surface-height observations, not '
    'proof of an occupied L5, parapet height, or penthouse position. GIS 48 ft remains '
    'a conflict. The comparison and its limitations are in '
    'audit/complete_knoy/roof_spatial_check_r18.json.\n\n'
    'Circulation: no newly found dimensioned as-built stair/route source. Existing '
    'stair runs and room traces remain illustrative; continuous accessible circulation '
    'to basement, L1, L5, or roof is not verified. No circulation geometry was added.\n'
)

scene = bpy.context.scene
scene['knoy_r18_review_status'] = 'Evidence and uncertainty pass; no geometric changes.'
scene['knoy_r18_independent_scores'] = 'R17: 7.8/10 and 7.9/10; both below 8/10.'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('R18_SAVED', ASSET)
print('R18_FACADE', facade_status)

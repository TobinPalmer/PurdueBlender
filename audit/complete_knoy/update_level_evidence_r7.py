import bpy

ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET = ROOT + r'/modular/buildings/knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=ASSET)
notes = bpy.data.texts.get('EVIDENCE_AND_INTERIOR_NOTES.txt')
assert notes
text = notes.as_string()
old = (
    "Purdue's 2018 Gateway planning study (PDF page 24) labels existing Knoy Levels 1-4 at 14 ft 8 in floor-to-floor. "
    "The current modeled L1-L4 datum intervals are 4.481, 4.480 and 4.481 m, about 0.010 m above that planning note. "
    "This is not an as-built survey. Purdue GIS feature 243 reports five levels and 48 ft extrusion, but those attributes "
    "do not resolve the 2018 sheet's four-level labeling or provide a roof elevation. L5, roof-deck, parapet and penthouse "
    "heights remain uncertain; the related geometry was retained unchanged."
)
new = (
    "Purdue's 2018 Gateway planning study (PDF page 24) labels existing Knoy Levels 1-4 at 14 ft 8 in floor-to-floor. "
    "The current modeled L1-L4 datum intervals are 4.481, 4.480 and 4.481 m, about 0.010 m above that planning note. "
    "This is not an as-built survey. Purdue Polytechnic's emergency-plan page lists KNOY G-011 and KNOY 457 and refers "
    "to staff on the first and fourth floors, corroborating L1/L4 use but not mapping rooms or locating stairs. Purdue GIS "
    "feature 243 reports five levels and 48 ft extrusion, but those attributes do not resolve the 2018 sheet's four-level "
    "labeling or provide a roof elevation. L5, roof-deck, parapet and penthouse heights remain uncertain; the related "
    "geometry was retained unchanged."
)
assert old in text, 'Expected round-6 floor note missing.'
notes.clear()
notes.write(text.replace(old, new))
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print('Saved Knoy round-7 floor evidence note; no mesh geometry changed.')

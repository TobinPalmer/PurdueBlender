import bpy
import os

wiley_blend = r"C:\Users\Tobin\Documents\Codex\2026-10-21\inste\outputs\Wiley_Street_View_Reconstruction.blend"

# Check available collections in wiley_blend
with bpy.data.libraries.load(wiley_blend) as (data_from, data_to):
    print("Available Wiley collections:", data_from.collections)

# Append Wiley collections
wiley_cols_to_load = [
    '01_Wiley_Masonry', '02_Windows_and_Frames', '03_Stair_Entrances', 
    '04_Roofs', '05_Site', '06_Landscape', '08_Dining_Hall_Side_Entrances',
    '11_Interior_Basement', '12_Interior_First_Floor', '13_Interior_Second_Floor',
    '14_Interior_Third_Floor', '15_Common_Block_Interiors', '16_Stairs_Lifts_Connectors'
]

# Create Master Wiley Collection in scene
master_wiley_col = bpy.data.collections.get("06_Wiley_Hall_Detailed")
if not master_wiley_col:
    master_wiley_col = bpy.data.collections.new("06_Wiley_Hall_Detailed")
    bpy.context.scene.collection.children.link(master_wiley_col)

# Append each collection from the blend file
for cname in wiley_cols_to_load:
    # Use bpy.ops.wm.append to append collection
    try:
        bpy.ops.wm.append(
            filepath=os.path.join(wiley_blend, "Collection", cname),
            directory=os.path.join(wiley_blend, "Collection"),
            filename=cname
        )
        print(f"Successfully appended: {cname}")
    except Exception as e:
        print(f"Error appending {cname}: {e}")

# Link newly added collections under master_wiley_col and translate objects
target_x, target_y = -599.2, 125.6
translated_count = 0

for cname in wiley_cols_to_load:
    col = bpy.data.collections.get(cname)
    if col:
        # Move col to be child of master_wiley_col if linked to scene root
        if col in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.unlink(col)
        if col not in master_wiley_col.children:
            master_wiley_col.children.link(col)
            
        for obj in col.objects:
            obj.location.x += target_x
            obj.location.y += target_y
            translated_count += 1

print(f"Total Wiley objects moved to real campus site ({target_x}, {target_y}): {translated_count}")

"""
Execute Refinement & Render for Hovde Hall
"""

import bpy
import sys
import os

master_blend = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
script_dir = r"C:\Users\Tobin\.gemini\antigravity\scratch\purdue_digital_twin"

print(f"Opening master blend file: {master_blend}")
bpy.ops.wm.open_mainfile(filepath=master_blend)

# Execute refine script
refine_script = os.path.join(script_dir, "refine_hovde_hall.py")
print(f"Executing: {refine_script}")
with open(refine_script, "r", encoding="utf-8") as f:
    exec(f.read())

# Save blend file
print(f"Saving master blend file: {master_blend}")
bpy.ops.wm.save_mainfile(filepath=master_blend)
print("Master blend file saved successfully!")

# Execute render script
render_script = os.path.join(script_dir, "render_hovde_cams.py")
print(f"Executing: {render_script}")
with open(render_script, "r", encoding="utf-8") as f:
    exec(f.read())

print("=== ALL HOVDE REFINEMENT TASKS COMPLETED! ===")

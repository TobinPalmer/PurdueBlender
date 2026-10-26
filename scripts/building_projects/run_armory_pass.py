"""
Combined Runner: Build Purdue Armory & Render Inspection Cameras
"""

import bpy
import sys
import os

master_blend = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
script_dir = r"C:\Users\Tobin\.gemini\antigravity\scratch\purdue_digital_twin"

print(f"Opening master blend file: {master_blend}")
bpy.ops.wm.open_mainfile(filepath=master_blend)

# Execute build script
build_script = os.path.join(script_dir, "build_purdue_armory.py")
print(f"Executing: {build_script}")
with open(build_script, "r", encoding="utf-8") as f:
    exec(f.read())

# Save blend file
print(f"Saving master blend file: {master_blend}")
bpy.ops.wm.save_mainfile(filepath=master_blend)
print("Master blend file saved successfully!")

# Execute render script
render_script = os.path.join(script_dir, "render_armory_cams.py")
print(f"Executing: {render_script}")
with open(render_script, "r", encoding="utf-8") as f:
    exec(f.read())

print("=== ALL ARMORY PIPELINE TASKS COMPLETED! ===")

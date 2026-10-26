"""
Combined Runner: Stewart Center Gold Standard Remediation & Re-Render
"""

import bpy
import sys
import os

master_blend = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
script_dir = r"C:\Users\Tobin\.gemini\antigravity\scratch\purdue_digital_twin"

print(f"Opening master blend file: {master_blend}")
bpy.ops.wm.open_mainfile(filepath=master_blend)

# Execute gold remediation script
gold_script = os.path.join(script_dir, "stewart_gold_remediation.py")
print(f"Executing: {gold_script}")
with open(gold_script, "r", encoding="utf-8") as f:
    exec(f.read())

# Save blend file
print(f"Saving master blend file: {master_blend}")
bpy.ops.wm.save_mainfile(filepath=master_blend)
print("Master blend file saved successfully!")

# Execute render script
render_script = os.path.join(script_dir, "render_stewart_cams.py")
print(f"Executing: {render_script}")
with open(render_script, "r", encoding="utf-8") as f:
    exec(f.read())

print("=== ALL STEWART CENTER PIPELINE TASKS COMPLETED! ===")

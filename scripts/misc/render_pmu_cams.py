import bpy
import os

artifact_dir = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

cams = [
    ("Cam_67_PMU_StateStreet_South_Hero", "pmu_cam67_south_hero.png"),
    ("Cam_68_PMU_GreatHall_MemorialCross_Interior", "pmu_cam68_greathall_interior.png"),
    ("Cam_69_PMU_DiningCourt_Commons_Interior", "pmu_cam69_diningcourt_interior.png"),
    ("Cam_70_PMU_WestCourtyard_Stewart_Interface", "pmu_cam70_west_courtyard.png"),
    ("Cam_71_PMU_StateStreet_GrantStreet_Aerial", "pmu_cam71_precinct_aerial.png")
]

scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

for cam_name, fname in cams:
    cam_obj = bpy.data.objects.get(cam_name)
    if cam_obj:
        scene.camera = cam_obj
        out_path = os.path.join(artifact_dir, fname)
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        size_kb = os.path.getsize(out_path) / 1024
        print(f"Rendered {cam_name} -> {fname} ({size_kb:.1f} KB)")
    else:
        print(f"ERROR: Camera {cam_name} not found!")

print("All PMU inspection cameras rendered successfully!")

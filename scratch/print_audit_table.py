import json

data = json.load(open('scratch/deep_material_audit.json'))
print(f"{'Building ID':<26} | {'Meshes':<6} | {'Unassigned':<10} | {'DefaultMat':<10} | {'Materials':<10}")
print("-" * 75)
for b_id, d in data.items():
    print(f"{b_id:<26} | {d['total_mesh_objects']:<6} | {d['unassigned_count']:<10} | {d['default_mat_count']:<10} | {len(d['materials']):<10}")

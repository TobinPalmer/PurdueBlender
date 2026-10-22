import json

data = json.load(open('scratch/deep_material_audit.json'))
for b_id in ['felix_haas_hall', 'math_sciences', 'owen_hall', 'class_of_1950', 'rawls_hall']:
    d = data[b_id]
    print(f"=== {b_id} (unassigned: {d['unassigned_count']}) ===")
    print("Sample:", d['unassigned_sample'])

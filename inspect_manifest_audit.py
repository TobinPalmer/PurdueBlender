import json

with open("purdue_30_sector_manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

with open("sector_audit_report.json", "r", encoding="utf-8") as f:
    audit = json.load(f)

print("Title:", audit.get("title"))
print("Total scene objects:", audit.get("total_scene_objects"))
print("Total sectors audited:", audit.get("total_sectors_audited"))
print("Average score:", audit.get("average_sector_score"))
print("-" * 80)
print(f"{'Sector':<6} | {'Col':<3} | {'Row':<3} | {'Objs':<5} | {'Score':<5} | {'Status':<25} | {'Name'}")
print("-" * 80)
for s in audit["sectors"]:
    print(f"{s['sector_id']:<6} | {s['grid_col']:<3} | {s['grid_row']:<3} | {s['object_count']:<5} | {s['fidelity_score']:<5} | {s['status']:<25} | {s['name']}")

from pathlib import Path
import bpy, json
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
ASSET=ROOT/"modular/buildings/benjamin_harrison_hall.blend"
bpy.ops.wm.open_mainfile(filepath=str(ASSET)); scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE_NEXT"
scene.render.resolution_x=900; scene.render.resolution_y=700; scene.render.resolution_percentage=55
scene.render.image_settings.file_format="PNG"
scene.render.resolution_percentage=60
reports=[]
for name in ("Cam_Hero_Perspective","Cam_TopDown_Footprint","Cam_West_Entrance"):
 cam=bpy.data.objects.get(name)
 if not cam or cam.type!="CAMERA":
  reports.append({"camera":name,"error":"missing"});continue
 scene.camera=cam
 path=OUT/(name.lower()+".png")
 scene.render.filepath=str(path)
 bpy.ops.render.render(write_still=True)
 reports.append({"camera":name,"output":path.name,"exists":path.exists(),"bytes":path.stat().st_size if path.exists() else 0})
(OUT/"render_report.json").write_text(json.dumps(reports,indent=2)+"\n",encoding="utf-8")
print(json.dumps(reports,indent=2))

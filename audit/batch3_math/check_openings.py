import bpy,json
from pathlib import Path
ROOT=Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
SRC=ROOT/"modular/buildings/math_sciences.blend"
OUT=ROOT/"audit/batch3_math/geometry_checks.json"
bpy.ops.wm.open_mainfile(filepath=str(SRC))
wall=bpy.data.objects["MATH_Corrected_GIS_Wall_Envelope"]
infill=bpy.data.objects["MATH_2026_Perforated_Brick_Facades"]
objs=[wall,infill]
east_y=[-23.1,-16.8,-10.5,-4.2,2.1,8.4]
floor_z=[5.15+3.18*i for i in range(9)]
south_x=[1.4,5.0,8.6]
miss=[];hits=[]
for label, samples, start, direction in [
    ("east",[(y,z) for y in east_y for z in floor_z],lambda yz:(18.0,yz[0],yz[1]),(-1,0,0)),
    ("south",[(x,z) for x in south_x for z in floor_z],lambda xz:(xz[0],-34.3,xz[1]),(0,1,0))]:
    for a,b in samples:
        origin=start((a,b)); found=[]
        for obj in objs:
            hit,loc,norm,face=obj.ray_cast(origin,direction,distance=5.0)
            if hit: found.append((obj.name,tuple(round(v,4) for v in loc)))
        (hits if found else miss).append({"elevation":label,"sample":(a,b),"hit":found})
controls=[]
for label, samples, start, direction in [
    ("east",[(-19.95,5.15),(-7.35,5.15),(-1.05,5.15),(5.25,5.15)],lambda yz:(18.0,yz[0],yz[1]),(-1,0,0)),
    ("south",[(3.2,5.15),(6.8,5.15)],lambda xz:(xz[0],-34.3,xz[1]),(0,1,0))]:
    for a,b in samples:
        origin=start((a,b)); found=[]
        for obj in objs:
            hit,loc,norm,face=obj.ray_cast(origin,direction,distance=5.0)
            if hit: found.append((obj.name,tuple(round(v,4) for v in loc)))
        controls.append({"elevation":label,"sample":(a,b),"hit":found})
result={"reopened":True,"export_collection":"Asset_math_sciences",
 "direct_objects":len(bpy.data.collections['Asset_math_sciences'].objects),
 "all_export_objects":len(bpy.data.collections['Asset_math_sciences'].all_objects),
 "window_openings_expected":81,"east_face_samples":54,"south_face_samples":27,
 "ray_samples_blocked_by_brick":len(hits),"ray_samples_clear_through_wall":len(miss),
 "blocked_samples":hits,"clear_samples":miss,"solid_wall_control_samples":controls,
 "wall_component_bounds_m":{"east":[[16.754,17.307],[-27.489,11.981],[0,33.2]],
  "south":[[-2.303,12.924],[-33.961,-33.594],[0,33.2]]},
 "notes":"Ray checks exclude glass and limestone trim and test only the shell plus the brick infill at each pane center."}
OUT.write_text(json.dumps(result,indent=2))
print(result)

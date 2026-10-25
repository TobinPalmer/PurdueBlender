"""Photo-reference proportion pass for Lawson's still-unmeasured roof silhouette."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT=Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET=ROOT/"modular/buildings/lawson_hall.blend"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))

def world_points(ob):
    return [ob.matrix_world @ v.co for v in ob.data.vertices]

def scale_about_bbox(ob, sx, sy, new_height=None, preserve_bottom=True):
    if ob.data.users>1: ob.data=ob.data.copy()
    pts=world_points(ob)
    x0=min(p.x for p in pts);x1=max(p.x for p in pts)
    y0=min(p.y for p in pts);y1=max(p.y for p in pts)
    z0=min(p.z for p in pts);z1=max(p.z for p in pts)
    cx=(x0+x1)/2;cy=(y0+y1)/2
    sz=(new_height/(z1-z0)) if new_height is not None else 1.0
    inv=ob.matrix_world.inverted()
    for v in ob.data.vertices:
        p=ob.matrix_world @ v.co
        zbase=z0 if preserve_bottom else (z0+z1)/2
        if preserve_bottom:
            np=Vector((cx+(p.x-cx)*sx,cy+(p.y-cy)*sy,zbase+(p.z-zbase)*sz))
        else:
            cz=(z0+z1)/2
            np=Vector((cx+(p.x-cx)*sx,cy+(p.y-cy)*sy,cz+(p.z-cz)*sz))
        v.co=inv@np
    ob.data.update()
    return {"before_bounds_m":[[x0,x1],[y0,y1],[z0,z1]],"after_dimensions_m":[(x1-x0)*sx,(y1-y0)*sy,(z1-z0)*sz],"center_xy_m":[cx,cy]}

roof=bpy.data.objects.get("LWSN_Mechanical_Penthouse")
units=bpy.data.objects.get("LWSN_Rooftop_Mechanical_Units")
if not roof or not units: raise RuntimeError("Expected Lawson rooftop objects")
if roof.get("r8_photo_silhouette_refined"):
    print("R8 photo proportions already applied; leaving saved geometry unchanged")
else:
    roof_before=world_points(roof);base=min(p.z for p in roof_before)
    roof_report=scale_about_bbox(roof,8.5/12.0,20.0/38.0,new_height=3.8,preserve_bottom=True)
    roof["r8_photo_silhouette_refined"]=True
    roof["r8_photo_source"]="Purdue CS Lawson Building Update, 2006-03-17, aerial/exterior photos; audit/batch2_lawson/lawson_2006_building_march1.jpg and audit/batch2_lawson/lawson_2006_dedication4.jpg"
    roof["r8_dimension_status"]="All revised footprint and height values are visual proportions from perspective photos; not measured."
    roof_after=world_points(roof);new_top=max(p.z for p in roof_after)
    unit_report=scale_about_bbox(units,8.0/11.75,14.0/28.5,new_height=1.4,preserve_bottom=True)
    unit_after=world_points(units);unit_base=min(p.z for p in unit_after)
    inv=units.matrix_world.inverted();dz=new_top-unit_base
    if units.data.users>1: units.data=units.data.copy();inv=units.matrix_world.inverted()
    for v in units.data.vertices:
        p=units.matrix_world@v.co;v.co=inv@Vector((p.x,p.y,p.z+dz))
    units.data.update()
    units["r8_photo_silhouette_refined"]=True
    units["r8_photo_source"]="Purdue CS Lawson Building Update, 2006-03-17, exterior/aerial photographs; visual-only rooftop scale reference."
    units["r8_dimension_status"]="Approximate resized equipment group to read as small rooftop elements; size and exact count are unverified."
    report={"photo_source":"https://www.cs.purdue.edu/news/articles/2006/building-update-march.html","roof":roof_report,"rooftop_units":unit_report,"new_roof_top_z_m":new_top,"units_bottom_z_m":min(p.z for p in world_points(units)),"limits":"Perspective photos support relative silhouette only; no measured roof elevations or equipment schedule found."}
    (ROOT/"audit/batch2_lawson/roof_photo_refinement_round8.json").write_text(json.dumps(report,indent=2),encoding="utf8")
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    print(json.dumps(report,indent=2))

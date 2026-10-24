import bpy, os
ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET=os.path.join(ROOT,"modular","buildings","neil_armstrong_hall.blend")
bpy.ops.wm.open_mainfile(filepath=ASSET)
# A LiDAR envelope top is a triangulated height surface, not one single flat
# cap. Apply the documented red ACM cue to every upward-facing roof patch in
# this high zone; retain brick on the envelope's vertical sides.
roof=bpy.data.objects["ARMS_R5_Coarse_LiDAR_roof_high"]
roof.data.update()
acm=bpy.data.materials.get("ARMS_R6_Mayflower_Red_ACM") or bpy.data.materials.new("ARMS_R6_Mayflower_Red_ACM")
acm.use_nodes=True
acm_bs=next(n for n in acm.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
acm_bs.inputs["Base Color"].default_value=(0.24,0.018,0.035,1)
acm_bs.inputs["Metallic"].default_value=0.18
acm_bs.inputs["Roughness"].default_value=0.38
# Existing roof slabs already use the building's ACM material. Give that
# building-local material the same restrained red so old and LiDAR-derived
# roof surfaces do not read as conflicting pink/white finishes.
legacy_acm=bpy.data.materials["ARMS_Mayflower_Red_ACM"]
legacy_acm.use_nodes=True
legacy_bs=next(n for n in legacy_acm.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
legacy_bs.inputs["Base Color"].default_value=(0.24,0.018,0.035,1)
legacy_bs.inputs["Metallic"].default_value=0.18
legacy_bs.inputs["Roughness"].default_value=0.38
if acm.name not in [m.name for m in roof.data.materials if m]:
    roof.data.materials.append(acm)
acm_index=next(i for i,m in enumerate(roof.data.materials) if m and m.name==acm.name)
roof_faces=0
for poly in roof.data.polygons:
    if poly.normal.z > 0.85:
        poly.material_index=acm_index
        roof_faces+=1
roof["roof_finish_note"]="Mayflower Red ACM assigned to all upward-facing facets in the coarse highest LiDAR roof zone. FRP documents a Mayflower Red ACM roof/truss expression; exact plan edge, slope and cladding boundary are not registered. Vertical LiDAR envelope sides remain brick."
obj=bpy.data.objects["ARMS_R6_North_Clerestory_Glass"]
mat=bpy.data.materials.get("ARMS_R6_Reflective_Blue_Glass") or bpy.data.materials.new("ARMS_R6_Reflective_Blue_Glass")
mat.use_nodes=True
bs=next(n for n in mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
bs.inputs["Base Color"].default_value=(0.20,0.34,0.43,1)
bs.inputs["Metallic"].default_value=0.08
bs.inputs["Roughness"].default_value=0.20
if "Coat Weight" in bs.inputs: bs.inputs["Coat Weight"].default_value=0.28
if "Coat Roughness" in bs.inputs: bs.inputs["Coat Roughness"].default_value=0.16
obj.data.materials.clear(); obj.data.materials.append(mat)
obj["material_note"]="Brighter blue-gray reflective glazing proxy to remain legible in the campus-scale render; derived from the documented glass curtainwall appearance, without an exact photograph-to-wall texture projection."
obj["source_basis"]="Geotagged Commons 2016-03 exterior image shows an upper horizontal glazing band above red-brick facade. Added to the candidate north-side edge of the GIS-aligned envelope as a qualitative interpretation; camera bearing is unavailable."
obj["registration_uncertainty"]="The geotag places the camera northwest of the footprint, but photo bearing, focal calibration, exact facade assignment and band dimensions are unavailable; location/size are schematic and should not be read as a registered elevation."
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print("Updated R6 roof facets",roof_faces,"and glass material; saved source asset")

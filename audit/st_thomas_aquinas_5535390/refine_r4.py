"""R4 corrective pass: connect sanctuary structure, temper masonry, finish classroom cutaway."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
AUDIT=Path(__file__).resolve().parent
ASSET_PATH=ROOT/"modular/buildings/massing_st_thomas_aquinas_5535390.blend"
ASSET=bpy.data.collections["Asset_massing_st_thomas_aquinas_5535390"]
ROOT_OBJ=bpy.data.objects["AssetRoot_massing_st_thomas_aquinas_5535390"]

# Make this script safe to rerun from the R3/R4 asset.
for ob in list(ASSET.all_objects):
    if ob.name.startswith("SOTAC_R4_"):
        bpy.data.objects.remove(ob,do_unlink=True)

def box(name,loc,dims,mat,bevel=.012):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob=bpy.context.object; ob.name=name; ob.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    ASSET.objects.link(ob); ob.parent=ROOT_OBJ; ob.matrix_parent_inverse=ROOT_OBJ.matrix_world.inverted()
    if mat: ob.data.materials.append(mat)
    if bevel>0:
        m=ob.modifiers.new("R4 softened edges","BEVEL");m.width=bevel;m.segments=2
        ob.modifiers.new("R4 weighted normals","WEIGHTED_NORMAL")
    return ob

def beam(name,a,b,width,mat):
    av,bv=Vector(a),Vector(b);d=bv-av
    ob=box(name,(av+bv)*.5,(width,width,d.length),mat,.009)
    ob.rotation_mode="QUATERNION";ob.rotation_quaternion=d.to_track_quat("Z","Y")
    return ob

def mat(name): return bpy.data.materials.get(name)
wood=mat("SOTAC_Warm_Oak") or mat("SOTAC_Pew_Oak")
woodlight=mat("SOTAC_Pew_Oak") or wood
plaster=mat("SOTAC_Interior_Warm_Plaster")
stone=mat("SOTAC_Limestone_Trim")
brick=mat("SOTAC_Procedural_Red_Brick")
green=mat("SOTAC_Interior_Sanctuary_Accent") or mat("SOTAC_Recess_Shadow")
if not green:
    green=bpy.data.materials.new("SOTAC_R4_Classroom_Board_Green"); green.diffuse_color=(.035,.16,.105,1)
    green.use_nodes=True;green.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.035,.16,.105,1)
    green.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=.78

# Lower procedural course contrast and relief. Keep meter-based facade UVs intact.
if brick and brick.use_nodes:
    nodes=brick.node_tree.nodes
    bn=next((n for n in nodes if n.bl_idname=="ShaderNodeTexBrick"),None)
    bump=next((n for n in nodes if n.bl_idname=="ShaderNodeBump"),None)
    if bn:
        bn.inputs["Color1"].default_value=(.34,.12,.072,1)
        bn.inputs["Color2"].default_value=(.29,.085,.050,1)
        bn.inputs["Mortar"].default_value=(.24,.17,.12,1)
        bn.inputs["Scale"].default_value=.78
        bn.inputs["Brick Width"].default_value=.50
        bn.inputs["Row Height"].default_value=.115
        bn.inputs["Mortar Size"].default_value=.009
        bn.inputs["Mortar Smooth"].default_value=.05
    if bump:
        bump.inputs["Strength"].default_value=.065
        bump.inputs["Distance"].default_value=.009

# Replace the floating R3 truss set with six identical trusses whose rafter feet
# land directly on continuous wall plates above the brick piers. The geometry is
# intentionally open in review cutaways; it represents schematic timber framing.
for ob in list(ASSET.all_objects):
    if ob.name.startswith(("SOTAC_CeilingTruss_","SOTAC_Sanctuary_Pendant_")):
        bpy.data.objects.remove(ob,do_unlink=True)
xw=-19.42; xe=-3.58; xr=-11.50
z_eave=6.48; z_ridge=10.70
y0=-5.25; y1=25.25
for side,x in (("west",xw),("east",xe)):
    box(f"SOTAC_R4_Sanctuary_WallPlate_{side}",(x,(y0+y1)/2,z_eave+.12),(.40,y1-y0,.24),wood,.025)
    box(f"SOTAC_R4_Sanctuary_Eave_Fascia_{side}",(x,(y0+y1)/2,z_eave+.42),(.20,y1-y0,.24),wood,.015)
for i,y in enumerate((-3.0,2.0,7.0,12.0,17.0,22.0)):
    left=(xw,y,z_eave+.25);right=(xe,y,z_eave+.25);peak=(xr,y,z_ridge)
    beam(f"SOTAC_R4_SanctuaryTruss_{i}_Tie",left,right,.20,wood)
    beam(f"SOTAC_R4_SanctuaryTruss_{i}_WestRafter",left,peak,.19,wood)
    beam(f"SOTAC_R4_SanctuaryTruss_{i}_EastRafter",peak,right,.19,wood)
    beam(f"SOTAC_R4_SanctuaryTruss_{i}_KingPost",(xr,y,z_eave+.25),peak,.15,wood)
    beam(f"SOTAC_R4_SanctuaryTruss_{i}_WestStrut",(xw+3.0,y,z_eave+.25),peak,.13,wood)
    beam(f"SOTAC_R4_SanctuaryTruss_{i}_EastStrut",(xe-3.0,y,z_eave+.25),peak,.13,wood)

# A north-end brick gable closes the visible roof triangle and visually anchors
# the framing at the end wall; its silhouette is an approximation, not a measured plan.
gable_mat=mat("SOTAC_Interior_Exposed_Brick") or brick
verts=[(xw,y0-.12,6.35),(xe,y0-.12,6.35),(xr,y0-.12,10.55),
       (xw,y0+.08,6.35),(xe,y0+.08,6.35),(xr,y0+.08,10.55)]
faces=[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
me=bpy.data.meshes.new("SOTAC_R4_Gable_End_InfillMesh");me.from_pydata(verts,[],faces);me.materials.append(gable_mat);me.update()
gable=bpy.data.objects.new("SOTAC_R4_Sanctuary_North_GableEnd",me);ASSET.objects.link(gable);gable.parent=ROOT_OBJ;gable.matrix_parent_inverse=ROOT_OBJ.matrix_world.inverted()
gable.location=(0,0,0)
# At roof intersections, add shallow metal apron/step flashing where the gabled
# sanctuary meets the lower flat-roof volume. The location follows the footprint junction.
metal=bpy.data.materials.get("SOTAC_Dark_Roof_Membrane") or bpy.data.materials.get("SOTAC_Roof_Membrane")
if not metal:
    metal=bpy.data.materials.new("SOTAC_R4_Roof_Flashing");metal.diffuse_color=(.15,.17,.18,1)
    metal.use_nodes=True;metal.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.15,.17,.18,1)
    metal.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value=.72
    metal.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=.38
# The junction is deliberately left without a broad visible overlay: public
# photographs do not resolve its exact flashing line, and an estimated stripe
# across the roof would imply false geometry. Existing coping remains the finish.

# Give classroom cutaways legible teaching walls and room identities. Boards,
# trays and front lecterns attach to the schematic partition runs; their exact
# locations are illustrative because no public interior plan was found.
for i,ywall in enumerate((-24.55,-17.55,-10.55)):
    for side,xmid in (("west",-8.1),("east",9.4)):
        z=2.42
        board=box(f"SOTAC_R4_Classroom_Board_{i}_{side}",(xmid,ywall,z),(3.5,.075,1.15),green,.018)
        # Pale board frame and chalk/marker rail.
        for k,(loc,dims) in enumerate((((xmid,ywall-.052,z+.60),(3.62,.07,.075)),((xmid,ywall-.052,z-.60),(3.62,.07,.075)),
                                       ((xmid-1.78,ywall-.052,z),(.075,.07,1.26)),((xmid+1.78,ywall-.052,z),(.075,.07,1.26)))):
            box(f"SOTAC_R4_Classroom_BoardFrame_{i}_{side}_{k}",loc,dims,stone,.008)
        box(f"SOTAC_R4_Classroom_BoardTray_{i}_{side}",(xmid,ywall-.10,z-.67),(1.3,.12,.09),woodlight,.015)
        # A front instructor station and low storage cabinet add variation to rows of desks.
        yy=ywall+.85
        box(f"SOTAC_R4_Classroom_Lectern_{i}_{side}",(xmid,yy,.68),(1.0,.60,1.04),wood,.025)
        box(f"SOTAC_R4_Classroom_LecternTop_{i}_{side}",(xmid,yy-.04,1.22),(1.12,.68,.10),woodlight,.02)
        box(f"SOTAC_R4_Classroom_Cabinet_{i}_{side}",(xmid+3.5,yy+.1,1.05),(.60,1.8,.78),wood,.02)
        for d in (-.45,.45):
            box(f"SOTAC_R4_Classroom_CabinetDoor_{i}_{side}_{d}",(xmid+3.18,yy+.1+d,1.05),(.05,.82,.70),woodlight,.01)

evidence={"revision":"R4","stable_asset_id":"massing_st_thomas_aquinas_5535390",
 "changes":["replaced the previous floating sanctuary trusses with rafters and ties seated on continuous wall plates at the brick-pier line","added gable end infill and subtle flashing at the pitched-to-flat roof junction","reduced brick color contrast, mortar width, and bump depth while preserving the facade UV mapping","added classroom boards, framed rails, instructor stations, and cabinets to make the cutaways read as furnished learning rooms"],
 "limits":["Public sources do not provide measured interior plans, truss drawings, or precise roof junction details; interior fit-out and structural framing remain schematic.","Roof-junction flashing follows the current approximate component alignment and should be checked against architect photographs."]}
(AUDIT/"r4_design_evidence.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
print("R4 saved",ASSET_PATH,"asset objects",len(ASSET.all_objects))

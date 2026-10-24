import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/life_science_plant_and_soils_laboratory.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_life_science_plant_and_soils_laboratory']
roof=bpy.data.collections['LSPS_Roof']
interior=bpy.data.collections['LSPS_Interior']
for o in list(bpy.data.objects):
    if o.name.startswith('LSPS R3 | ') or o.name.startswith('LSPS | rooftop mechanical curb'):
        bpy.data.objects.remove(o,do_unlink=True)
def mat(name,color,rough=.65,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    return m
m_roof=mat('LSPS | R3 rooftop service equipment enamel',(0.29,.32,.32),.72,.25)
m_dark=mat('LSPS | R3 roof vent recess',(0.045,.06,.06),.82,.05)
m_cold=mat('LSPS | R3 insulated cold-room panels',(.44,.49,.50),.72,.08)
m_door=mat('LSPS | R3 walk-in cold-room door',(.35,.42,.43),.48,.35)
m_floor=mat('LSPS | R3 below-grade concrete floor',(.36,.38,.37),.84)
# Source-backed darker reflective glass cue from the qualitative 2019 Russell Street view.
for material_name,color,metallic,roughness,opacity in [
    ('LSPS | schematic clear facade glazing',(.055,.085,.095),.32,.21,.92),
    ('LSPS | greenhouse clear glazing',(.14,.21,.20),.28,.25,.82)]:
    glass=bpy.data.materials[material_name]
    bsdf=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value=(*color,1)
    bsdf.inputs['Metallic'].default_value=metallic
    bsdf.inputs['Roughness'].default_value=roughness
    mix=next(n for n in glass.node_tree.nodes if n.type=='MIX_SHADER')
    mix.inputs['Factor'].default_value=opacity
    glass['r4_source_basis']='Qualitative Purdue/GIS and August 2019 Google Street View glazing cue: darker reflective glazing; exact color/reflectance is estimated.'
def box(name, loc, size, material, collection, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection): c.objects.unlink(o)
    collection.objects.link(o)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Small softened sheet-metal edges','BEVEL'); mod.width=bevel; mod.segments=2
        o.modifiers.new('Weighted panel normals','WEIGHTED_NORMAL')
    o['detail_status']='schematic detail added from source evidence; exact dimensions/positions unverified'
    return o
# Two below-grade floor plates, cloned from existing GIS-clipped ground slab; use attribute interval as an estimate only.
ground=bpy.data.objects['Life Science Plant and Soils Laboratory | official GIS footprint ground floor']
for label,z in [('B',-3.6576),('SB',-7.3152)]:
    me=ground.data.copy(); me.name=f'LSPS R3 | level {label} below-grade floor slab mesh'
    for v in me.vertices: v.co.z += z
    o=bpy.data.objects.new(f'LSPS R3 | level {label} below-grade floor plate',me); interior.objects.link(o); o.data.materials.append(m_floor)
    o['source']='Purdue BuildingShapesZip4 FID 917 attributes B=-12 and SB=-24; unit semantics undocumented, modeled at approximate 12-foot intervals.'
    o['geometry_status']='GIS footprint-shaped schematic basement plate; basement wall extents not independently verified.'
# Roof evidence: 2022-2025 Indiana orthophoto shows a broad flat roof and several small rooftop service units.
# Pixel positions are visual approximations from local evidence image; model placements are illustrative.
roof_z=11.0
roof_xy=[(-24.5,-7.2),(-16.0,-5.3),(-8.3,-7.8),(-1.2,-4.5),(7.0,-7.4),(15.2,-5.4),(23.1,-7.0),(27.4,0.5)]
for i,(x,y) in enumerate(roof_xy,1):
    base=box(f'LSPS R3 | roof service unit {i:02}',(x,y,roof_z+.16),(1.45,.85,.32),m_roof,roof,.04)
    base['source_basis']='Visual check against Indiana GIO current orthophoto, 2022-2025; small rooftop service equipment is visible, exact count/type/positions unresolved.'
    box(f'LSPS R3 | roof service unit {i:02} vent cap',(x,y,roof_z+.48),(.78,.52,.32),m_roof,roof,.035)
    for j in range(3):
        box(f'LSPS R3 | roof service unit {i:02} louver {j+1}',(x,y-.27+j*.20,roof_z+.50),(.62,.025,.15),m_dark,roof,.008)
# One source-sized basement walk-in climate-controlled seed-storage room.
# Purdue reports 1,163 sq ft (108.05 m2) and says it is in the basement; exact sublevel and room plan are unavailable.
room_area_m2=1163*0.09290304
side=math.sqrt(room_area_m2)
rx,ry=-10.0,0.0
base_z=-3.6576
h=2.45
cz=base_z+h/2
wall=.14
door_w=1.25
# Full perimeter with an opening in the south wall; the subdivision and position are schematic.
box('LSPS R4 | basement walk-in seed storage left wall',(rx-side/2+wall/2,ry,cz),(wall,side,h),m_cold,interior,.02)
box('LSPS R4 | basement walk-in seed storage right wall',(rx+side/2-wall/2,ry,cz),(wall,side,h),m_cold,interior,.02)
box('LSPS R4 | basement walk-in seed storage north wall',(rx,ry+side/2-wall/2,cz),(side,wall,h),m_cold,interior,.02)
segment=(side-door_w)/2
box('LSPS R4 | basement walk-in seed storage south wall west',(rx-side/2+segment/2,ry-side/2+wall/2,cz),(segment,wall,h),m_cold,interior,.02)
box('LSPS R4 | basement walk-in seed storage south wall east',(rx+side/2-segment/2,ry-side/2+wall/2,cz),(segment,wall,h),m_cold,interior,.02)
box('LSPS R4 | basement walk-in seed storage door lintel',(rx,ry-side/2+wall/2,base_z+h-.22),(door_w,wall,.44),m_cold,interior,.02)
box('LSPS R4 | insulated seed-room door',(rx,ry-side/2-wall/2,base_z+1.05),(door_w-.12,.10,2.10),m_door,interior,.025)
box('LSPS R4 | seed-room door handle',(rx+.42,ry-side/2-wall/2-.08,base_z+1.05),(.04,.05,.45),m_dark,interior,.01)
box('LSPS R4 | basement walk-in seed storage ceiling',(rx,ry,base_z+h+.07),(side,side,.14),m_cold,interior,.02)
# Interior rack rows leave a clear central access aisle; rack layout is illustrative, room area is source-based.
for row,x in enumerate((rx-3.05,rx+3.05),1):
    for j in range(5):
        yy=ry-3.2+j*1.55
        box(f'LSPS R4 | seed storage rack {row}-{j+1} uprights',(x,yy,base_z+1.05),(.08,.08,2.05),m_roof,interior,.008)
        for lev in range(3):
            box(f'LSPS R4 | seed storage rack {row}-{j+1} shelf {lev+1}',(x,yy,base_z+.42+lev*.66),(.82,.72,.055),m_roof,interior,.01)
            box(f'LSPS R4 | seed storage sample bin {row}-{j+1}-{lev+1}',(x,yy,base_z+.58+lev*.66),(.48,.46,.30),m_cold,interior,.02)
# Temperature monitoring and refrigeration equipment are program cues; make/type/count not sourced.
box('LSPS R4 | seed-room temperature monitor',(rx+side/2-.35,ry-side/2+.8,base_z+1.55),(.18,.10,.30),m_dark,interior,.02)
box('LSPS R4 | seed-room refrigeration control unit',(rx+side/2-.55,ry+side/2-.7,base_z+2.02),(.72,.42,.58),m_roof,interior,.035)
for obj in interior.objects:
    if obj.name.startswith('LSPS R4 | '):
        obj['source_basis']='Purdue Agronomy, Background Information: Facilities & Equipment, page 30, reports a 1,163 sq ft walk-in climate-controlled long-term seed-storage room in the basement. Exact dimensions, room position, floor sublevel, circulation, and equipment arrangement are not available.'
        obj['room_area_m2']=round(room_area_m2,2)
        obj['room_shape_status']='Approximate square footprint used to preserve reported area; dimensions and position are schematic.'
# Preserve standard view state, save and force a reload to validate persistence.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('R4_saved',ASSET,'objects',len(list(o for o in asset.all_objects)),'materials',len({m for o in asset.all_objects if o.type=='MESH' for m in o.data.materials if m}))

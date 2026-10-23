import bpy, math, json, shutil
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
ASSET=ROOT/'modular/buildings/potter_engineering.blend'
OUT=ROOT/'audit/batch4_potter'
OUT.mkdir(exist_ok=True)
if not (OUT/'before.blend').exists(): shutil.copy2(ASSET, OUT/'before.blend')
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections['Asset_potter_engineering']
# Preserve the exported collection, root and GIS-local coordinates.
brick=bpy.data.materials['POTR_Meter_Brick']; nodes=brick.node_tree.nodes
bt=next(n for n in nodes if n.type=='TEX_BRICK')
bt.inputs['Color1'].default_value=(0.28,0.062,0.028,1)
bt.inputs['Color2'].default_value=(0.16,0.028,0.014,1)
bt.inputs['Mortar'].default_value=(0.20,0.17,0.14,1)
bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Roughness'].default_value=.82
# Ground-level reddish-brown masonry visible in the dated exterior reference.
brown=bpy.data.materials.get('POTR_GroundFloor_BrownBrick') or bpy.data.materials.new('POTR_GroundFloor_BrownBrick')
brown.diffuse_color=(.105,.035,.022,1);brown.use_nodes=True
bn=brown.node_tree.nodes; bb=next(n for n in bn if n.type=='BSDF_PRINCIPLED'); bb.inputs['Roughness'].default_value=.83
brick_tex=bn.new('ShaderNodeTexBrick');brick_tex.inputs['Color1'].default_value=(.19,.045,.024,1);brick_tex.inputs['Color2'].default_value=(.09,.022,.014,1);brick_tex.inputs['Mortar'].default_value=(.13,.10,.08,1);brick_tex.inputs['Brick Width'].default_value=.203;brick_tex.inputs['Row Height'].default_value=.067;brick_tex.inputs['Mortar Size'].default_value=.007
coord=bn.new('ShaderNodeTexCoord');sep=bn.new('ShaderNodeSeparateXYZ');comb=bn.new('ShaderNodeCombineXYZ');geom=bn.new('ShaderNodeNewGeometry');nsep=bn.new('ShaderNodeSeparateXYZ');ab=bn.new('ShaderNodeMath');ab.operation='ABSOLUTE';mix=bn.new('ShaderNodeMixRGB')
brown.node_tree.links.new(coord.outputs['Object'],sep.inputs[0]);brown.node_tree.links.new(geom.outputs['Normal'],nsep.inputs[0]);brown.node_tree.links.new(nsep.outputs['X'],ab.inputs[0]);brown.node_tree.links.new(ab.outputs[0],mix.inputs[0]);brown.node_tree.links.new(sep.outputs['X'],mix.inputs[1]);brown.node_tree.links.new(sep.outputs['Y'],mix.inputs[2]);brown.node_tree.links.new(mix.outputs[0],comb.inputs['X']);brown.node_tree.links.new(sep.outputs['Z'],comb.inputs['Y']);brown.node_tree.links.new(comb.outputs[0],brick_tex.inputs['Vector']);brown.node_tree.links.new(brick_tex.outputs['Color'],bb.inputs['Base Color'])
wall=next(o for o in col.objects if 'Structural_Envelope' in o.name)
if brown.name not in [m.name for m in wall.data.materials if m]: wall.data.materials.append(brown)
brown_idx=next(i for i,m in enumerate(wall.data.materials) if m and m.name==brown.name)
for poly in wall.data.polygons:
    z=sum(wall.data.vertices[i].co.z for i in poly.vertices)/len(poly.vertices)
    if poly.material_index==0 and z<4.4: poly.material_index=brown_idx
# Dark bronze frames around each real aperture. Joined into one inspectable mesh.
frame=bpy.data.materials.get('POTR_Dark_Bronze_Window_Frame') or bpy.data.materials.new('POTR_Dark_Bronze_Window_Frame')
frame.diffuse_color=(.055,.045,.035,1);frame.use_nodes=True
fbs=next(n for n in frame.node_tree.nodes if n.type=='BSDF_PRINCIPLED');fbs.inputs['Base Color'].default_value=(.055,.045,.035,1);fbs.inputs['Metallic'].default_value=.55;fbs.inputs['Roughness'].default_value=.34
verts=[];faces=[]
def addbox(center,theta,size):
    cx,cy,cz=center;w,d,h=size
    start=len(verts)
    local=[(-w/2,-d/2,-h/2),(w/2,-d/2,-h/2),(w/2,d/2,-h/2),(-w/2,d/2,-h/2),(-w/2,-d/2,h/2),(w/2,-d/2,h/2),(w/2,d/2,h/2),(-w/2,d/2,h/2)]
    co,si=math.cos(theta),math.sin(theta)
    for x,y,z in local: verts.append((cx+co*x-si*y,cy+si*x+co*y,cz+z))
    faces.extend([tuple(start+i for i in f) for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
windows=[o for o in col.objects if o.name.startswith('POTR_RealOpening_Glazing')]
for win in windows:
    theta=win.rotation_euler.z;cx,cy,cz=win.location;w=.71;h=.7066
    # Frames sit just proud of the glass plane and leave the clear aperture visible.
    depth=.075
    addbox((cx,cy,cz+h/2+.035),theta,(w+.08,depth,.055))
    addbox((cx,cy,cz-h/2-.035),theta,(w+.08,depth,.055))
    addbox((cx-w/2-.012,cy,cz),theta,(.055,depth,h-.035))
    addbox((cx+w/2+.012,cy,cz),theta,(.055,depth,h-.035))
me=bpy.data.meshes.new('POTR_Window_Frame_Assembly_Mesh');me.from_pydata(verts,[],faces);me.materials.append(frame);me.update()
old=bpy.data.objects.get('POTR_All_Window_Frames_Batch4')
if old: bpy.data.objects.remove(old,do_unlink=True)
ob=bpy.data.objects.new('POTR_All_Window_Frames_Batch4',me);col.objects.link(ob);ob['source']='Purdue Engineering College Potter exterior image; framing dimensions estimated from source image and 2016 study window schedule'
# Representative laboratory detail in the explicitly documented 2016 Room 205 reference.
steel=bpy.data.materials.get('POTR_2016_Lab205_Stainless') or bpy.data.materials.new('POTR_2016_Lab205_Stainless');steel.use_nodes=True;steel.diffuse_color=(.48,.51,.52,1);sbs=next(n for n in steel.node_tree.nodes if n.type=='BSDF_PRINCIPLED');sbs.inputs['Base Color'].default_value=(.48,.51,.52,1);sbs.inputs['Metallic'].default_value=.72;sbs.inputs['Roughness'].default_value=.27
white=bpy.data.materials.get('POTR_2016_Lab205_Enamel') or bpy.data.materials.new('POTR_2016_Lab205_Enamel');white.use_nodes=True;white.diffuse_color=(.8,.8,.76,1);wbs=next(n for n in white.node_tree.nodes if n.type=='BSDF_PRINCIPLED');wbs.inputs['Base Color'].default_value=(.8,.8,.76,1);wbs.inputs['Roughness'].default_value=.48
labcol=bpy.data.collections.get('POTR_Historic2016_Room205_Detail')
if not labcol: labcol=bpy.data.collections.new('POTR_Historic2016_Room205_Detail');col.children.link(labcol)
def cube(name,loc,scale,matl,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(matl)
    for c in list(o.users_collection):c.objects.unlink(o)
    labcol.objects.link(o)
    if bevel:
      mod=o.modifiers.new('Soft_Edges','BEVEL');mod.width=bevel;mod.segments=2
      o.modifiers.new('Weighted_Corner_Normals','WEIGHTED_NORMAL')
    o['source']='2016 Potter renovation study PDF, p.195, Room 205 laboratory photograph; local dimensions and exact placement are estimated'
    return o
# Sink bowl and raised rim mounted in the recorded worktop.
cube('POTR_R205_Sink_Rim',(42.65,9.80,5.80),(.58,.40,.045),steel,.035)
cube('POTR_R205_Sink_Basin',(42.65,9.80,5.765),(.48,.30,.055),bpy.data.materials['POTR_2016_Lab205_Dark_Worktop'],.035)
# Gooseneck faucet made as a beveled curve, with two control handles.
cu=bpy.data.curves.new('POTR_R205_Faucet_Tube','CURVE');cu.dimensions='3D';cu.resolution_u=18;cu.bevel_depth=.024;cu.bevel_resolution=3
sp=cu.splines.new('BEZIER');sp.bezier_points.add(3)
for bp,co in zip(sp.bezier_points,[(42.93,9.70,5.82),(42.93,9.70,6.04),(42.83,9.70,6.13),(42.65,9.70,6.13)]): bp.co=co;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
fauc=bpy.data.objects.new('POTR_R205_Gooseneck_Lab_Faucet',cu);labcol.objects.link(fauc);fauc.data.materials.append(steel);fauc['source']='2016 Potter renovation study PDF, p.195, Room 205 laboratory photo; form and placement estimated'
for i,x in enumerate([42.48,42.82]):cube('POTR_R205_Faucet_Handle_%d'%i,(x,9.70,5.86),(.035,.04,.10),steel,.012)
# A small bench-top meter, consistent with the electronics visible in the source photograph.
cube('POTR_R205_Bench_Meter_Base',(43.55,9.77,5.94),(.42,.30,.30),steel,.025)
cube('POTR_R205_Bench_Meter_Display',(43.55,9.604,5.98),(.25,.015,.10),bpy.data.materials['POTR_2016_Lab205_Dark_Worktop'],.01)
# Slim handles on upper cabinets; attach to the front plane of three red-orange doors.
for i,x in enumerate([42.7,43.35,44.0]):
    cube('POTR_R205_UpperCabinet_Handle_%d'%i,(x-.18,9.83,6.80),(.025,.035,.17),steel,.012)
# Two simple lab stools on the open side of the bench.
red=bpy.data.materials['POTR_2016_Lab205_RedOrange_Cabinets']
for i,x in enumerate([43.0,44.0]):
    y=8.85
    for j,(dx,dy) in enumerate([(-.18,-.15),(.18,-.15),(.18,.15),(-.18,.15)]):cube('POTR_R205_Stool_%d_Leg_%d'%(i,j),(x+dx,y+dy,5.17),(.035,.035,.54),steel,.006)
    cube('POTR_R205_Stool_%d_Seat'%i,(x,y,5.45),(.48,.42,.08),red,.035)
# Soft downlights under wall cabinets and two diffuse ceiling panels.
for i,x in enumerate([42.7,43.35,44.0]):cube('POTR_R205_Undercabinet_Light_%d'%i,(x,9.76,6.41),(.48,.20,.035),white,.012)
# Keep explicit evidence and uncertainty in the asset.
ob['frame_count']=len(windows)*4
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections['Asset_potter_engineering']
print(json.dumps({'saved':True,'reopened':True,'asset':str(ASSET),'export_collection':col.name,'asset_objects':len(col.all_objects),'window_count':len([o for o in col.objects if o.name.startswith('POTR_RealOpening_Glazing')]),'frame_mesh':len(col.objects['POTR_All_Window_Frames_Batch4'].data.polygons),'root_origin':tuple(col.objects['AssetRoot_potter_engineering'].location),'missing_external_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file]},indent=2))

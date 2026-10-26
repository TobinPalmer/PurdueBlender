"""Close the entrance gap in the R6 upper-glazing ribbon and style the cutaway route."""
import bpy,hashlib,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/stanley_coulter_hall.blend'
AUDIT=ROOT/'audit/batch3_stanley'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_stanley_coulter_hall']
scene=bpy.context.scene
archive=bpy.data.collections['SC_Archived_Facade_Windows_R6']
def bounds(o):
    bpy.context.view_layer.update();pts=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
def arch(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    archive.objects.link(o);o.hide_render=True;o.hide_viewport=True;o.hide_set(True)
    o['R6_status']='Replaced with the photo-supported continuous grouped upper glass band; preserved in hidden scene archive.'
def newmesh(name,verts,faces,mat):
    m=bpy.data.meshes.new(name+'_Mesh');m.from_pydata(verts,[],faces);m.materials.append(mat);m.update()
    o=bpy.data.objects.new(name,m);asset.objects.link(o);o['R6_evidence']='Current Purdue CLA photograph shows grouped high-level glazing; exact dimensions are estimated.'
    return o
def prism(name,y0,y1,z0,z1,depth,mat,xfunc):
    x0,x1=xfunc(y0),xfunc(y1);xr0,xr1=x0-depth,x1-depth
    verts=[(x0,y0,z0),(x1,y1,z0),(x1,y1,z1),(x0,y0,z1),(xr0,y0,z0),(xr1,y1,z0),(xr1,y1,z1),(xr0,y0,z1)]
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return newmesh(name,verts,faces,mat)

# R6 renders the center over the recessed entry as part of the same upper ribbon.
old_f3=[];centers=[]
for i in range(3):
    pane=bpy.data.objects.get(f'SC_Win_East_Portico_F3_{i}_GlassPane')
    if pane:
        b=bounds(pane);centers.append((b[0][1]+b[1][1])/2)
    for part in ('LimestoneTrim','BronzeFrame','GlassPane'):
        o=bpy.data.objects.get(f'SC_Win_East_Portico_F3_{i}_{part}')
        if o:old_f3.append(o.name);arch(o)
if len(old_f3)!=9:raise RuntimeError(f'Expected 9 R3 upper-east portal window parts; found {len(old_f3)}')

left=bpy.data.objects['SC_R6_East_Glazing_Band_0'];right=bpy.data.objects['SC_R6_East_Glazing_Band_1']
def endpoint(o,which):
    pts=[o.matrix_world@v.co for v in o.data.vertices]
    yval=min(p.y for p in pts) if which=='min' else max(p.y for p in pts)
    relevant=[p.x for p in pts if abs(p.y-yval)<1e-5]
    return yval,max(relevant)
yA,xA=endpoint(left,'max');yB,xB=endpoint(right,'min')
def xfunc(y):return xA+(xB-xA)*(y-yA)/(yB-yA)
y0,y1=yA,yB
if y1-y0<7.5:raise RuntimeError(f'Unexpected portal gap width: {y0}..{y1}')
glass=bpy.data.materials['Architectural_Glazing'];bronze=bpy.data.materials['Dark_Bronze_Framing'];limestone=bpy.data.materials['Bedford_Indiana_Limestone']
created=[prism('SC_R6_East_Glazing_Band_Entry',y0,y1,10.04,11.96,0.035,glass,xfunc),
         prism('SC_R6_East_Glazing_Head_Entry',y0,y1,11.98,12.12,0.20,limestone,xfunc),
         prism('SC_R6_East_Glazing_Sill_Entry',y0,y1,9.88,10.02,0.20,limestone,xfunc)]
for i,yc in enumerate(centers):
    yf0,yf1=yc-0.035,yc+0.035;xf=xfunc(yc)+0.015
    verts=[(xf,yf0,10.04),(xf,yf1,10.04),(xf,yf1,11.96),(xf,yf0,11.96),(xf-.07,yf0,10.04),(xf-.07,yf1,10.04),(xf-.07,yf1,11.96),(xf-.07,yf0,11.96)]
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    created.append(newmesh(f'SC_R6_East_Glazing_Mullion_Entry_{i}',verts,faces,bronze))

# Make the schematic circulation route legible without assigning a false finish.
route=bpy.data.objects.get('SC_R6_Circulation_Spine_Floor')
if not route:raise RuntimeError('R6 circulation spine floor missing')
route_mat=bpy.data.materials.get('SC_R6_Circulation_Terrazzo_Schematic')
if not route_mat:
    route_mat=bpy.data.materials.new('SC_R6_Circulation_Terrazzo_Schematic');route_mat.diffuse_color=(0.62,0.48,0.28,1);route_mat.use_nodes=True
bs=next((n for n in route_mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
if bs:bs.inputs['Base Color'].default_value=(0.62,0.48,0.28,1);bs.inputs['Roughness'].default_value=.82
route.data.materials.clear();route.data.materials.append(route_mat)
route_mat['status']='Neutral schematic route tint for the review cutaway only; current floor finish unverified.'

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
result={'asset':str(ASSET),'sha256':sha,'archived_portico_f3_objects':old_f3,'center_band_gap_m':y1-y0,'center_mullion_centers_m':centers,'added_objects':[o.name for o in created],'continuous_upper_glazing':'Two main groups and an entry-center band now join into one continuous photo-supported upper glazed band with narrow mullions.','route_finish':'Differentiated neutral schematic floor tint; no as-built flooring claim.','upper_facade_window_archive_count':len(archive.all_objects)}
(AUDIT/'grouped_glazing_r6.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

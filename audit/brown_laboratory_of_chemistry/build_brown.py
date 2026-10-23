import bpy, bmesh, math, json, os
from pathlib import Path
from mathutils import Vector, Quaternion

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
SOURCE = ROOT / 'modular/buildings/massing_brown_laboratory_of_chemistry_brwn_aed3885.blend'
OUTPUT = ROOT / 'modular/buildings/brown_laboratory_of_chemistry.blend'
AUDIT = ROOT / 'audit/brown_laboratory_of_chemistry'
AUDIT.mkdir(parents=True, exist_ok=True)
ASSET_ID='brown_laboratory_of_chemistry'
COLLECTION_NAME='Asset_brown_laboratory_of_chemistry'
SCENE_NAME='Building_brown_laboratory_of_chemistry'

# Preserve source-derived coordinates and faces only; the massing library is never saved.
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
src=bpy.context.scene.objects.get('Brown Laboratory of Chemistry (BRWN)')
if src is None: raise RuntimeError('Source massing object not found')
mesh=src.data
xs=[v.co.x for v in mesh.vertices]; ys=[v.co.y for v in mesh.vertices]
origin_x=(min(xs)+max(xs))*0.5; origin_y=(min(ys)+max(ys))*0.5
height=max(v.co.z for v in mesh.vertices)
# Exterior perimeter edges are the base edges of vertical facade faces.
perim=set()
for poly in mesh.polygons:
    ids=list(poly.vertices)
    zs=[mesh.vertices[i].co.z for i in ids]
    if min(zs)>1e-5 or max(zs)<1e-4: continue
    bottom=[i for i in ids if abs(mesh.vertices[i].co.z)<1e-5]
    if len(bottom)==2: perim.add(tuple(sorted(bottom)))
    elif len(bottom)>2:
        for a,b in zip(bottom,bottom[1:]+bottom[:1]):
            if (mesh.vertices[a].co-mesh.vertices[b].co).length>1e-4: perim.add(tuple(sorted((a,b))))
adj={}
for a,b in perim: adj.setdefault(a,set()).add(b); adj.setdefault(b,set()).add(a)
if not adj or any(len(ns)!=2 for ns in adj.values()): raise RuntimeError('Could not recover a single closed exterior perimeter')
start=min(adj,key=lambda i:(mesh.vertices[i].co.x,mesh.vertices[i].co.y))
loop=[start]; prev=None; cur=start
while True:
    opts=sorted(adj[cur]-({prev} if prev is not None else set()))
    nxt=opts[0]
    if nxt==start: break
    if nxt in loop: raise RuntimeError('Perimeter loop repeated before closing')
    loop.append(nxt); prev,cur=cur,nxt
    if len(loop)>len(adj)+1: raise RuntimeError('Perimeter traversal overflow')
pts=[Vector((mesh.vertices[i].co.x-origin_x,mesh.vertices[i].co.y-origin_y)) for i in loop]
# Collapse almost-collinear source tessellation vertices, preserving all meaningful corners.
changed=True
while changed and len(pts)>4:
    changed=False
    for i in range(len(pts)):
        a=pts[i]-pts[i-1]; b=pts[(i+1)%len(pts)]-pts[i]
        if a.length>0 and b.length>0 and a.dot(b)>0 and abs(a.x*b.y-a.y*b.x)<max(a.length,b.length)*0.075:
            pts.pop(i); changed=True; break
centroid=sum(pts,Vector((0,0)))/len(pts)
def point_in_footprint(x,y):
    inside=False
    for a,b in zip(pts,pts[1:]+pts[:1]):
        if ((a.y>y)!=(b.y>y)) and x < (b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x:
            inside=not inside
    return inside
def point_on_footprint(x,y,tol=1e-5):
    p=Vector((x,y))
    for a,b in zip(pts,pts[1:]+pts[:1]):
        ab=b-a
        if ab.length_squared==0: continue
        t=max(0.0,min(1.0,(p-a).dot(ab)/ab.length_squared))
        if (p-(a+ab*t)).length<=tol: return True
    return point_in_footprint(x,y)
def horizontal_inside_intervals(y,xlo,xhi):
    cuts=[xlo,xhi]
    for a,b in zip(pts,pts[1:]+pts[:1]):
        if (a.y<=y<b.y) or (b.y<=y<a.y): cuts.append(a.x+(y-a.y)*(b.x-a.x)/(b.y-a.y))
        elif abs(a.y-y)<1e-8: cuts.append(a.x)
        elif abs(b.y-y)<1e-8: cuts.append(b.x)
    cuts=sorted(set(max(xlo,min(xhi,x)) for x in cuts if xlo-1e-8<=x<=xhi+1e-8))
    return [(a,b) for a,b in zip(cuts[:-1],cuts[1:]) if b-a>1e-6 and point_in_footprint((a+b)/2,y)]
def vertical_inside_intervals(x,ylo,yhi):
    cuts=[ylo,yhi]
    for a,b in zip(pts,pts[1:]+pts[:1]):
        if (a.x<=x<b.x) or (b.x<=x<a.x): cuts.append(a.y+(x-a.x)*(b.y-a.y)/(b.x-a.x))
        elif abs(a.x-x)<1e-8: cuts.append(a.y)
        elif abs(b.x-x)<1e-8: cuts.append(b.y)
    cuts=sorted(set(max(ylo,min(yhi,y)) for y in cuts if ylo-1e-8<=y<=yhi+1e-8))
    return [(a,b) for a,b in zip(cuts[:-1],cuts[1:]) if b-a>1e-6 and point_in_footprint(x,(a+b)/2)]
def intersect_intervals(left,right):
    out=[]
    for a,b in left:
        for c,d in right:
            lo=max(a,c); hi=min(b,d)
            if hi>lo+1e-6: out.append((lo,hi))
    return out
# Source top triangulation describes the official polygon footprint.
top_faces=[]
for poly in mesh.polygons:
    if all(abs(mesh.vertices[i].co.z-height)<1e-5 for i in poly.vertices):
        for tri in poly.loop_triangles if hasattr(poly,'loop_triangles') else []: pass
        ids=list(poly.vertices)
        if len(ids)==3: top_faces.append([ids[0],ids[1],ids[2]])
        elif len(ids)>3:
            for k in range(1,len(ids)-1): top_faces.append([ids[0],ids[k],ids[k+1]])
source_local_vertices=[(float(v.co.x-origin_x),float(v.co.y-origin_y),float(v.co.z)) for v in mesh.vertices]
# Build the standalone scene cleanly, with no link to the source massing library.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.name=SCENE_NAME
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1.0
collection=bpy.data.collections.new(COLLECTION_NAME); scene.collection.children.link(collection)
collection['building_id']=ASSET_ID
collection['placement_origin_xy_m']=[origin_x,origin_y]
collection['coordinate_frame']='local; master placement marker supplies campus XY origin'
collection['source_massing_id']='massing_brown_laboratory_of_chemistry_brwn_aed3885'
root=bpy.data.objects.new('AssetRoot_brown_laboratory_of_chemistry',None)
root.empty_display_type='PLAIN_AXES'; root.empty_display_size=2.0
collection.objects.link(root)

# Procedural materials: all image-free and portable with the .blend.
def mat_principled(name,color,rough=0.75,metal=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    return m
def brick_material(name,along):
    m=mat_principled(name,(.40,.145,.093),.84)
    nt=m.node_tree; bs=nt.nodes.get('Principled BSDF')
    pos=nt.nodes.new('ShaderNodeNewGeometry'); sep=nt.nodes.new('ShaderNodeSeparateXYZ'); comb=nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(pos.outputs['Position'],sep.inputs['Vector'])
    nt.links.new(sep.outputs['X' if along=='X' else 'Y'],comb.inputs['X']); nt.links.new(sep.outputs['Z'],comb.inputs['Y'])
    bt=nt.nodes.new('ShaderNodeTexBrick'); bt.inputs['Scale'].default_value=1.0; bt.inputs['Brick Width'].default_value=.23; bt.inputs['Row Height'].default_value=.072; bt.inputs['Mortar Size'].default_value=.016; bt.inputs['Mortar Smooth'].default_value=.012
    bt.inputs['Color1'].default_value=(.49,.195,.125,1); bt.inputs['Color2'].default_value=(.34,.095,.061,1); bt.inputs['Mortar'].default_value=(.16,.115,.09,1)
    nt.links.new(comb.outputs['Vector'],bt.inputs['Vector'])
    noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=38; noise.inputs['Detail'].default_value=2.2; nt.links.new(pos.outputs['Position'],noise.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(.72,.63,.56,1); ramp.color_ramp.elements[1].color=(1.0,.96,.91,1)
    nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac']); mix=nt.nodes.new('ShaderNodeMixRGB'); mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=.18
    nt.links.new(bt.outputs['Color'],mix.inputs[1]); nt.links.new(ramp.outputs['Color'],mix.inputs[2]); nt.links.new(mix.outputs['Color'],bs.inputs['Base Color'])
    bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.28; bump.inputs['Distance'].default_value=.012; nt.links.new(bt.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return m
brick_x=brick_material('BRWN | running-bond brick on east-west elevations','X')
brick_y=brick_material('BRWN | running-bond brick on north-south elevations','Y')
concrete=mat_principled('BRWN | pale cast concrete',(.82,.79,.72),.82)
nt=concrete.node_tree; bs=nt.nodes.get('Principled BSDF'); noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=135; noise.inputs['Detail'].default_value=3; noise.inputs['Roughness'].default_value=.75
ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.22; ramp.color_ramp.elements[0].color=(.56,.54,.49,1); ramp.color_ramp.elements[1].position=.78; ramp.color_ramp.elements[1].color=(.81,.78,.70,1); nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
b=nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value=.15; b.inputs['Distance'].default_value=.012; nt.links.new(noise.outputs['Fac'],b.inputs['Height']); nt.links.new(b.outputs['Normal'],bs.inputs['Normal'])
glass=mat_principled('BRWN | blue-gray reflective glazing',(.035,.075,.095),.18,.24)
gs=glass.node_tree.nodes.get('Principled BSDF'); gs.inputs['IOR'].default_value=1.46
frame=mat_principled('BRWN | dark bronze window frames',(.16,.17,.16),.43,.35)
interior_wall=mat_principled('BRWN | warm off-white interior plaster',(.72,.71,.66),.88)
interior_floor=mat_principled('BRWN | lab resilient flooring',(.43,.46,.44),.77)
corridor_floor=mat_principled('BRWN | corridor terrazzo',(.53,.52,.47),.52)
steel=mat_principled('BRWN | stainless steel',(.44,.49,.50),.3,.72)
cabinet=mat_principled('BRWN | laboratory casework',(.68,.70,.68),.55,.05)
hood=mat_principled('BRWN | fume hood enamel',(.74,.74,.69),.88,.0)
hood_bs=hood.node_tree.nodes.get('Principled BSDF')
if 'Specular IOR Level' in hood_bs.inputs: hood_bs.inputs['Specular IOR Level'].default_value=0.0
black=mat_principled('BRWN | equipment dark details',(.055,.065,.068),.35,.18)
wood=mat_principled('BRWN | warm wood accents',(.34,.22,.12),.72)
white=mat_principled('BRWN | white painted metal',(.86,.87,.84),.34,.1)
yellow=mat_principled('BRWN | magnet access boundary tape',(.88,.58,.07),.55,.04)
screen_mat=mat_principled('BRWN | instrument control display',(.025,.24,.27),.22,.1)
screen_bs=screen_mat.node_tree.nodes.get('Principled BSDF')
if 'Emission Color' in screen_bs.inputs:
    screen_bs.inputs['Emission Color'].default_value=(.03,.42,.45,1); screen_bs.inputs['Emission Strength'].default_value=.45
red=mat_principled('BRWN | safety red indicator',(.7,.025,.012),.3,.05)
contained_materials={interior_wall,interior_floor,corridor_floor,steel,cabinet,hood,black,wood,white,screen_mat,yellow,red}

# Efficient mesh builder for repeated architectural elements.
class Batch:
    def __init__(self,name,material): self.name=name; self.material=material; self.verts=[]; self.faces=[]
    def box(self,c,t,n,dt,dn,dz):
        c=Vector(c); t=Vector(t).normalized(); n=Vector(n).normalized()
        if self.material in contained_materials:
            if abs(t.x)>.999 and abs(n.y)>.999:
                xlo,xhi=c.x-dt/2,c.x+dt/2
                intervals=horizontal_inside_intervals(c.y,xlo,xhi)
                intervals=intersect_intervals(intervals,horizontal_inside_intervals(c.y-dn/2,xlo,xhi))
                intervals=intersect_intervals(intervals,horizontal_inside_intervals(c.y+dn/2,xlo,xhi))
                for lo,hi in intervals:
                    lo+=.01; hi-=.01
                    if hi-lo>.12: self._append_box(( (lo+hi)/2,c.y,c.z),t,n,hi-lo,dn,dz)
                return
            if abs(t.y)>.999 and abs(n.x)>.999:
                ylo,yhi=c.y-dt/2,c.y+dt/2
                intervals=vertical_inside_intervals(c.x,ylo,yhi)
                intervals=intersect_intervals(intervals,vertical_inside_intervals(c.x-dn/2,ylo,yhi))
                intervals=intersect_intervals(intervals,vertical_inside_intervals(c.x+dn/2,ylo,yhi))
                for lo,hi in intervals:
                    lo+=.01; hi-=.01
                    if hi-lo>.12: self._append_box((c.x,(lo+hi)/2,c.z),t,n,hi-lo,dn,dz)
                return
        self._append_box(c,t,n,dt,dn,dz)
    def _append_box(self,c,t,n,dt,dn,dz):
        c=Vector(c); t=Vector(t).normalized(); n=Vector(n).normalized()
        base=len(self.verts)
        for z in (-dz/2,dz/2):
            for vv in (-dn/2,dn/2):
                for uu in (-dt/2,dt/2):
                    p=Vector((c.x+t.x*uu+n.x*vv, c.y+t.y*uu+n.y*vv, c.z+z)); self.verts.append(tuple(p))
        # bottom, top, and four walls; normals are recalculated at mesh creation.
        self.faces.extend([(base+0,base+1,base+3,base+2),(base+4,base+6,base+7,base+5),(base+0,base+4,base+5,base+1),(base+1,base+5,base+7,base+3),(base+3,base+7,base+6,base+2),(base+2,base+6,base+4,base+0)])
    def finish(self):
        if not self.faces: return None
        me=bpy.data.meshes.new(self.name+'_Mesh'); me.from_pydata(self.verts,[],self.faces); me.materials.append(self.material); me.update()
        bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free(); me.update()
        ob=bpy.data.objects.new(self.name,me); collection.objects.link(ob); ob.parent=root
        return ob

brick_bx=Batch('Exterior_Brickwork_EW',brick_x); brick_by=Batch('Exterior_Brickwork_NS',brick_y)
conc_b=Batch('Exterior_Concrete_Piers_and_Coping',concrete)
glass_b=Batch('Exterior_Glazing',glass); frame_b=Batch('Exterior_Window_Frames',frame)
interior_b=Batch('Interior_Partitions',interior_wall); case_b=Batch('Interior_Casework',cabinet)
top_b=Batch('Interior_Countertops',steel); hood_b=Batch('Interior_Fume_Hoods',hood)
detail_b=Batch('Interior_Fittings_and_Equipment',black); white_b=Batch('Interior_Painted_Metal',white)
wood_b=Batch('Interior_Wood',wood)
display_b=Batch('NMR_Control_Displays',screen_mat); safety_b=Batch('NMR_Safety_Boundaries',yellow)
indicator_b=Batch('NMR_Emergency_Stops',red)
up=Vector((0,0,1))
# Any segment normal is picked outward from the footprint centroid.
def outward(a,b):
    d=(b-a).normalized(); n=Vector((d.y,-d.x))
    if n.dot((a+b)*.5-centroid)<0: n=-n
    return d,n

def box2(batch,tangent,norm,center,z,d1,d2,dz): batch.box((center[0],center[1],z),tangent,norm,d1,d2,dz)

# Exterior wall panels. Short projecting 3 m bays from the footprint are rendered as the pale concrete piers seen in the reference photo.
story=3.2; wall_depth=.48; ground_to_roof=height
segments=[]
for i,a in enumerate(pts):
    b=pts[(i+1)%len(pts)]
    if (b-a).length<.2: continue
    t,n=outward(a,b); L=(b-a).length; mid=(a+b)*.5
    segments.append((a,b,t,n,L,mid))
    is_pier=(2.3<=L<=4.2 and abs(t.x)>.86) or (L<=1.8 and abs(t.y)>.86)
    batch=conc_b if is_pier else (brick_bx if abs(t.x)>abs(t.y) else brick_by)
    # Repeated laboratory windows fit each long bay; doors occupy the central south entry bay.
    count=max(1,int(round(L/2.9))) if L>4.6 else 0
    cell=L/count if count else L
    for floor in range(5):
        z0=floor*story; ztop=min(z0+story,ground_to_roof); H=ztop-z0
        if H<.2: continue
        if not count or is_pier:
            box2(batch,t,n,mid,z0+H/2,L,wall_depth,H)
        else:
            for k in range(count):
                s0=k*cell; sm=s0+cell/2
                c2=a+t*sm
                cx=c2.x
                south_entry=(floor==0 and n.y<-.7 and abs(c2.y-(-16.9))<2.0 and -3.0<cx<8.0)
                if south_entry:
                    # masonry left/right of a recessed pair of entry leaves
                    doorw=min(2.35,cell*.82); jamb=max(.12,(cell-doorw)/2)
                    box2(batch,t,n,c2,z0+(H-2.55)/2,jamb,wall_depth,H)
                    # soffit above the opening
                    if H>2.65: box2(batch,t,n,c2,z0+H-.2,cell,wall_depth,.4)
                    # pale stone portal, double glazed leaves and transom
                    for side in (-1,1): box2(conc_b,t,n,c2+t*(side*doorw*.53),z0+1.38,.18,.45,2.76)
                    box2(conc_b,t,n,c2,z0+2.78,doorw+.22,.45,.22)
                    box2(glass_b,t,n,c2,z0+1.27,doorw-.18,.08,2.30)
                    box2(frame_b,t,n,c2+t*(-.36),z0+1.27,.07,.12,2.3)
                    box2(frame_b,t,n,c2+t*(.36),z0+1.27,.07,.12,2.3)
                    box2(frame_b,t,n,c2,z0+1.24,doorw-.18,.12,.07)
                    box2(frame_b,t,n,c2,z0+2.39,doorw-.18,.12,.07)
                    box2(frame_b,t,n,c2,z0+1.27,.06,.12,2.25)
                    # recessed canopy and stair landing
                    box2(conc_b,t,n,c2,z0+3.10,3.7,1.6,.25)
                    continue
                if floor==0 and (k%3==2 or is_pier):
                    # Low, restricted first-floor opening rhythm as seen in the exterior reference.
                    box2(batch,t,n,c2,z0+H/2,cell,wall_depth,H)
                    continue
                ww=min(1.02,cell*.58); sill=.58 if floor else .50; wh=min(2.20,H-sill-.35)
                side=(cell-ww)*.5
                if side>.02:
                    box2(batch,t,n,c2-t*(ww/2+side/2),z0+H/2,side,wall_depth,H)
                    box2(batch,t,n,c2+t*(ww/2+side/2),z0+H/2,side,wall_depth,H)
                if sill>.02: box2(batch,t,n,c2,z0+sill/2,ww,wall_depth,sill)
                top_h=max(.05,H-sill-wh)
                if top_h>.02: box2(batch,t,n,c2,z0+sill+wh+top_h/2,ww,wall_depth,top_h)
                wz=z0+sill+wh/2
                box2(glass_b,t,n,c2,wz,ww-.14,.075,wh-.14)
                # Deep jambs and bronze mullions inside the glazed opening.
                for side_s in (-1,1): box2(frame_b,t,n,c2+t*(side_s*(ww/2-.035)),wz,.07,.15,wh)
                box2(frame_b,t,n,c2,wz,ww,.15,.07)
                box2(frame_b,t,n,c2,z0+sill+wh-.035,ww,.15,.07)
                box2(frame_b,t,n,c2+t*(-ww*.19),wz,.045,.12,wh-.12)
                box2(frame_b,t,n,c2,wz-.30,ww-.12,.12,.045)
    # structural bay/cornice detail at projecting white concrete piers
    if is_pier:
        box2(conc_b,t,n,mid,ground_to_roof+.45,L,wall_depth+.18,.9)

# Continuous floor plates from the official polygon triangulation, including the basement level.
def floor_mesh(name,z,material):
    used=sorted({i for f in top_faces for i in f})
    idx={v:k for k,v in enumerate(used)}
    verts=[]
    for i in used:
        v=source_local_vertices[i]
        verts.append((v[0],v[1],z))
    faces=[[idx[i] for i in f] for f in top_faces]
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    # Smooth cylindrical side quads; keep the end caps flat.
    for poly in me.polygons:
        poly.use_smooth=(len(poly.vertices)==4)
    # Smooth only the cylindrical side quads; flat caps preserve the machined rims.
    for poly in me.polygons:
        poly.use_smooth=(len(poly.vertices)==4)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();me.update()
    ob=bpy.data.objects.new(name,me);collection.objects.link(ob);ob.parent=root
    mod=ob.modifiers.new('Structural slab 180 mm','SOLIDIFY');mod.thickness=.18;mod.offset=-1.0
    return ob
for lev in [-3.2,0.0,3.2,6.4,9.6,12.8,16.0]:
    floor_mesh('Floor_plate_'+str(lev).replace('.','_')+'m',lev,interior_floor if lev<16 else concrete)

# Roof parapet, coping, lab exhausts and mechanical penthouses. Rooftop plant is a documented inference from the lab use.
for a,b,t,n,L,mid in segments:
    box2(conc_b,t,n,mid,ground_to_roof+.16,L,.42,.28)
# roof HVAC zones over the long lab wings
for x in [-38,-25,-12,2,16,30,43]:
    for y in (-10.0,10.0):
        case_b.box((x,y,ground_to_roof+.75),(1,0,0),(0,1,0),4.0,2.6,1.25)
        top_b.box((x,y,ground_to_roof+1.41),(1,0,0),(0,1,0),4.05,2.65,.08)
        for k in range(3):
            detail_b.box((x-1.2+k*1.2,y,ground_to_roof+1.65),(1,0,0),(0,1,0),.28,.3,.42)
for x in [-45,-31,-18,-4,10,24,38,50]:
    for y in (-12.5,12.5):
        # chemistry exhaust stack, elevated above roof with a weather cap
        hood_b.box((x,y,ground_to_roof+1.35),(1,0,0),(0,1,0),.55,.55,2.7)
        steel # (material is also used for visible equipment)
        top_b.box((x,y,ground_to_roof+2.75),(1,0,0),(0,1,0),.82,.82,.12)

# Floor-by-floor room divisions are traced approximately from Purdue's published BRWN plans.
# The plan scans are schematic and lack a scale bar tied to the supplied GIS polygon, so these
# partitions follow visible room/core relationships while retaining the source footprint.
xmin=-53.0; xmax=53.0
floor_layouts=[
 {'north':[-53,-46,-40,-34,-29,-23,-17,-12,-6,1,8,15,22,29,37,45,53],
  'south':[-53,-46,-39,-32,-26,-20,-14,-8,-2,5,12,19,26,33,40,47,53],
  'office_n':[(-19,-5),(-1,8)],'office_s':[(-20,-13),(25,35)],'hoodskip':[(-19,-5),(-1,8),(25,35)]},
 {'north':[-53,-47,-42,-36,-30,-23,-16,-9,-2,5,12,19,27,35,43,49,53],
  'south':[-53,-47,-41,-35,-29,-23,-17,-11,-5,2,9,16,23,30,38,46,53],
  'office_n':[(-53,-39)],'office_s':[(-53,-38)],'hoodskip':[(-53,-38),(46,53)]},
 {'north':[-53,-48,-43,-38,-32,-26,-20,-14,-8,-2,5,12,19,26,33,40,47,53],
  'south':[-53,-47,-41,-35,-29,-23,-17,-11,-5,2,9,16,23,30,37,44,50,53],
  'office_n':[(-53,-37)],'office_s':[(-53,-35),(29,47)],'hoodskip':[(-53,-35),(29,47),(4,20)]},
 {'north':[-53,-48,-43,-38,-32,-26,-20,-14,-8,-2,5,12,19,26,33,40,47,53],
  'south':[-53,-47,-41,-35,-29,-23,-17,-11,-5,2,9,16,23,30,37,44,50,53],
  'office_n':[(-53,-39)],'office_s':[(-53,-38),(-9,0),(32,41)],'hoodskip':[(-53,-38),(32,41)]},
 {'north':[-53,-48,-43,-38,-33,-28,-23,-18,-13,-8,-2,5,12,19,26,33,40,47,53],
  'south':[-53,-47,-41,-35,-29,-23,-17,-11,-5,2,9,16,23,30,37,44,50,53],
  'office_n':[(-53,-39),(38,53)],'office_s':[(-53,-38),(6,15),(38,48)],'hoodskip':[(-53,-38),(38,53)]}
]
def overlap(a,b,spans): return any(a < hi and b > lo for lo,hi in spans)
# Dimension checks for modeled corridor openings: door leaves stay inside their openings,
# and the divider grid cannot cross a corridor door (door centers are bay midpoints).
door_opening_width=1.12; door_leaf_width=.92; divider_half_width=.07
assert door_leaf_width < door_opening_width
assert min(abs((a+b)/2-x) for layout in floor_layouts for key in ('north','south')
           for a,b in zip(layout[key][:-1],layout[key][1:])
           for x in layout[key][1:-1]) > door_leaf_width/2 + divider_half_width
assert -27.8 < -27.0-door_leaf_width/2 < -27.0+door_leaf_width/2 < -26.2
for floor,layout in enumerate(floor_layouts):
    z=floor*story
    corridor_batch=Batch(f'Corridor_finish_{floor+1}',corridor_floor)
    corridor_batch.box((0,0,z+.10),(1,0,0),(0,1,0),xmax-xmin,3.6,.025); corridor_batch.finish()
    for side in (-1,1):
        y=side*2.0
        # Corridor wall openings are aligned to the actual (floor-specific) room module rhythm.
        centers=(layout['north'] if side>0 else layout['south'])
        door_centers=[(a+b)/2 for a,b in zip(centers[:-1],centers[1:])]
        cursor=xmin
        for dc in door_centers:
            lo=max(xmin,dc-.56); hi=min(xmax,dc+.56)
            if lo>cursor: interior_b.box(((cursor+lo)/2,y,z+1.42),(1,0,0),(0,1,0),lo-cursor,.14,2.84)
            cursor=max(cursor,hi)
        if cursor<xmax: interior_b.box(((cursor+xmax)/2,y,z+1.42),(1,0,0),(0,1,0),xmax-cursor,.14,2.84)
        divisions=centers
        for xx in divisions[1:-1]:
            # Keep a 0.9 m gap at the corridor end of each room divider so the modeled doorways
            # stay clear. Room partitions begin beyond the corridor wall and do not cross door leaves.
            if side>0:
                interior_b.box((xx,(3.9+17.7)/2,z+1.42),(0,1,0),(1,0,0),13.8,.14,2.84)
            else:
                interior_b.box((xx,(-17.7-3.9)/2,z+1.42),(0,1,0),(1,0,0),13.8,.14,2.84)
        # Rooms with offices, conference, teaching or shared functions receive an additional
        # cross-partition so those plan zones are not furnished as generic lab bays.
        nspans=layout['office_n'] if side>0 else layout['office_s']
        for lo,hi in nspans:
            for yy in (side*7.0,side*12.3):
                interior_b.box(((lo+hi)/2,yy,z+1.42),(1,0,0),(0,1,0),hi-lo,.12,2.84)
        # Furniture scale adapts to each floor's own irregular room widths and role.
        for lo,hi in zip(divisions[:-1],divisions[1:]):
            width=hi-lo
            if width<3.3 or overlap(lo,hi,nspans): continue
            cx=(lo+hi)/2
            lab_rows=(side*6.2,side*10.6)
            for row,yy in enumerate(lab_rows):
                if width>5.0:
                    benchw=min(width*.62,4.6)
                    case_b.box((cx,yy,z+.49),(1,0,0),(0,1,0),benchw,.66,.78)
                    top_b.box((cx,yy,z+.91),(1,0,0),(0,1,0),benchw+.20,.84,.07)
                    for k in range(3):
                        xx=cx+(k-1)*benchw*.28
                        detail_b.box((xx,yy-side*.34,z+.42),(1,0,0),(0,1,0),.54,.03,.50)
                if row==0 and width>6.0 and not overlap(lo,hi,layout['hoodskip']):
                    hx=cx; hy=side*14.8
                    hood_b.box((hx,hy,z+1.2),(1,0,0),(0,1,0),min(2.2,width*.48),1.0,2.25)
                    top_b.box((hx,hy,z+2.37),(1,0,0),(0,1,0),min(2.4,width*.52),1.12,.12)
                    glass_b.box((hx,hy-side*.53,z+1.4),(1,0,0),(0,1,0),min(1.65,width*.38),.045,1.25)
        # Door leaves are centered in actual rooms and sit wholly inside the corridor-wall openings.
        for dc in door_centers:
            detail_b.box((dc,side*2.0,z+1.05),(1,0,0),(0,1,0),.92,.045,2.1)
            for jamb_x in (dc-.50,dc+.50):
                frame_b.box((jamb_x,side*2.0,z+1.08),(1,0,0),(0,1,0),.055,.18,2.18)
    # Repeated central stairs/lifts line up, with smaller side cores at ends as shown on plans.
    for sx in (-43.0,-7.0,20.0,47.0):
        interior_b.box((sx,0,z+1.42),(0,1,0),(1,0,0),2.8,.18,2.84)
        detail_b.box((sx,1.62,z+1.15),(0,1,0),(1,0,0),1.20,.04,2.25)
        frame_b.box((sx,1.66,z+1.15),(0,1,0),(1,0,0),1.3,.08,2.35)
    # Floor-specific special rooms drawn from the labeled campus plan sheets.
    if floor==0: # first: north-center general chemistry/journal, south-center server/TA rooms
        for x,y,w,d in [(-13,10,8,4),(3,10,7,4),(-13,-10,6,3),(30,-10,7,4)]:
            wood_b.box((x,y,z+.78),(1,0,0),(0,1,0),w,d,.12)
    elif floor==1: # second: west main office/copy and east organic preparation rooms
        for x,y,w,d in [(-46,8,7,2),(-46,-9,7,2),(49,9,5,2),(10,-9,8,2)]:
            case_b.box((x,y,z+.48),(1,0,0),(0,1,0),w,d,.75)
            top_b.box((x,y,z+.88),(1,0,0),(0,1,0),w+.1,d+.1,.08)
    elif floor==2: # third: instrument facility and analytical teaching suites
        for x in (8,13,18):
            case_b.box((x,11,z+.55),(1,0,0),(0,1,0),2.4,.8,.95)
        for x in (32,38,44):
            wood_b.box((x,-10,z+.78),(1,0,0),(0,1,0),4.3,1.15,.12)
    elif floor==3: # fourth: west conference rooms and south instrument suite
        for x in (-49,-43): wood_b.box((x,10,z+.78),(1,0,0),(0,1,0),4.5,1.3,.12)
        for x in (-6,1,8): case_b.box((x,-10,z+.52),(1,0,0),(0,1,0),3.2,.75,.9)
    else: # fifth: west instrument room and clustered east/central offices
        for x in (-50,-45,-40): case_b.box((x,10,z+.55),(1,0,0),(0,1,0),2.1,.8,.95)
        for x in (9,16,42): wood_b.box((x,-10,z+.78),(1,0,0),(0,1,0),4.0,1.2,.12)

# Ground-level entrance glazing and steps at the south center entry.
entry_stairs=Batch('Entry_Stairs',concrete)
for i in range(5):
    # stair treads drop south from entry, broad enough for the central vestibule
    entry_stairs.box((2.0,-18.0-i*.34,.10+i*.08),(1,0,0),(0,1,0),4.8,.34,.16)

# A basement NMR / instrument-room vignette tied to BRWN B124 and the official basement plan.
# Walls and benches are laid out below grade; those spaces are not visible above ground.
base=-3.2
# BRWN basement plan places the labeled NMR/L8124 suite on the north-west wing.
# Its south wall fronts the long basement corridor; west/east walls enclose a large instrument room.
interior_b.box((-31.275,.35,base+1.35),(1,0,0),(0,1,0),6.95,.14,2.7)
interior_b.box((-22.725,.35,base+1.35),(1,0,0),(0,1,0),6.95,.14,2.7)
detail_b.box((-27.0,.35,base+1.05),(1,0,0),(0,1,0),1.05,.045,2.1)
for door_x in (-27.70,-26.30):
    frame_b.box((door_x,.35,base+1.08),(1,0,0),(0,1,0),.055,.18,2.18)
interior_b.box((-27.0,16.65,base+1.35),(1,0,0),(0,1,0),15.5,.14,2.7)
interior_b.box((-34.75,8.5,base+1.35),(0,1,0),(1,0,0),16.3,.14,2.7)
interior_b.box((-19.25,8.5,base+1.35),(0,1,0),(1,0,0),16.3,.14,2.7)
# The official plan shows a continuous corridor and room sequence along the south basement wing.
basement_corridor=Batch('Basement_Corridor_finish',corridor_floor)
basement_corridor.box((5,-2.0,base+.10),(1,0,0),(0,1,0),103,.14,.025); basement_corridor.finish()
interior_b.box((4,-2.55,base+1.35),(1,0,0),(0,1,0),98,.14,2.7)
for xx in (-37,-29,-21,-13,-5,3,11,19,27,35,43,51):
    interior_b.box((xx,-10.0,base+1.35),(0,1,0),(1,0,0),13.8,.14,2.7)
# West-end prep lab/chemical storage is called out separately on the official basement sheet.
interior_b.box((-46,-3.2,base+1.35),(1,0,0),(0,1,0),14,.14,2.7)
interior_b.box((-46,-16.8,base+1.35),(1,0,0),(0,1,0),14,.14,2.7)
interior_b.box((-53,-10,base+1.35),(0,1,0),(1,0,0),13.6,.14,2.7)
interior_b.box((-39,-10,base+1.35),(0,1,0),(1,0,0),13.6,.14,2.7)
# two detailed vertical NMR magnet assemblies with cryostat shell, neck, base and access panel
for x in (-30.0,-24.0):
    # Circular superconducting magnet cryostat, not a generic cabinet block.
    detail_b.box((x,8.5,base+.28),(1,0,0),(0,1,0),1.8,1.8,.45)
    # Front-facing service console, screen and distinct emergency stop.
    # Place the control panel tangentially beside the south-facing shell; a slight
    # separation avoids the prior diagonal z-fighting/intersection across the casing.
    panel_side=1 if x< -27 else -1
    detail_b.box((x+panel_side*.86,7.89,base+1.48),(1,0,0),(0,1,0),.42,.18,.62)
    display_b.box((x+panel_side*.86,7.785,base+1.57),(1,0,0),(0,1,0),.29,.035,.21)
    indicator_b.box((x+panel_side*.86,7.77,base+1.31),(1,0,0),(0,1,0),.075,.05,.075)
    # Yellow access boundary around each magnet stand.
    for dx,dy,wx,wy in [(0,-1.08,2.12,.055),(0,1.08,2.12,.055),(-1.08,0,.055,2.12),(1.08,0,.055,2.12)]:
        safety_b.box((x+dx,8.5+dy,base+.035),(1,0,0),(0,1,0),wx,wy,.035)
# sample preparation cabinets and safety station
case_b.box((-27.0,2.2,base+.47),(1,0,0),(0,1,0),9.0,.7,.72)
top_b.box((-27.0,2.2,base+.87),(1,0,0),(0,1,0),9.2,.78,.08)
# Drawer fronts, a small sink, faucet, balance and sample rack make the prep bench read as lab equipment.
for dx in (-2.8,-1.4,0,1.4,2.8):
    frame_b.box((-27.0+dx,1.835,base+.45),(1,0,0),(0,1,0),1.22,.025,.43)
    detail_b.box((-27.0+dx,1.80,base+.47),(1,0,0),(0,1,0),.18,.035,.035)
detail_b.box((-30.5,2.05,base+.93),(1,0,0),(0,1,0),.72,.34,.045)
steel_basin=Batch('NMR_Prep_Sink_and_Faucet',steel)
steel_basin.box((-30.5,2.0,base+1.08),(0,1,0),(1,0,0),.055,.44,.42)
steel_basin.box((-30.5,2.20,base+1.27),(1,0,0),(0,1,0),.05,.045,.38)
steel_basin.box((-30.5,2.0,base+1.45),(1,0,0),(0,1,0),.42,.045,.05)
steel_basin.finish()
detail_b.box((-23.0,2.0,base+1.12),(1,0,0),(0,1,0),.42,.38,.42)
display_b.box((-23.0,1.79,base+1.20),(1,0,0),(0,1,0),.30,.035,.19)
# Wall-mounted sample rack and small cabinet fronts above the bench.
white_b.box((-27.0,3.75,base+2.30),(1,0,0),(0,1,0),4.8,.28,.38)
frame_b.box((-27.0,3.59,base+2.30),(1,0,0),(0,1,0),4.6,.035,.035)
for j in range(7):
    detail_b.box((-29.1+j*.7,2.05,base+1.18),(1,0,0),(0,1,0),.035,.09,.20)
white_b.box((-51.8,-10,base+1.05),(1,0,0),(0,1,0),.9,.25,2.1)
# Representative NMR control workstation and service equipment. Exact models/locations are
# undocumented; these are clearly illustrative room details, not claims about the installed systems.
case_b.box((-27.0,5.0,base+.47),(1,0,0),(0,1,0),2.65,.82,.82)
top_b.box((-27.0,5.0,base+.91),(1,0,0),(0,1,0),2.78,.9,.08)
detail_b.box((-27.55,5.28,base+1.34),(1,0,0),(0,1,0),.82,.09,.62)
display_b.box((-27.55,5.225,base+1.36),(1,0,0),(0,1,0),.66,.035,.40)
detail_b.box((-26.85,4.67,base+.98),(1,0,0),(0,1,0),.72,.24,.045) # keyboard
case_b.box((-23.8,5.0,base+.44),(1,0,0),(0,1,0),.75,.72,.72) # console tower
detail_b.box((-23.8,4.62,base+.78),(1,0,0),(0,1,0),.46,.04,.30)
for xx in (-27.55,-26.85):
    case_b.box((xx,3.85,base+.48),(1,0,0),(0,1,0),.52,.50,.10) # chair seat
    case_b.box((xx,4.05,base+.78),(1,0,0),(0,1,0),.50,.09,.54) # chair back
    white_b.box((xx,3.85,base+.21),(1,0,0),(0,1,0),.08,.08,.48) # chair post
    for dx,dy in [(-.27,0),(.27,0),(0,-.24),(0,.24)]:
        white_b.box((xx+dx,3.85+dy,base+.035),(1,0,0),(0,1,0),.18,.05,.05)

# Ensure every vertex of every generated interior wall is within or on the actual imported source footprint.
outside_partition_vertices=[v for v in interior_b.verts if not point_on_footprint(v[0],v[1])]
if outside_partition_vertices:
    raise RuntimeError(f'{len(outside_partition_vertices)} interior wall vertices extend beyond source footprint; first={outside_partition_vertices[0]}')
# Create all geometry batches. Floors, doors, windows, labs remain organized by clear object names.
interior_wall_object=None; entry_stairs_object=None
for batch in [brick_bx,brick_by,conc_b,glass_b,frame_b,interior_b,case_b,top_b,hood_b,detail_b,white_b,wood_b,display_b,safety_b,indicator_b,entry_stairs]:
    result=batch.finish()
    if batch is interior_b: interior_wall_object=result
    if batch is entry_stairs: entry_stairs_object=result
if entry_stairs_object:
    entry_stairs_object['containment_exemption']='Exterior entrance stair treads; intentional approach outside the source wall footprint. Entry location is reference-supported; exact extension is inferred.'
wall_vertices=[v.co for v in interior_wall_object.data.vertices]
outside_final=[v for v in wall_vertices if not point_on_footprint(v.x,v.y)]
if outside_final: raise RuntimeError(f'Final interior wall mesh has {len(outside_final)} vertices beyond the footprint')
collection['source_footprint_local_xy_json']=json.dumps([(float(p.x),float(p.y)) for p in pts])
collection['interior_wall_vertex_count_checked']=len(wall_vertices)
collection['interior_wall_containment']='asserted inside/on the local source massing polygon, including wall thickness'
contained_batches=[brick_bx,brick_by,conc_b,glass_b,frame_b,interior_b,case_b,top_b,hood_b,detail_b,white_b,wood_b,display_b,safety_b,indicator_b]
contained_batch_vertices=[v for batch in contained_batches if batch.material in contained_materials for v in batch.verts]
outside_interior_vertices=[v for v in contained_batch_vertices if not point_on_footprint(v[0],v[1])]
if outside_interior_vertices:
    raise RuntimeError(f'{len(outside_interior_vertices)} interior vertices extend beyond source footprint; first={outside_interior_vertices[0]}')
collection['interior_geometry_vertex_count_checked']=len(contained_batch_vertices)
collection['interior_geometry_containment']='all non-exempt interior batches asserted inside/on the source footprint'

def add_nmr_cylinder(name,x,y,z,radius,depth,material):
    sides=48; verts=[]
    for zz in (z-depth/2,z+depth/2):
        for k in range(sides):
            ang=2*math.pi*k/sides
            verts.append((x+radius*math.cos(ang),y+radius*math.sin(ang),zz))
    faces=[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]
    faces.extend((k,(k+1)%sides,(k+1)%sides+sides,k+sides) for k in range(sides))
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    # Smooth cylindrical side quads; keep the end caps flat.
    for poly in me.polygons:
        poly.use_smooth=(len(poly.vertices)==4)
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free(); me.update()
    ob=bpy.data.objects.new(name,me); collection.objects.link(ob); ob.parent=root
    bevel=ob.modifiers.new('Soft instrument casing edges','BEVEL'); bevel.width=.035; bevel.segments=3
    return ob

for x in (-30.0,-24.0):
    add_nmr_cylinder('NMR_Cryostat_'+str(x).replace('-','m'),x,8.5,base+1.45,.63,1.82,hood)
    add_nmr_cylinder('NMR_Top_Cap_'+str(x).replace('-','m'),x,8.5,base+2.43,.39,.22,white)
    add_nmr_cylinder('NMR_Cryoline_Neck_'+str(x).replace('-','m'),x,8.5,base+2.69,.17,.34,steel)
    add_nmr_cylinder('NMR_Base_Ring_'+str(x).replace('-','m'),x,8.5,base+.51,.70,.12,steel)
    add_nmr_cylinder('NMR_Service_Collar_'+str(x).replace('-','m'),x,8.5,base+2.02,.65,.10,steel)

# Two small cryogen/utility dewars and control valves add a distinct secondary equipment group.
# Their presence, exact type and locations are illustrative because current equipment records were unavailable.
cryo_valves=Batch('NMR_Cryogen_Regulators',black)
for i,x in enumerate((-31.8,-22.2),1):
    add_nmr_cylinder(f'NMR_Cryogen_Dewar_{i}',x,13.8,base+.68,.25,1.25,white)
    add_nmr_cylinder(f'NMR_Cryogen_Dewar_Cap_{i}',x,13.8,base+1.36,.13,.12,steel)
    cryo_valves.box((x,13.48,base+1.20),(0,1,0),(1,0,0),.24,.05,.22)
    cryo_valves.box((x,13.445,base+1.20),(0,1,0),(1,0,0),.07,.025,.07)
cryo_valves.finish()

# Glass sample tubes and bottle necks sit on the back preparation counter.
for i in range(6):
    vx=-24.7+i*.38
    add_nmr_cylinder('Sample_Vial_'+str(i+1),vx,2.05,base+1.25,.065,.24,white)
    add_nmr_cylinder('Sample_Vial_Cap_'+str(i+1),vx,2.05,base+1.40,.072,.055,red if i==0 else steel)

# Explicit entrance sign; its lettering is modeled as geometry to avoid font dependencies.
def add_text(name,body,loc,size,mat,rot=(math.pi/2,0,0)):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.size=size; cu.extrude=.006; cu.align_x='CENTER'; cu.align_y='CENTER'
    ob=bpy.data.objects.new(name,cu); collection.objects.link(ob); ob.parent=root; ob.location=loc; ob.rotation_euler=rot; ob.data.materials.append(mat); return ob
# Door sign sits on the south face; directional type is small but legible in close render.
add_text('Entrance_Sign','HERBERT C. BROWN LABORATORY OF CHEMISTRY',(2.0,-17.48,3.62),.38,concrete,(math.pi/2,0,0))
add_text('NMR_Room_Identification','NMR FACILITY  /  L8124',(-27.0,15.83,base+2.12),.24,black,(math.pi/2,0,0))
add_text('NMR_Magnet_Safety','MAGNET SAFETY  -  KEEP METAL CLEAR',(-27.0,15.83,base+1.82),.105,red,(math.pi/2,0,0))
add_text('NMR_Instrument_Label_A','NMR A',(-29.66,7.50,base+1.72),.075,black,(math.pi/2,0,0))
add_text('NMR_Instrument_Label_B','NMR B',(-23.66,7.50,base+1.72),.075,black,(math.pi/2,0,0))

# Exterior site threshold: restrained concrete landing and planters, kept within this asset.
land=Batch('Entry_Landing',concrete)
land.box((2.0,-17.2,.06),(1,0,0),(0,1,0),6.0,2.0,.12); land.finish()
landing_object=next((o for o in collection.objects if o.name=='Entry_Landing'),None)
if landing_object:
    landing_object['containment_exemption']='Exterior entrance landing; intentional projection beyond the source wall footprint. Entrance presence is photo-supported; projection dimensions are inferred.'
# Roof and exterior component materials are procedural, so the library has no file dependencies.

# Render setup and included cameras/lights.
def look_at(ob,target): ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
def create_camera(name,loc,target,lens):
    data=bpy.data.cameras.new(name); data.lens=lens; data.sensor_width=36; ob=bpy.data.objects.new(name,data); collection.objects.link(ob); ob.parent=root; ob.location=loc; look_at(ob,target); return ob
cam_ext=create_camera('Camera_Brown_Exterior',(10,-160,58),(0,0,7.0),42)
cam_int=create_camera('Camera_Brown_Interior',(-27.0,2.4,-1.55),(-27.0,9.0,-1.85),24)
cam_cut=create_camera('Camera_Brown_Cutaway',(-65,-180,140),(0,0,15),50)
cam_cut.data.type='ORTHO'; cam_cut.data.ortho_scale=175
scene.camera=cam_ext
# Sun plus soft fill for readable brick texture; interior area lights are placed in major lab zones.
ld=bpy.data.lights.new('Sun_Brown_Daylight','SUN'); ld.energy=3.3; ld.angle=math.radians(18)
lo=bpy.data.objects.new('Sun_Brown_Daylight',ld); collection.objects.link(lo); lo.parent=root; lo.location=(-60,-80,90); lo.rotation_euler=(math.radians(25),0,math.radians(-25))
def area(name,loc,energy,color,size,target):
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color
    o=bpy.data.objects.new(name,d);collection.objects.link(o);o.parent=root;o.location=loc;look_at(o,target);return o
area('Exterior_Soft_Fill',(35,-62,52),5200,(1.0,.88,.76),32,(0,0,8))
area('Interior_Lab_Key',(-2.0,8.0,2.72),1150,(.82,.9,1.0),5,(0,8,1.5))
area('Interior_Lab_Fill',(1.5,9.4,2.55),650,(1.0,.85,.68),4,(0,8,1.4))
area('Basement_NMR_Key',(-27.0,-6.0,-.35),2600,(.86,.92,1.0),10,(-27.0,8.0,-1.7))
area('Basement_NMR_Fill',(-35.0,-1.0,-.15),1200,(1.0,.91,.80),8,(-27.0,8.0,-1.7))
# Soft white world; exterior background remains neutral, with world illumination for interior.
world=bpy.data.worlds.new('Brown Laboratory neutral world'); world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.16,.19,.23,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.58;scene.world=world
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=48
scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=.35
scene.render.filepath=str(AUDIT/'brown_exterior.png')
# Metadata documents the frame and evidence limitations.
scene['building_id']=ASSET_ID;scene['placement_origin_xy_m']=[origin_x,origin_y];scene['placement_origin_z_m']=0.0
scene['source_footprint_feature_id']=247;scene['source_footprint_status']='official Purdue GIS footprint; horizontal polygon retained from source massing, exact geometry identity as represented by source'
scene['height_status']='estimated from source massing 16.0 m, consistent with five occupied levels but not a measured survey height'
scene['architectural_detail_status']='photo-supported red brick, pale projecting concrete piers, repeated vertical glazing; rooftop equipment, interior furniture and NMR support equipment are illustrative inferences, not verified installed systems'

# Ensure every object belongs to the exported asset collection and is rooted at local zero.
for ob in list(collection.objects):
    if ob is root: continue
    if ob.parent is None: ob.parent=root
    ob['asset_id']=ASSET_ID
# Apply no scale to root or child objects; all design dimensions are metric.
root.location=(0,0,0);root.scale=(1,1,1)
# Final pre-save containment audit for every interior mesh, including newly added standalone NMR
# equipment. Only explicit exterior-envelope meshes and tagged entry projections are exempt.
exterior_mesh_names={'Exterior_Brickwork_EW','Exterior_Brickwork_NS','Exterior_Concrete_Piers_and_Coping','Exterior_Glazing','Exterior_Window_Frames'}
pre_save_interior=[]; pre_save_outside={}
for ob in collection.objects:
    if ob.type!='MESH' or ob.name in exterior_mesh_names or ob.get('containment_exemption'): continue
    pre_save_interior.append(ob)
    bad=[]
    for v in ob.data.vertices:
        p=ob.matrix_world @ v.co
        if not point_on_footprint(p.x,p.y): bad.append(v.co)
    if bad: pre_save_outside[ob.name]=len(bad)
if pre_save_outside: raise RuntimeError(f'Pre-save interior containment failure: {pre_save_outside}')
collection['interior_mesh_count_checked_before_save']=len(pre_save_interior)
collection['interior_mesh_vertex_count_checked_before_save']=sum(len(o.data.vertices) for o in pre_save_interior)
# Save standalone asset, then render exterior and a real in-building lab view.
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
scene.camera=cam_ext;scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.filepath=str(AUDIT/'brown_exterior.png');bpy.ops.render.render(write_still=True)
scene.camera=cam_int;scene.render.resolution_x=1350;scene.render.resolution_y=900;scene.render.filepath=str(AUDIT/'brown_interior_lab.png')
# Render only basement-height faces for a clean interior preview: upper floors and the first-floor
# slab cannot intrude into this camera, while the saved full asset remains untouched.
interior_visibility={o.name:o.hide_render for o in collection.objects}; basement_preview=[]
for ob in collection.objects:
    if ob.type=='LIGHT': ob.hide_render=False
    elif ob.type=='CAMERA': ob.hide_render=(ob is not cam_int)
    else: ob.hide_render=True
root.hide_render=False
for source in list(collection.objects):
    if source.type!='MESH': continue
    data=source.data.copy(); bm=bmesh.new(); bm.from_mesh(data)
    remove=[face for face in bm.faces if face.calc_center_median().z < -3.40 or face.calc_center_median().z > -.20]
    if remove: bmesh.ops.delete(bm,geom=remove,context='FACES')
    loose=[v for v in bm.verts if not v.link_faces]
    if loose: bmesh.ops.delete(bm,geom=loose,context='VERTS')
    if not bm.faces:
        bm.free(); bpy.data.meshes.remove(data); continue
    bm.to_mesh(data); bm.free(); data.update()
    copy=source.copy(); copy.data=data; copy.name='BasementPreview_'+source.name
    collection.objects.link(copy); copy.parent=root; copy.hide_render=False
    basement_preview.append(copy)
bpy.ops.render.render(write_still=True)
for copy in basement_preview:
    data=copy.data; bpy.data.objects.remove(copy,do_unlink=True)
    if data.users==0: bpy.data.meshes.remove(data)
for ob in collection.objects:
    if ob.name in interior_visibility: ob.hide_render=interior_visibility[ob.name]
# Render-only exploded floor cutaway. Split each interior batch by story height, then separate
# stories vertically by an 8 m pitch. A three-quarter elevated camera exposes the room plan,
# door openings and cores from both sides while preserving the north-up model orientation.
levels=[('basement',-3.2,-8.0),('01',0.0,0.0),('02',3.2,8.0),('03',6.4,16.0),('04',9.6,24.0),('05',12.8,32.0)]
original_visibility={o.name:o.hide_render for o in collection.objects}
for ob in collection.objects:
    if ob.type=='LIGHT': ob.hide_render=False
    elif ob.type=='CAMERA': ob.hide_render=True
    else: ob.hide_render=True
root.hide_render=False
temp_objects=[]; level_objects={}
cut_floor_material=mat_principled('Temporary cutaway | contrasting floor datum',(.19,.24,.27),.92)
level_floor_colors={'basement':(.20,.27,.32),'01':(.34,.31,.25),'02':(.23,.31,.27),'03':(.24,.29,.34),'04':(.35,.28,.21),'05':(.29,.25,.34)}
level_floor_materials={name:mat_principled('Temporary cutaway | '+name+' floor',color,.92) for name,color in level_floor_colors.items()}
skip_names={'Exterior_Brickwork_EW','Exterior_Brickwork_NS','Exterior_Concrete_Piers_and_Coping','Exterior_Glazing','Exterior_Window_Frames','Entry_Landing'}
source_meshes=[o for o in list(collection.objects) if o.type=='MESH' and o.name not in skip_names and not o.name.startswith('Floor_plate_')]
for level_name,zbase,outbase in levels:
    group=[]
    for source in source_meshes:
        data=source.data.copy(); bm=bmesh.new(); bm.from_mesh(data)
        remove=[]
        for face in bm.faces:
            zc=face.calc_center_median().z
            if zc < zbase-.025 or zc > zbase+story+.025: remove.append(face)
        if remove: bmesh.ops.delete(bm,geom=remove,context='FACES')
        loose=[v for v in bm.verts if not v.link_faces]
        if loose: bmesh.ops.delete(bm,geom=loose,context='VERTS')
        if not bm.faces:
            bm.free(); bpy.data.meshes.remove(data); continue
        for vert in bm.verts: vert.co.z += outbase-zbase
        bm.to_mesh(data); bm.free(); data.update()
        ob=source.copy(); ob.data=data; ob.name=f'Cutaway_{level_name}_{source.name}'
        collection.objects.link(ob); ob.hide_render=False
        ob.parent=root; group.append(ob); temp_objects.append(ob)
    # Matching plan-based slab provides a clear floor datum under each exploded level.
    plate=next((o for o in collection.objects if o.name==f'Floor_plate_{str(zbase).replace(".","_")}m'),None)
    if plate:
        pdata=plate.data.copy()
        pdata.materials.clear(); pdata.materials.append(level_floor_materials[level_name])
        for vert in pdata.vertices: vert.co.z += outbase-zbase
        pobj=plate.copy(); pobj.data=pdata; pobj.name=f'Cutaway_{level_name}_floor_plate'
        collection.objects.link(pobj); pobj.parent=root; pobj.hide_render=False
        group.append(pobj); temp_objects.append(pobj)
    level_objects[level_name]=group
scene.camera=cam_cut; scene.render.resolution_x=2000; scene.render.resolution_y=1300
# Render-only level tags make the deliberately exploded story spacing unambiguous.
cutaway_labels=[]
for label,zout in [('BASEMENT',-8.0),('LEVEL 01',0.0),('LEVEL 02',8.0),('LEVEL 03',16.0),('LEVEL 04',24.0),('LEVEL 05',32.0)]:
    cu=bpy.data.curves.new('TempCutawayLabel_'+label,'FONT'); cu.body=label; cu.size=1.7; cu.extrude=.012
    cu.materials.append(white)
    ob=bpy.data.objects.new('TempCutawayLabel_'+label,cu); collection.objects.link(ob); ob.parent=root
    ob.location=(-62,-17,zout+1.3); ob.rotation_euler=cam_cut.rotation_euler; ob.hide_render=False
    cutaway_labels.append(ob)
scene.render.filepath=str(AUDIT/'brown_cutaway.png'); bpy.ops.render.render(write_still=True)
for ob in cutaway_labels: ob.hide_render=True
# Each source plan gets its own orthographic top view so room partitions and entries can be read.
plan_cam=create_camera('Camera_Brown_PlanCutaway_Temp',(0,0,35),(0,0,0),50)
plan_cam.data.type='ORTHO'; plan_cam.data.ortho_scale=116
scene.camera=plan_cam; scene.render.resolution_x=1800; scene.render.resolution_y=800
for level_name,zbase,outbase in levels:
    for other,group in level_objects.items():
        for ob in group: ob.hide_render=(other!=level_name)
    plan_cam.location=(0,0,outbase+38); look_at(plan_cam,(0,0,outbase))
    filename='brown_basement_cutaway.png' if level_name=='basement' else f'brown_floor_{level_name}_cutaway.png'
    scene.render.filepath=str(AUDIT/filename); bpy.ops.render.render(write_still=True)
for ob in temp_objects:
    data=ob.data; bpy.data.objects.remove(ob,do_unlink=True)
    if data.users==0: bpy.data.meshes.remove(data)
for mat in [cut_floor_material,*level_floor_materials.values()]:
    if mat.users==0: bpy.data.materials.remove(mat)
for ob in cutaway_labels:
    data=ob.data; bpy.data.objects.remove(ob,do_unlink=True)
    if data.users==0: bpy.data.curves.remove(data)
bpy.data.objects.remove(plan_cam,do_unlink=True)
for ob in collection.objects:
    if ob.name in original_visibility: ob.hide_render=original_visibility[ob.name]
scene.render.resolution_x=1500;scene.render.resolution_y=1000
scene.camera=cam_ext;scene.render.filepath='//'
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
print(json.dumps({'status':'BUILT','asset':str(OUTPUT),'origin_xy_m':[origin_x,origin_y],'height_source_m':height,'perimeter_simplified_vertices':len(pts),'top_triangles':len(top_faces),'object_count':len(collection.objects),'mesh_objects':sum(o.type=='MESH' for o in collection.objects),'materials':len([m for m in bpy.data.materials if m.users>0]),'render_exterior':str(AUDIT/'brown_exterior.png'),'render_interior':str(AUDIT/'brown_interior_lab.png')},indent=2))

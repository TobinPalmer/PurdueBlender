"""Create Haas facade meshes from GIS and explicit photo-derived schedules.

Run with repository Python (Shapely 2.2), then run build_felix_haas_hall.py in
Blender. No geometry is sampled from the previous Blender model.
"""
from pathlib import Path
import json,math
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
from shapely.geometry.polygon import orient

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'modular/manifest.json').exists())
REVISION='detail_color_r04'
OUT=ROOT/'audit/felix_haas_hall/second_pass'/REVISION;OUT.mkdir(parents=True,exist_ok=True)
source=json.loads((OUT.parent/'sources/haas_official_footprint_fid233.json').read_text())
origin=(-214.84998321533203,-64.0199966430664)
ring=[(x-origin[0],y-origin[1]) for x,y in source['building']['rings_xy_m'][0][:-1]]
parts=[];windows=[];facades=[]
def polygons(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return [g]
    return [p for q in getattr(g,'geoms',[]) for p in polygons(q)]
def make_part(name,poly,material,basis,front=0,back=-.26):
    """Watertight extrusion of a constrained triangulation, including hole reveals."""
    poly=poly.buffer(0).simplify(.00001,preserve_topology=True)
    for number,p in enumerate(polygons(poly)):
        if p.area<1e-5 or p.minimum_clearance<.00001:continue
        p=orient(p,sign=1);vertices=[];faces=[];lookup={}
        def index(u,z,d):
            xyz=(basis['a'][0]+basis['t'][0]*u+basis['n'][0]*d,basis['a'][1]+basis['t'][1]*u+basis['n'][1]*d,z)
            key=tuple(round(c,7) for c in xyz)
            if key not in lookup:lookup[key]=len(vertices);vertices.append(key)
            return lookup[key]
        for tri in constrained_delaunay_triangles(p).geoms:
            pts=list(orient(tri,sign=1).exterior.coords)[:-1]
            faces.append([index(u,z,front) for u,z in reversed(pts)])
            faces.append([index(u,z,back) for u,z in pts])
        for loop in [p.exterior,*p.interiors]:
            pts=list(loop.coords)
            for (u,z),(v,w) in zip(pts,pts[1:]):faces.append([index(u,z,front),index(v,w,front),index(v,w,back),index(u,z,back)])
        parts.append({'name':name+(f'_{number}' if number else ''),'material':material,'vertices':vertices,'faces':faces})
def arch(u,bottom,w,top,rise=0):
    if rise<=0:return box(u-w/2,bottom,u+w/2,top)
    a=w/2;r=(a*a+rise*rise)/(2*rise);cz=top-r
    crown=[(u-a+2*a*i/24,cz+math.sqrt(max(0,r*r-(-a+2*a*i/24)**2))) for i in range(25)]
    return Polygon([(u-a,bottom),(u+a,bottom),*reversed(crown)])
def window(face,label,u,z,w,h,cols=2,rows=2,rise=0,style='plain',door=False):
    hole=arch(u,z,w,z+h,rise)
    item={'face':face,'label':label,'u':u,'bottom':z,'width':w,'height':h,'columns':cols,'rows':rows,'rise':rise,'style':style,'door':door,'hole':hole}
    windows.append(item);return item

for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
    L=math.dist(a,b);t=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(-t[1],t[0])
    # The source ring is clockwise: outward is to the left of each edge.
    face={'id':i,'a':a,'b':b,'t':t,'n':n,'length':L,'height':11.55};facades.append(face)
    if i==4: # Main east pavilion front; photographs establish three bays.
        for j,u in enumerate([L*.18,L*.50,L*.82]):
            window(i,f'FrontUpper{j}',u,8.55,3.55,1.85,3,2,style='stepped')
            if j!=1:window(i,f'FrontSegmental{j}',u,3.10,3.55,3.45,2,3,.52,style='segmental')
            else:window(i,'MainEntrance',u,2.38,2.95,4.15,2,2,.42,style='portal',door=True)
        # Small basement openings flanking the stair, visible in official photo.
        for j,u in enumerate([L*.18,L*.82]):window(i,f'FrontBasement{j}',u,.82,2.5,1.05,2,1)
    elif i==10: # Long west / University Street elevation.
        for j in range(9):
            u=L*(j+.5)/9
            window(i,f'WestUpper{j}',u,9.15,3.45 if j>=6 else 2.95,1.82,3 if j>=6 else 2,2,style='stepped')
            window(i,f'WestMiddle{j}',u,5.20,.76,2.15,1,2,style='narrow')
            window(i,f'WestBase{j}',u,.82,2.72,1.40,2,2)
        # Door seen in two independent views, third bay from north.
        w=next(w for w in windows if w['label']=='WestBase6')
        w.update(label='WestDoor',bottom=.10,width=2.7,height=2.95,rows=2,door=True)
        w['hole']=arch(w['u'],.10,2.7,3.05)
    elif i in (9,11): # Main north/south end walls; photo coverage differs by side.
        for j in range(5):
            u=L*(j+.5)/5
            window(i,f'{"South" if i==9 else "North"}Upper{j}',u,9.15,3.15,1.82,2,2,style='stepped')
            window(i,f'{"South" if i==9 else "North"}Middle{j}',u,5.20,.76,2.15,1,2,style='narrow')
            window(i,f'{"South" if i==9 else "North"}Base{j}',u,.82,2.60,1.40,2,2)
        if i==11:
            w=next(w for w in windows if w['label']=='NorthBase0')
            w.update(label='NorthServiceDoor',bottom=.08,width=2.60,height=2.25,rows=1,door=True)
            w['hole']=box(w['u']-1.30,.08,w['u']+1.30,2.33)
    elif i in (0,8): # Front returns of the main hall; not identical to the entry front.
        for j in range(3):
            u=L*(j+.5)/3
            window(i,f'EastWing{i}Upper{j}',u,9.15,2.95,1.82,2,2,style='stepped')
            window(i,f'EastWing{i}Middle{j}',u,5.2,.76,2.15,1,2,style='narrow')
            window(i,f'EastWing{i}Base{j}',u,.82,2.40,1.4,2,2)
    elif i in (3,5) and L>7: # Side walls of the projecting entry pavilion.
        for j in range(2):
            u=L*(j+.5)/2
            window(i,f'PavilionReturn{i}Upper{j}',u,8.55,2.45,1.85,2,2,style='stepped')
            window(i,f'PavilionReturn{i}Lower{j}',u,3.1,2.25,3.45,2,3,.4,style='segmental')

for face in facades:
    i=face['id'];L=face['length'];W=[w for w in windows if w['face']==i]
    holes=unary_union([w['hole'] for w in W]) if W else Polygon()
    surface=box(0,0,L,11.55).difference(holes)
    # One structural wall with actual apertures, rather than accumulated patches.
    make_part(f'HAAS_Rebuild_Wall_{i}',surface,'brick',face)
    stone_regions=[box(0,0,L,3.24),box(0,11.04,L,11.23),box(0,11.40,L,11.55)]
    if i==4:
        # The real entrance is a predominantly pale stone composition with
        # inset pressed-brick panels and stepped stone/brick boundaries.
        # Build that composition as one carved cladding mesh, not floating bars.
        brick_panels=[]
        for u in [L*.18,L*.5,L*.82]:
            for z0,z1 in [(3.24,6.82),(7.18,10.75)]:
                bands=8;left=[];right=[]
                for k in range(bands):
                    zz=z0+(z1-z0)*k/bands;zn=z0+(z1-z0)*(k+1)/bands
                    half=2.65-(.14 if k%2==0 else 0)
                    left.extend([(u-half,zz),(u-half,zn)])
                    right.extend([(u+half,zz),(u+half,zn)])
                brick_panels.append(Polygon(left+list(reversed(right))))
        stone_regions=[box(0,0,L,11.55).difference(unary_union(brick_panels))]
    else:
        count=9 if i==10 else 5 if i in (9,11) else 3 if i in (0,8) else 2
        if L>7:
            for j in range(count+1):
                u=L*j/count
                # Brick projecting piers, not tall white columns.
                make_part(f'HAAS_Rebuild_BrickPier_{i}_{j}',box(max(0,u-.22),3.24,min(L,u+.22),11.04),'brick',face,.16,.005)
    # Brick inset panels in the broad pale basement register.
    if i!=4 and L>7:
        centers=sorted(w['u'] for w in W if 'Base' in w['label'] or w['label']=='WestDoor')
        for u,v in zip(centers,centers[1:]):stone_regions.append(box((u+v)/2-.8,1.10,(u+v)/2+.8,2.45).buffer(0))
        insets=unary_union([box((u+v)/2-.8,1.10,(u+v)/2+.8,2.45) for u,v in zip(centers,centers[1:])])
    else:insets=Polygon()
    stone_zone=unary_union(stone_regions).difference(holes).difference(insets)
    make_part(f'HAAS_Rebuild_StoneRegister_{i}',stone_zone,'stone',face,.10,-.01)
    for k,(zz,hh,depth) in enumerate([(3.20,.13,.23),(3.02,.055,.19)]):
        make_part(f'HAAS_Detail_BasementMolding_{i}_{k}',box(0,zz,L,zz+hh).difference(holes),'stone',face,depth,.09)
    for w in W:
        label='HAAS_Rebuild_'+w['label'];h=w['hole'];u=w['u'];z=w['bottom'];width=w['width'];height=w['height']
        outer=h.buffer(.20,join_style='mitre');inner=h.buffer(-.075,join_style='mitre');pane=h.buffer(-.16,join_style='mitre')
        if w['style']=='narrow':
            # Minimal pale sill and tapered key rather than an oversized full surround.
            make_part(label+'_Sill',box(u-width/2-.13,z-.15,u+width/2+.13,z+.015),'stone',face,.23,-.03)
            key=Polygon([(u-.20,z+height+.50),(u+.20,z+height+.50),(u+.085,z+height+.04),(u-.085,z+height+.04)])
            make_part(label+'_Key',key,'stone',face,.15,-.01)
        else:
            make_part(label+'_StoneSurround',outer.difference(h),'stone',face,.22,-.01)
            make_part(label+'_ProjectingSill',box(u-width/2-.25,z-.19,u+width/2+.25,z-.015),'stone',face,.35,-.02)
            if w['style']=='stepped':
                for sign in (-1,1):
                    for zz in (z+.18,z+height-.18):
                        make_part(label+f'_Quoin_{sign}_{zz:.2f}',box(u+sign*(width/2+.19)-.18,zz-.15,u+sign*(width/2+.19)+.18,zz+.15).difference(h),'stone',face,.255,-.01)
                make_part(label+'_Key',box(u-.14,z+height-.02,u+.14,z+height+.40).difference(h),'stone',face,.26,-.01)
        make_part(label+'_Frame',h.buffer(-.035).difference(pane),'bronze',face,.025,-.22)
        if w['door'] and w['label']=='MainEntrance':
            # Narrow oak door deep inside the broad stone portal.
            leaf_top=z+2.85
            door_poly=box(u-.70,z+.02,u+.70,leaf_top)
            make_part(label+'_DeepReveal',h.difference(h.buffer(-.10)),'stone',face,-.015,-.82)
            make_part(label+'_PortalBack',pane.difference(door_poly),'stone',face,-.72,-.83)
            make_part(label+'_DoorFrame',door_poly.buffer(.08).difference(door_poly),'bronze',face,-.61,-.75)
            make_part(label+'_Timber',door_poly,'wood',face,-.64,-.75)
            for sign in (-1,1):
                yy=u+sign*.28
                make_part(label+f'_UpperDoorGlass_{sign}',box(yy-.17,z+1.90,yy+.17,leaf_top-.24),'glass',face,-.60,-.625)
                make_part(label+f'_LowerDoorPanel_{sign}',box(yy-.19,z+.30,yy+.19,z+1.55),'wood_dark',face,-.60,-.625)
            make_part(label+'_DoorHandle',box(u+.48,z+1.08,u+.51,z+1.40),'bronze',face,-.54,-.61)
        elif w['label']=='NorthServiceDoor':
            make_part(label+'_ServiceLeaves',pane,'service_metal',face,-.14,-.22)
        else:make_part(label+'_Glass',pane,'glass',face,-.18,-.21)
        bars=[]
        for k in range(1,w['columns']):
            xx=u-width/2+width*k/w['columns'];bars.append(box(xx-.037,z,xx+.037,z+height))
        if w['style']=='stepped':levels=[z+height*(.50 if i==4 else .72)]
        else:levels=[z+height*k/w['rows'] for k in range(1,w['rows'])]
        if w['door']:levels=[z+height*.75]
        if w['label']=='WestDoor':levels=[z+height*.52,z+height*.82]
        if w['label']=='NorthServiceDoor':levels=[]
        for zz in levels:bars.append(box(u-width,zz-.032,u+width,zz+.032))
        if bars and w['label']!='MainEntrance':make_part(label+'_Mullions',unary_union(bars).intersection(pane),'bronze',face,-.10,-.19)
        # Segmental arch joints are real separations in raised stone blocks.
        if w['rise']>0:
            a=width/2;r=(a*a+w['rise']**2)/(2*w['rise']);cz=z+height-r
            for k in range(1,9):
                xx=u-a+width*k/9
                zz=cz+math.sqrt(max(0,r*r-(xx-u)**2))
                make_part(label+f'_ArchJoint{k}',box(xx-.007,zz,xx+.007,zz+.22).intersection(outer.difference(h)),'joint',face,.226,.222)
        w['source_status']='photograph-supported character; dimensions estimated'
        if i in (3,5,8,9):w['source_status']='partially observed; schedule and dimensions remain estimates pending closer view'

    if i==4:
        u=L/2
        portal=next(w['hole'] for w in W if w['label']=='MainEntrance')
        for k,(offset,depth) in enumerate([(.28,.29),(.38,.23),(.46,.18)]):
            make_part(f'HAAS_Detail_Portal_Profile{k}',portal.buffer(offset,join_style='mitre').difference(portal.buffer(offset-.055,join_style='mitre')),'stone',face,depth,.11)
        # Shallow plaque border only: lettering/figurative relief is unresolved.
        plaque=box(u-1.95,6.96,u+1.95,7.88)
        make_part('HAAS_Detail_Entry_PlaqueBorder',plaque.difference(plaque.buffer(-.10)),'stone',face,.205,.11)
        make_part('HAAS_Detail_Entry_PlaqueInset',plaque.buffer(-.16),'stone',face,.115,.10)
        for k,zz in enumerate((10.88,11.00)):
            make_part(f'HAAS_Detail_FrontFriezeMolding_{k}',box(0,zz,L,zz+.045),'stone',face,.18,.105)
        for sign in (-1,1):
            x=u+sign*L*.16
            relief=box(x-.29,9.42,x+.29,10.58)
            make_part(f'HAAS_Detail_UpperPierReliefBorder_{sign}',relief.difference(relief.buffer(-.06)),'stone',face,.15,.105)
            for dx in (-.13,.13):
                make_part(f'HAAS_Detail_UpperPierReliefLine_{sign}_{dx}',box(x+dx-.012,9.65,x+dx+.012,10.38),'stone_shade',face,.115,.108)
        for sign in (-1,1):
            x=u+sign*1.83
            make_part(f'HAAS_Detail_PortalPilaster_{sign}',box(x-.14,2.48,x+.14,6.14),'stone',face,.28,.12)
            make_part(f'HAAS_Detail_PortalCapital_{sign}',box(x-.24,6.06,x+.24,6.35),'stone',face,.35,.12)
            for k in (-1,0,1):
                make_part(f'HAAS_Detail_JambFlute_{sign}_{k}',box(x+k*.07-.011,2.70,x+k*.07+.011,5.96),'stone_shade',face,.283,.280)
        for w in W:
            if w['style']=='segmental':
                x=w['u'];top=w['bottom']+w['height']
                key=Polygon([(x-.16,top-.10),(x+.16,top-.10),(x+.22,top+.38),(x-.22,top+.38)])
                make_part('HAAS_Detail_'+w['label']+'_CrownKey',key,'stone',face,.34,.20)

# Two newly constructed closed hipped volumes. The Blender builder unites them
# once, eliminating the intersecting roof surfaces rather than stacking meshes.
def hip_solid(name,x0,y0,x1,y1,eave,rise):
    cx=(x0+x1)/2;half=(x1-x0)/2
    v=[(x0,y0,eave),(x1,y0,eave),(x1,y1,eave),(x0,y1,eave),
       (cx,y0+half,eave+rise),(cx,y1-half,eave+rise),
       (x0,y0,eave-.25),(x1,y0,eave-.25),(x1,y1,eave-.25),(x0,y1,eave-.25)]
    f=[(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5),(0,6,7,1),
       (1,7,8,2),(2,8,9,3),(3,9,6,0),(6,9,8,7)]
    parts.append({'name':name,'material':'roof','vertices':v,'faces':f})
hip_solid('HAAS_Rebuild_Main_RoofSolid',-26.83,-26.58,2.85,27.36,11.75,2.55)
hip_solid('HAAS_Rebuild_Entry_RoofSolid',-.40,-12.18,13.59,13.24,11.75,1.65)
record={'revision':REVISION,'method':'New constrained polygon meshes from official footprint and documented photo-derived opening schedule; no source blend geometry sampled','origin_xy_m':origin,'footprint_source':source,'local_footprint':ring,'facades':facades,'openings':[{k:v for k,v in w.items() if k!='hole'} for w in windows],'parts':parts,'limitations':['Opening dimensions and elevations are photographic estimates, not measured elevations.','South, pavilion returns and portions of east wings have incomplete photographic coverage; no claim of 9.9 or exact reconstruction.','The prior schematic interior is kept in a separate hidden archive, not used as an exterior reference.']}
(OUT/'geometry_input.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'parts':len(parts),'openings':len(windows),'vertices':sum(len(p['vertices']) for p in parts),'roof_solids':2}))

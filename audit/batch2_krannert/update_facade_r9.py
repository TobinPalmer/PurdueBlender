import bpy, bmesh, math, json, hashlib, os
from pathlib import Path
ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
ASSET=ROOT/'modular/buildings/krannert_building.blend'
OUT=ROOT/'audit/batch2_krannert/facade_round9_update.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections['Asset_krannert_building']
KRAN_PTS=[(196.535,-421.196),(207.995,-421.115),(207.769,-395.855),(234.402,-395.602),(234.383,-394.273),(228.530,-393.438),(228.553,-389.212),(237.336,-387.954),(237.422,-387.954),(246.152,-389.095),(246.419,-393.254),(246.212,-393.272),(240.380,-394.169),(240.357,-395.544),(267.040,-395.291),(267.061,-397.474),(270.872,-397.441),(270.921,-403.263),(272.490,-403.251),(272.534,-408.759),(270.965,-408.771),(271.015,-414.575),(267.181,-414.603),(267.193,-416.820),(238.060,-417.003),(238.187,-434.122),(233.743,-434.152),(233.665,-422.829),(230.689,-422.847),(230.764,-435.202),(222.543,-435.252),(222.543,-435.441),(222.238,-435.440),(222.239,-435.255),(214.998,-435.298),(214.997,-435.484),(214.763,-435.484),(214.763,-435.300),(208.122,-435.342),(208.079,-432.871),(196.753,-432.950)]
Z_GROUND=0.0; Z_L1=3.871;Z_L2=8.534;Z_L3=12.405;Z_L4=16.307;Z_L5=20.178;Z_L6=24.049;Z_L7=27.920;Z_ROOF=31.791
names=['KRAN_Vertical_Limestone_Piers','KRAN_Window_Ribbon_Glazing','KRAN_Horizontal_Spandrel_Panels','KRAN_Anodized_Bronze_Mullions']
objects={n:bpy.data.objects[n] for n in names}
meshes={};bms={}
for n,o in objects.items():
    m=bpy.data.meshes.new(n+'_R9')
    if o.data.materials: m.materials.append(o.data.materials[0])
    meshes[n]=m;bms[n]=bmesh.new()
bp=bms[names[0]];bg=bms[names[1]];bs=bms[names[2]];bm=bms[names[3]]

def facade(pA,pB,num_bays,has_ground_windows=True,skip_skyport=False):
    xA,yA=pA;xB,yB=pB;dx=xB-xA;dy=yB-yA;length=math.hypot(dx,dy)
    ux=dx/length;uy=dy/length;nx=-uy;ny=ux;bay=length/num_bays;pier_width=.72;pier_depth=.25
    floors=[(Z_L1,Z_L2),(Z_L2,Z_L3),(Z_L3,Z_L4),(Z_L4,Z_L5),(Z_L5,Z_L6),(Z_L6,Z_L7),(Z_L7,Z_ROOF)]
    for i in range(num_bays):
        s0=i*bay;s1=(i+1)*bay
        # Source-supported pale piers between the vertical glazing slots.
        if i>0:
            a=s0-pier_width/2;b=s0+pier_width/2
            x0=xA+a*ux;y0=yA+a*uy;x1=xA+b*ux;y1=yA+b*uy
            v0=bp.verts.new((x0,y0,Z_L1));v1=bp.verts.new((x1,y1,Z_L1));v2=bp.verts.new((x1+nx*pier_depth,y1+ny*pier_depth,Z_L1));v3=bp.verts.new((x0+nx*pier_depth,y0+ny*pier_depth,Z_L1))
            v4=bp.verts.new((x0,y0,Z_ROOF));v5=bp.verts.new((x1,y1,Z_ROOF));v6=bp.verts.new((x1+nx*pier_depth,y1+ny*pier_depth,Z_ROOF));v7=bp.verts.new((x0+nx*pier_depth,y0+ny*pier_depth,Z_ROOF))
            bp.faces.new((v3,v2,v6,v7));bp.faces.new((v0,v3,v7,v4));bp.faces.new((v2,v1,v5,v6))
        if has_ground_windows:
            gx0=xA+(s0+.20)*ux+nx*.04;gy0=yA+(s0+.20)*uy+ny*.04;gx1=xA+(s1-.20)*ux+nx*.04;gy1=yA+(s1-.20)*uy+ny*.04
            gb=Z_GROUND+.85;gt=Z_L1-.35
            g0=bg.verts.new((gx0,gy0,gb));g1=bg.verts.new((gx1,gy1,gb));g2=bg.verts.new((gx1,gy1,gt));g3=bg.verts.new((gx0,gy0,gt));bg.faces.new((g0,g1,g2,g3))
            m0=bm.verts.new((gx0,gy0,gb-.04));m1=bm.verts.new((gx1,gy1,gb-.04));m2=bm.verts.new((gx1+nx*.03,gy1+ny*.03,gb+.04));m3=bm.verts.new((gx0+nx*.03,gy0+ny*.03,gb+.04));bm.faces.new((m0,m1,m2,m3))
        slot=min(1.25,bay*.46);w0=(s0+s1-slot)/2;w1=w0+slot
        x0=xA+w0*ux+nx*.05;y0=yA+w0*uy+ny*.05;x1=xA+w1*ux+nx*.05;y1=yA+w1*uy+ny*.05
        for flo,fhi in floors:
            if skip_skyport and abs(flo-Z_L4)<1e-6:continue
            sill=.28;wb=flo+sill;wt=fhi-.18
            q0=bs.verts.new((x0,y0,flo));q1=bs.verts.new((x1,y1,flo));q2=bs.verts.new((x1,y1,wb));q3=bs.verts.new((x0,y0,wb));bs.faces.new((q0,q1,q2,q3))
            a=bg.verts.new((x0,y0,wb));b=bg.verts.new((x1,y1,wb));c=bg.verts.new((x1,y1,wt));d=bg.verts.new((x0,y0,wt));bg.faces.new((a,b,c,d))
            t=.045
            for z in (wb,wt,wb+(wt-wb)*.52):
                vv=[bm.verts.new((x0,y0,z-t/2)),bm.verts.new((x1,y1,z-t/2)),bm.verts.new((x1+nx*.04,y1+ny*.04,z+t/2)),bm.verts.new((x0+nx*.04,y0+ny*.04,z+t/2))]
                bm.faces.new(vv)

# Reproduce every existing facade segment. The source-supported vertical-slot treatment is applied consistently to windowed facades.
for a,b,n,kw in [(29,38,8,{'has_ground_windows':False}),(25,26,2,{}),(23,24,10,{}),(24,25,6,{}),(26,27,4,{}),(28,29,4,{}),(39,40,4,{}),(0,1,4,{}),(1,2,8,{}),(2,3,9,{}),(13,14,9,{}),(5,6,2,{}),(6,7,3,{}),(8,9,3,{}),(9,10,2,{}),(16,17,2,{}),(18,19,2,{'skip_skyport':True}),(20,21,2,{})]:
    facade(KRAN_PTS[a],KRAN_PTS[b],n,**kw)

before={n:{'vertices':len(o.data.vertices),'faces':len(o.data.polygons)} for n,o in objects.items()}
for n in names:
    bms[n].to_mesh(meshes[n]);bms[n].free()
    old=objects[n].data;objects[n].data=meshes[n]
    if old.users==0:bpy.data.meshes.remove(old)
# Keep the source asset's existing transforms, parents, material identities, collections, and all non-facade geometry intact.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
# Reopen exactly what was saved and record resulting mesh/collection integrity.
bpy.ops.wm.open_mainfile(filepath=str(ASSET));col=bpy.data.collections['Asset_krannert_building']
after={n:{'vertices':len(bpy.data.objects[n].data.vertices),'faces':len(bpy.data.objects[n].data.polygons),'matrix_world':[[float(v) for v in row] for row in bpy.data.objects[n].matrix_world]} for n in names}
result={'revision':9,'saved_asset_reopened':True,'asset':'modular/buildings/krannert_building.blend','blender_version':bpy.app.version_string,
 'source_photo_support':'Purdue University Events current exterior photo and Indiana Architect Oct 1965 p.32 support narrow vertical glazed strips separated by broad pale piers, with fine floor/transom lines.',
 'edits':['Replaced centered bay piers with 0.72 m full-height piers at bay boundaries.','Changed each windowed bay to one centered 1.25 m maximum vertical glazing strip.','Reduced opaque spandrel height from 1.10 m to 0.28 m; kept fine 0.045 m sill/head/transom mullions.','Retained all existing footprint, roof, floor elevations, entrance, seam/courtyard, interior, and master placement geometry.'],
 'facade_meshes_before':before,'facade_meshes_after_reopen':after,
 'collection_object_count':len(col.all_objects),'mesh_object_count':sum(1 for o in col.all_objects if o.type=='MESH'),
 'preserved_asset_root_identity':all(abs(bpy.data.objects['AssetRoot_krannert_building'].matrix_world[i][j]-(1.0 if i==j else 0.0))<1e-7 for i in range(4) for j in range(4)),
 'uncertainties':['The photo perspective does not provide measured bay widths; 1.25 m glazing and 0.72 m piers are visual proportions, not surveyed dimensions.','Facade orientation is matched to the documented south/front view; hidden/re-entrant face details remain uncertain.','Courtyard/re-entrant gap and roof/penthouse levels remain unchanged and unverified.']}
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

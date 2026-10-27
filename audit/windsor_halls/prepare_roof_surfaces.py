"""Prepare steep roof facets from GIS footprints using local Shapely.

The resulting triangle data is bundled beside the build script so Blender's
asset-generation run itself has no third-party dependency.
"""
import json, math, os
from shapely.geometry import Polygon, Point
from shapely import constrained_delaunay_triangles

HERE=os.path.dirname(__file__)
SOURCE=os.path.join(HERE,"sources","purdue_gis_windsor_fids_63_66_277_278_2026-10-26.geojson")
OUT=os.path.join(HERE,"roof_surfaces.json")
ORIGIN_LAT,ORIGIN_LON=40.4274,-86.9137
INSETS={63:3.0,64:3.0,65:3.0,66:.35}
RIDGE_EXPONENT={63:0.95,64:0.92,65:0.98}
SUBDIVISION_LEVELS=3
ROOF_EDGE_INSET_M=0.3
ROOF_PLAN_SIMPLIFY_M=0.55
data=json.load(open(SOURCE,encoding="utf-8"))
features={f["properties"]["FID"]:f for f in data["features"]}
output={"method":"Warren/Wood/Vawter use separately constrained, midpoint-refined roof plans inset 0.3m and simplified 0.55m solely to smooth GIS digitization steps. Height follows a near-linear distance-to-roof-boundary profile normalized by sampled inradius, yielding estimated ridge planes without broad flat caps. Structural shells remain on the exact GIS ring. FID66 retains its previous low roof form because its subgrade relationship is unresolved.","source_crs":"EPSG:4326","project_transform":"X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040","inset_m":INSETS,"roof_edge_inset_m":ROOF_EDGE_INSET_M,"roof_plan_simplify_m":ROOF_PLAN_SIMPLIFY_M,"ridge_height_profile_exponent":RIDGE_EXPONENT,"subdivision_levels":SUBDIVISION_LEVELS,"components":{}}
for fid,inset in INSETS.items():
    ring=[((lon+86.9137)*111412.84*math.cos(math.radians(ORIGIN_LAT)),(lat-40.4274)*111040) for lon,lat,*_ in features[fid]["geometry"]["coordinates"][0]]
    footprint=Polygon(ring)
    cap=footprint.buffer(-inset,join_style="mitre")
    if cap.geom_type!="Polygon" or cap.is_empty: raise RuntimeError(f"Inset geometry invalid for FID {fid}: {cap.geom_type}")
    annulus=footprint.difference(cap)
    def triangles(geom,mode):
        geoms=list(geom.geoms) if geom.geom_type=="MultiPolygon" else [geom]
        result=[]
        for poly in geoms:
            for tri in constrained_delaunay_triangles(poly).geoms:
                if not poly.covers(tri): continue
                coords=list(tri.exterior.coords)[:3]
                if mode=="cap": factors=[1.,1.,1.]
                else: factors=[min(1.,max(0.,footprint.boundary.distance(Point(x,y))/inset)) for x,y in coords]
                result.append([[round(x,7),round(y,7),round(t,6)] for (x,y),t in zip(coords,factors)])
        return result
    if fid in RIDGE_EXPONENT:
        # Start with exact constrained coverage of the whole building polygon.
        # Midpoint refinement makes the distance-field ridge legible without
        # adding a broad, level cap that hides upper facade and courtyard walls.
        roof_plan=footprint.buffer(-ROOF_EDGE_INSET_M,join_style="mitre").simplify(ROOF_PLAN_SIMPLIFY_M,preserve_topology=True)
        if roof_plan.geom_type!="Polygon" or roof_plan.is_empty:
            raise RuntimeError(f"Invalid simplified roof plan for FID {fid}: {roof_plan.geom_type}")
        vertices=[]; faces=[]; vertex_map={}
        for source_tri in constrained_delaunay_triangles(roof_plan).geoms:
            if not roof_plan.covers(source_tri):
                continue
            coords=[tuple(xy) for xy in list(source_tri.exterior.coords)[:3]]
            pieces=[coords]
            for _ in range(SUBDIVISION_LEVELS):
                next_pieces=[]
                for a,b,c in pieces:
                    ab=((a[0]+b[0])/2,(a[1]+b[1])/2)
                    bc=((b[0]+c[0])/2,(b[1]+c[1])/2)
                    ca=((c[0]+a[0])/2,(c[1]+a[1])/2)
                    next_pieces.extend([(a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)])
                pieces=next_pieces
            for tri in pieces:
                face=[]
                for x,y in tri:
                    key=(round(x,7),round(y,7))
                    if key not in vertex_map:
                        vertex_map[key]=len(vertices); vertices.append((x,y))
                    face.append(vertex_map[key])
                faces.append(tuple(face))
        distances=[roof_plan.boundary.distance(Point(x,y)) for x,y in vertices]
        max_distance=max(distances)
        heights=[min(1.0,(d/max_distance)**RIDGE_EXPONENT[fid]) if max_distance else 0.0 for d in distances]
        neighbors=[set() for _ in vertices]
        for a,b,c in faces:
            for u,v in ((a,b),(b,c),(c,a)):
                neighbors[u].add(v); neighbors[v].add(u)
        fixed=[d<0.08 for d in distances]
        # The distance field has ridges where a vertex becomes equidistant from
        # multiple walls. A short constrained Laplacian pass removes sampling
        # spikes while keeping eaves at zero and leaving the medial ridges high.
        for _ in range(18):
            updated=heights[:]
            for i,adj in enumerate(neighbors):
                if adj and not fixed[i]:
                    mean=sum(heights[j] for j in adj)/len(adj)
                    updated[i]=0.62*heights[i]+0.38*mean
            heights=updated
        full=[[[round(vertices[i][0],7),round(vertices[i][1],7),round(heights[i],6)] for i in face] for face in faces]
        if not full: raise RuntimeError(f"Missing full roof triangles for FID {fid}")
        output["components"][str(fid)]={"inset_m":inset,"footprint_area_m2":footprint.area,"roof_plan_area_m2":roof_plan.area,"sampled_max_inradius_m":max_distance,"cap_area_m2":cap.area,"roof_triangles":full,"profile":"smoothed near-linear distance-field gable/hip blend; estimated ridges and no broad level cap"}
    else:
        shell=triangles(annulus,"slope")
        top=triangles(cap,"cap")
        if not shell or not top: raise RuntimeError(f"Missing roof triangles for FID {fid}")
        output["components"][str(fid)]={"inset_m":inset,"footprint_area_m2":footprint.area,"cap_area_m2":cap.area,"slope_triangles":shell,"cap_triangles":top,"profile":"low estimated service roof; footprint and subgrade relation preserved"}
json.dump(output,open(OUT,"w",encoding="utf-8"),indent=2)
print("wrote",OUT,{fid:len(v.get("roof_triangles",[])) or (len(v["slope_triangles"]),len(v["cap_triangles"])) for fid,v in output["components"].items()})

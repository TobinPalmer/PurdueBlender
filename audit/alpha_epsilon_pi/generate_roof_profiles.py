"""Build a triangulated mansard surface from safe offsets of the GIS outline."""
import json
import math
from pathlib import Path
from shapely.geometry import Polygon, Point
from shapely import constrained_delaunay_triangles

root = Path(__file__).resolve().parent
data = json.loads((root / "purdue_gis_features_fid754_821.json").read_text(encoding="utf-8-sig"))
feature = next(f for f in data["features"] if int(f["properties"]["FID"]) == 754)
lat0, lon0 = 40.4274, -86.9137
lon_scale = 111412.84 * math.cos(math.radians(lat0))
lat_scale = 111040.0
ll = feature["geometry"]["coordinates"][0]
if ll[0] == ll[-1]: ll = ll[:-1]
xy = [((lon-lon0)*lon_scale, (lat-lat0)*lat_scale) for lon,lat in ll]
poly = Polygon(xy)
assert poly.is_valid and poly.geom_type == "Polygon"
center = poly.centroid
offsets = {"eave":0.25,"mansard_break":-1.3,"top_cap":-4.0}
zvals = {"eave":9.48,"mansard_break":11.03,"top_cap":12.38}
profiles = {k:poly.buffer(v,join_style="mitre") for k,v in offsets.items()}
assert all(p.is_valid and p.area>0 and p.geom_type=="Polygon" for p in profiles.values())
regions = {
    "lower_slope":profiles["eave"].difference(profiles["mansard_break"]),
    "upper_slope":profiles["mansard_break"].difference(profiles["top_cap"]),
    "flat_cap":profiles["top_cap"]
}

def mesh_for(region, low_profile=None, high_profile=None, zlo=0.0, zhi=0.0):
    out=constrained_delaunay_triangles(region)
    triangles=list(out.geoms)
    vertices=[]; faces=[]
    for tri in triangles:
        coords=list(tri.exterior.coords)[:-1]
        if len(coords)!=3: continue
        face=[]
        for x,y in coords:
            lx,ly=x-center.x,y-center.y
            if low_profile is None:
                z=zhi
            else:
                # Boundary vertices are on exactly one contour; representative
                # point is used only when a constraint has a tiny numerical gap.
                dp=low_profile.boundary.distance(Point(x,y))
                dq=high_profile.boundary.distance(Point(x,y))
                z=zlo if dp<=dq else zhi
            face.append(len(vertices));vertices.append([lx,ly,z])
        faces.append(face)
    return {"vertices":vertices,"faces":faces,"triangles":len(faces),"area_m2":region.area}

surfaces={
  "lower_slope":mesh_for(regions["lower_slope"],profiles["eave"],profiles["mansard_break"],zvals["eave"],zvals["mansard_break"]),
  "upper_slope":mesh_for(regions["upper_slope"],profiles["mansard_break"],profiles["top_cap"],zvals["mansard_break"],zvals["top_cap"]),
  "flat_cap":mesh_for(regions["flat_cap"],None,None,zvals["top_cap"],zvals["top_cap"])
}
result={
  "source_feature_id":754,
  "units":"meters in local east/north frame",
  "coordinate_origin_xy_m":[center.x,center.y],
  "method":"Topology-safe Shapely mitre buffers; constrained Delaunay triangulation of the regions between contours; each roof triangle vertex is assigned the corresponding low/high contour elevation. Offsets and elevations are design estimates, not measured roof dimensions.",
  "profiles":{k:{"offset_m":offsets[k],"z_m":zvals[k],"perimeter_m":p.exterior.length,"area_m2":p.area,"points_local_xy":[[x-center.x,y-center.y] for x,y in list(p.exterior.coords)[:-1]]} for k,p in profiles.items()},
  "surfaces":surfaces
}
(root/"roof_profiles.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps({k:{"triangles":v["triangles"],"surface_area_m2":v["area_m2"]} for k,v in surfaces.items()},indent=2))

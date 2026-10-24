"""Build conservative local-frame mass polygons from the public 2018 NDHM.

The masks are constrained to official GIS FID 642 and exclude the current
modeled shell bounding rectangle so the derived solids only fill omitted plan
areas. Height-band tops use median NDHM samples; they are coarse, not floor
or roof-plan measurements.
"""
import json, math
from pathlib import Path

import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.features import geometry_mask, shapes
from shapely.geometry import Polygon, box, mapping, shape, Point
from shapely.ops import transform as shp_transform, unary_union
from shapely import constrained_delaunay_triangles

root = Path(__file__).resolve().parent
src = root / "sources"
ds = rasterio.open(src / "tippecanoe_ndhm_clip_r5.tif")
nd = ds.read(1, masked=True)
valid = ~np.ma.getmaskarray(nd)
gis = json.load(open(src / "gis_feature_642_20261024.json", encoding="utf-8-sig"))
gis_geom_3857 = Polygon(gis["features"][0]["geometry"]["rings"][0])
merc_to_sp = Transformer.from_crs(3857, 2968, always_xy=True)
sp_to_merc = Transformer.from_crs(2968, 3857, always_xy=True)
merc_to_ll = Transformer.from_crs(3857, 4326, always_xy=True)
gis_geom_sp = shp_transform(lambda x, y, z=None: merc_to_sp.transform(x, y), gis_geom_3857)
gis_mask = geometry_mask([mapping(gis_geom_sp)], out_shape=nd.shape,
                         transform=ds.transform, invert=True)

def sp_to_local(x, y, z=None):
    mx, my = sp_to_merc.transform(x, y)
    lon, lat = merc_to_ll.transform(mx, my)
    lat0, lon0 = 40.4274, -86.9137
    return ((lon-lon0)*111412.84*math.cos(math.radians(lat0))+109.0,
            (lat-lat0)*111040.0-400.1893310546875)

# Existing source shell extent, derived from the saved R4 geometry validation.
shell_bounds = box(-63.0, -29.6893425, 63.0, -3.1893189)
bands = [(14.0, 18.0, "wing_low"), (18.0, 20.0, "wing_mid"),
         (20.0, 40.0, "roof_high")]
features, summaries = [], []
cell_height_m = 0.304800609601219

for low, high, name in bands:
    vals_m = nd.data * cell_height_m
    mask = gis_mask & valid & (vals_m >= low) & (vals_m < high)
    # Keep height statistics outside the pre-existing shell, in the same local frame.
    samples = []
    for r, c in zip(*np.nonzero(mask)):
        sx = ds.transform.c + (c + .5) * ds.transform.a
        sy = ds.transform.f + (r + .5) * ds.transform.e
        lx, ly = sp_to_local(sx, sy)
        if not shell_bounds.contains(Point(lx, ly)):
            samples.append(float(vals_m[r, c]))
    if len(samples) < 20:
        continue
    median = float(np.median(samples))
    geom_sp = unary_union([shape(g) for g, value in shapes(
        mask.astype("uint8"), mask=mask, transform=ds.transform) if value == 1])
    geom_local = shp_transform(sp_to_local, geom_sp).difference(shell_bounds)
    # Simplify each region then union again so raster fragments that touch
    # along an edge become a single watertight mass instead of duplicate walls.
    raw_parts = list(geom_local.geoms) if geom_local.geom_type == "MultiPolygon" else [geom_local]
    geom_local = unary_union([p.simplify(.65, preserve_topology=True) for p in raw_parts]).buffer(0)
    polygons = list(geom_local.geoms) if geom_local.geom_type == "MultiPolygon" else [geom_local]
    polygons = [p for p in polygons if p.geom_type == "Polygon" and p.area >= 12.0]
    parts = []
    for poly in polygons:
        # Shapely triangulation provides top/bottom caps even for polygons with holes.
        tris = []
        for tri in constrained_delaunay_triangles(poly).geoms:
            if tri.area > 1e-5:
                tris.append([[float(x), float(y)] for x, y in list(tri.exterior.coords)[:3]])
        parts.append({
            "outer": [[float(x), float(y)] for x, y in poly.exterior.coords[:-1]],
            "holes": [[[float(x), float(y)] for x, y in ring.coords[:-1]] for ring in poly.interiors],
            "triangles": tris,
            "area_m2": float(poly.area),
            "bounds_local_m": [float(v) for v in poly.bounds],
        })
    features.append({"type": "Feature", "properties": {
        "class": name, "ndhm_threshold_m": [low, high],
        "median_top_height_m": median, "p10_p90_sample_height_m": [
            float(np.percentile(samples, 10)), float(np.percentile(samples, 90))],
        "sample_cells_outside_shell": len(samples),
        "method": "2018 5-ft NDHM cells polygonized within official GIS FID 642; transformed into building local frame and clipped outside saved source shell bounds; simplified 0.65m; height set to outside-shell band median.",
        "uncertainty": "Coarse roof/wall envelope only. Raster height does not distinguish floors, parapets, canopies, or exact wall line. No room layout, facade openings, or story claims."
    }, "geometry": {"type": "MultiPolygon", "coordinates": [
        [ring + [ring[0]] for ring in [part["outer"]] + part["holes"]]
        for part in parts]}})
    # Coordinates + cap triangulation retained as a project-specific mesh recipe.
    features[-1]["properties"]["parts"] = parts
    area = sum(p["area_m2"] for p in parts)
    summaries.append({"class": name, "source_threshold_m": [low, high],
                      "median_top_height_m": median,
                      "p10_p90_sample_height_m": [float(np.percentile(samples, 10)), float(np.percentile(samples, 90))],
                      "sample_cells_outside_shell": len(samples), "area_m2": area,
                      "part_count": len(parts), "triangle_count": sum(len(p["triangles"]) for p in parts)})

out = {"type": "FeatureCollection", "name": "Neil Armstrong Hall R5 coarse NDHM-derived masses",
       "crs": {"name": "Purdue project building-local meters; X east, Y north, Z up"},
       "source_crs": "EPSG:2968, US survey feet; normalized height converted to meters",
       "features": features,
       "properties": {"source": "2018 Tippecanoe 3DEP NDHM, 5-ft grid; official GIS feature 642; shell bounds from validation_r4.json",
                       "summaries": summaries}}
json.dump(out, open(root / "sources/lidar_wing_zones_r5.json", "w", encoding="utf-8"), indent=2)
print(json.dumps(summaries, indent=2))

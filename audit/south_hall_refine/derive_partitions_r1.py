"""Produce a documented rough split for residential mass vs. low dining connector."""
import json
from pathlib import Path
from shapely.geometry import Polygon, LineString
from shapely.ops import split

HERE=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\south_hall_refine")
fp=json.loads((HERE/"gis_footprint_r1.json").read_text(encoding="utf-8"))
poly=Polygon(fp["local_outline_xy_m"])
# The board site plan distinguishes residential (blue) from the dining/link arm (tan).
# It is not georeferenced, so y=5m is only a morphology-based approximate split line.
pieces=list(split(poly,LineString([(-100.0,5.0),(100.0,5.0)])).geoms)
connector=max(pieces,key=lambda p:p.bounds[3])
residential=max(pieces,key=lambda p:p.area)
assert connector.area<residential.area and connector.bounds[3]>20
data={
 "building_id":"south_hall",
 "source":"2023 Purdue Board site plan Exhibit A; see purdue_board_hillenbrand_south_siteplan_2023.pdf and board_siteplan-6.png",
 "split_method":"approximate horizontal clip at local Y=5m, selected to isolate the narrow north arm seen as the tan dining/link zone; the plan is not georeferenced",
 "split_y_local_m":5.0,
 "uncertainty":"connector/residential boundary and exact endpoint are approximate (about 3 m); verify against georeferenced architectural drawing when available",
 "residential_outline_xy_local_m":[[round(x,5),round(y,5)] for x,y in list(residential.exterior.coords)[:-1]],
 "residential_area_m2":residential.area,
 "connector_outline_xy_local_m":[[round(x,5),round(y,5)] for x,y in list(connector.exterior.coords)[:-1]],
 "connector_area_m2":connector.area,
 "total_gis_area_m2":poly.area,
 "connector_roof_height_m_estimated":7.3152
}
(HERE/"gis_partition_r1.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:data[k] for k in ["residential_area_m2","connector_area_m2","total_gis_area_m2","split_y_local_m","uncertainty"]},indent=2))

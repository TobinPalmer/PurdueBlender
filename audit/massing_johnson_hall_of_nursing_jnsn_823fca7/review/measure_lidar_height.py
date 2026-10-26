"""Recompute JNSN roof height from the official 2018 COPC tile.

Requires laspy[lazrs], shapely, pyproj. The raw COPC is intentionally kept under
work/jnsn rather than committed in the audit folder.
"""
import json, math, pathlib, sys
import laspy
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely import contains_xy

ROOT=pathlib.Path(__file__).resolve().parents[3]
AUDIT=ROOT/'audit/massing_johnson_hall_of_nursing_jnsn_823fca7'
TILE=ROOT/'work/jnsn/in2018_29951885_12.copc.laz'
if len(sys.argv)>1: TILE=pathlib.Path(sys.argv[1])
feature=json.loads((AUDIT/'sources/purdue_building_shapes_fid218_jnsn.json').read_text(encoding='utf-8-sig'))['feature']
ring=feature['geometry']['rings'][0]
project=Transformer.from_crs(4326,2968,always_xy=True)
poly=Polygon([project.transform(lon,lat) for lon,lat in ring])
# EPSG:2968 coordinates use US survey feet; convert the requested metric buffers.
inner=poly.buffer(-3.0/0.3048006096012192)
outer=poly.buffer(5.0/0.3048006096012192).difference(poly)
las=laspy.read(TILE)
x=las.x; y=las.y; z=las.z; cls=las.classification
# Restrict vector operations to each polygon's bounding box before exact tests.
ib=inner.bounds; ob=outer.bounds
import numpy as np
im=(cls==1)&(x>=ib[0])&(x<=ib[2])&(y>=ib[1])&(y<=ib[3])
candidate_inside=np.flatnonzero(im)
inside_idx=candidate_inside[contains_xy(inner,x[candidate_inside],y[candidate_inside])]
gm=(cls==2)&(x>=ob[0])&(x<=ob[2])&(y>=ob[1])&(y<=ob[3])
candidate_ground=np.flatnonzero(gm)
ground_idx=candidate_ground[contains_xy(outer,x[candidate_ground],y[candidate_ground])]
ground=np.asarray(z[ground_idx],dtype=float)
inside=inside_idx
assert len(inside)>0 and len(ground)>0
base=float(np.median(ground))
heights=(np.asarray(z[inside],dtype=float)-base)*0.3048
q=lambda p: float(np.partition(heights,min(len(heights)-1,math.ceil(p*len(heights))-1))[min(len(heights)-1,math.ceil(p*len(heights))-1)])
result={'source_file':TILE.name,'interior_class1_count':int(len(inside)),'exterior_class2_ground_count':int(len(ground)),'ground_median_ftUS':base,'roof_height_median_m':q(.5),'roof_height_p95_m':q(.95),'roof_height_p99_m':q(.99),'roof_height_max_m':float(heights.max())}
print(json.dumps(result,indent=2))

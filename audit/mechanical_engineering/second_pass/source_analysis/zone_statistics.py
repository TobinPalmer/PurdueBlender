from pathlib import Path
import numpy as np,json
from matplotlib.path import Path as Poly
p=Path(__file__).resolve().parent;a=np.load(p/'class1_asset_local_xyz.npy')
zones={'1932':[[-33.66,13.69],[20.27,57.90],[32.66,42.77],[-21.27,-1.44]],'1929':[[6.35,23],[20.24,24],[47.2,-17.25],[38.69,-24.32]],'1942':[[32.46,42.62],[62.70,5.62],[50.89,-4.03],[20.82,32.77]],'Gatewood_bbox':[[-54,-34],[-3,-34],[-3,10],[-54,10]]}
out={'warning':'Approximate modeler-supplied zones; vertices are not surveyed wing boundaries. Class1 unclassified surfaces include equipment and vegetation; these distributions are candidate height constraints, not wall/eave/ridge measurements. Ground reference pooled median622.56ftUS; units converted ftUS to m.'}
for name,vs in zones.items():
 z=a[Poly(vs).contains_points(a[:,:2]),2];high=z[z>8]
 out[name]={'polygon_asset_local_m':vs,'all_count':len(z),'all_p10_p50_p75_p90_p99_m':np.percentile(z,[10,50,75,90,99]).tolist(),'above8m_count':len(high),'above8m_p10_p50_p75_p90_p99_m':np.percentile(high,[10,50,75,90,99]).tolist()}
(p/'zone_statistics.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

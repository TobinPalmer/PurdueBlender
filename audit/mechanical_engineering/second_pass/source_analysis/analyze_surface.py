from pathlib import Path
import laspy, numpy as np, pyproj, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json, csv, hashlib
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
src=ROOT/"research/second_pass/buildings/mechanical_engineering/data/lidar"
rows=[];ground=[];sources=[]
for p in src.glob("*.laz"):
 las=laspy.read(p);t=pyproj.Transformer.from_crs(las.header.parse_crs(),4326,always_xy=True)
 lon,lat=t.transform(np.asarray(las.x),np.asarray(las.y));x=(lon+86.9137)*111412.84*np.cos(np.radians(40.4274))-66.30000114440918;y=(lat-40.4274)*111040.-86.5
 z=np.asarray(las.z);cls=np.asarray(las.classification)
 ground.extend(z[cls==2]);mask=cls==1
 rows.append(np.column_stack([x[mask],y[mask],z[mask]]));sources.append({"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
a=np.concatenate(rows);g=float(np.median(ground));a[:,2]=(a[:,2]-g)*0.30480060960121924
np.save(OUT/"class1_asset_local_xyz.npy",a)
ix=np.floor(a[:,:2]).astype(int);cells={}
for xy,z in zip(ix,a[:,2]):cells.setdefault(tuple(xy),[]).append(z)
data=[]
for (x,y),zs in sorted(cells.items()):data.append([x+.5,y+.5,len(zs),*np.percentile(zs,[10,50,75,90,99])])
with (OUT/"surface_grid_1m.csv").open("w",newline="") as f:
 w=csv.writer(f);w.writerow(["asset_local_x_m","asset_local_y_m","count","p10_height_m","p50_height_m","p75_height_m","p90_height_m","p99_height_m"]);w.writerows(data)
d=np.asarray(data);fig,ax=plt.subplots(figsize=(13,10));sc=ax.scatter(d[:,0],d[:,1],c=d[:,5],s=10,marker="s",cmap="turbo",vmin=0,vmax=26);fig.colorbar(sc,ax=ax,label="Class-1 p75 height over pooled class-2 median (m)")
ax.set(xlabel="Asset local X east (m)",ylabel="Asset local Y north (m)",title="ME 2018 LiDAR candidate upper surfaces — 1m bins; vegetation/equipment included");ax.set_aspect("equal");ax.grid(alpha=.25);fig.savefig(OUT/"surface_grid_1m.png",dpi=160);plt.close(fig)
(OUT/"provenance.json").write_text(json.dumps({"sources":sources,"capture":"2018-04-20","source_crs":"NAD83(HARN) Indiana West ftUS + NAVD88 ftUS Geoid12B","project_conversion":"repository approximate lon/lat conversion; asset marker subtract66.30000114440918,86.5","ground_median_ftUS":g,"ground_count":len(ground),"class1_count":len(a),"method":"1m XY bins; candidate surface quantiles; no roof classifications; no automated eave/ridge claims","uncertainty":"Class1 includes roofs, vegetation, equipment, canopy and non-ground features; 2018 predates2023-25 renovation. Ground median is pooled crop context, not per-wing surveyed datum."},indent=2))
print(json.dumps({"ground_ftUS":g,"points":len(a),"bins":len(data),"output":str(OUT)}))

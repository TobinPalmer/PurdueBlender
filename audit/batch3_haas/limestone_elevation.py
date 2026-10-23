import bpy,json
from pathlib import Path
p=bpy.data.filepath;c=bpy.data.collections['Asset_felix_haas_hall'];stone=bpy.data.materials['HAAS_Photo_Limestone']
# Replace earlier separate stone patch pieces with a connected elevation skin whose cell boundaries align to openings.
for o in list(bpy.data.objects):
 if o.name.startswith('HAAS_Photo_StonePanel_'):bpy.data.objects.remove(o,do_unlink=True)
# The east-facing entrance wall is treated as a photo-derived elevation skin; actual wall, window, door and GIS footprint stay intact.
yedges={-12.0,12.0,-4.9,-4.1,4.1,4.9}
for center in [-7.65,0,7.65]:yedges.update([center-1.6,center+1.6])
for center in [-7.65,7.65]:yedges.update([center-1.5,center+1.5])
yedges.update([-1.1,1.1]);ys=sorted(yedges)
zs=[.45,.5,1.5,3.14,4.7,5.4,5.8,6.9,8.5,9.1,10.2]
verts=[];faces=[];skipped=0
for a,b in zip(ys,ys[1:]):
 ym=(a+b)/2
 for z0,z1 in zip(zs,zs[1:]):
  zm=(z0+z1)/2
  hole=False
  if 6.9<=zm<8.5 and any(abs(ym-center)<1.6 for center in [-7.65,0,7.65]):hole=True
  if 1.5<=zm<4.7 and any(abs(ym-center)<1.5 for center in [-7.65,7.65]):hole=True
  if .5<=zm<3.14 and abs(ym)<1.1:hole=True
  # Narrow dark brick pilasters between pale bays, visible through this skin.
  if abs(ym-4.5)<.4 or abs(ym+4.5)<.4:hole=True
  if hole:skipped+=1;continue
  k=len(verts);verts.extend([(13.005,a,z0),(13.005,b,z0),(13.005,b,z1),(13.005,a,z1)]);faces.append((k,k+1,k+2,k+3))
mesh=bpy.data.meshes.new('HAAS_Photo_Limestone_Elevation_Mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('HAAS_Photo_Entrance_Limestone_Facade',mesh);c.objects.link(o);mesh.materials.append(stone);o['evidence']='Purdue Felix Haas Hall exterior photo gallery: https://events.purdue.edu/felix_haas_hall ; elevation regions interpreted qualitatively, dimensions estimated.';o['openings']='Three upper windows; two lower windows; central entrance, positions aligned to existing window/door meshes.'
bpy.ops.wm.save_as_mainfile(filepath=p)
Path('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/limestone_elevation.json').write_text(json.dumps({'objects':[o.name],'face_count':len(faces),'opening_cells_skipped':skipped,'source':'https://events.purdue.edu/felix_haas_hall','method':'metric planar cells aligned to current apertures; narrow underlying red-brick pilaster zones preserved','limitations':'Photo perspective lacks measured elevation dimensions; panel geometry estimated'},indent=2))

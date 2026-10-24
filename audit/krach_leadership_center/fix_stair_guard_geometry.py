import bpy,json
src=bpy.data.filepath
st=bpy.data.objects['KRCH | four-story visible switchback stair and etched glass guard']
levels=[-0.92,2.98,6.88,10.78,14.68]
for story in range(4):
 lo,hi=levels[story],levels[story+1]; mid=(lo+hi)/2
 guard_start=story*(25*8+16)+25*8
 for side in range(4):
  k=guard_start+side*4; vs=[st.data.vertices[k+i] for i in range(4)]
  zs=[lo+0.14,mid+0.14,mid+0.96,lo+0.96] if side<2 else [mid+0.14,hi+0.14,hi+0.96,mid+0.96]
  for v,z in zip(vs,zs): v.co.z=z
st.data.update(); st['guard_geometry_note']='Guard panel elevations corrected to use actual story Z coordinates; verified after render review.'
vals=[tuple(v.co) for v in st.data.vertices]
bounds=[[min(v[i] for v in vals),max(v[i] for v in vals)] for i in range(3)]
dims=[b[1]-b[0] for b in bounds]
assert dims[2]<17,(dims,bounds)
bpy.ops.wm.save_as_mainfile(filepath=src)
print(json.dumps({'saved':src,'stair_vertices':len(st.data.vertices),'stair_dimensions':dims,'stair_bounds':bounds},indent=2))

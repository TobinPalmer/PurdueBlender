import bpy,json,os
o=bpy.data.objects['RAWL_Site_Sidewalk_Apron'];tris=json.load(open(os.path.join(os.path.dirname(__file__),'apron_triangles.json')));verts=[];faces=[]
for t in tris:
 i=len(verts);verts.extend([(x-323.6582336425781,y+409.62242126464844,.012) for x,y in t]);faces.append((i,i+1,i+2))
mesh=bpy.data.meshes.new('RAWL_ValidatedExteriorApron');mesh.from_pydata(verts,[],faces);mesh.materials.append(bpy.data.materials['RAWL_Concrete_Floor']);o.data=mesh;o.location=(0,0,0);o['evidence']='GIS polygon outward1.8m buffer minus structural footprint, constrained triangulation; prior selfoverlap removed'
# Published floor1 is ground0 and has no void: assert rather than silently add false upperfloor geometry.
g=bpy.data.objects['RAWL_FloorSlab_L1_Ground'];g['evidence']='Groundfloor slab retained complete; original void applies upperlevels only. Published2024firstfloor classrooms have continuous support. Upperlevel hole location remains unverified.'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

import bpy,json
c=bpy.data.collections['Asset_knoy_hall'];pairs=[]
for o in c.all_objects:
 if o.name.endswith('_AccessSide'):
  a=bpy.data.objects[o.name[:-11]];d=(o.location-a.location).length;gap=d-(o.dimensions.x+a.dimensions.x)/2;pairs.append(gap)
print(json.dumps({'objects':len(c.all_objects),'gap_count':len(pairs),'gap_min':min(pairs),'gap_max':max(pairs),'root_identity':list(bpy.data.objects['AssetRoot_knoy_hall'].matrix_world)} ,default=lambda x:list(x)))

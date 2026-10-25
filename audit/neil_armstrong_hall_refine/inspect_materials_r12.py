import bpy,json
out=[]
for name in ["ARMS_Mayflower_Red_ACM","ARMS_Sea_Wolf_ACM","ARMS_R9_Light_Roof_Surface"]:
 m=bpy.data.materials[name]
 row={"name":name,"diffuse":list(m.diffuse_color),"nodes":m.use_nodes}
 if m.use_nodes:
  b=next((n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED"),None)
  if b: row.update({"base_color":list(b.inputs["Base Color"].default_value),"metallic":float(b.inputs["Metallic"].default_value),"roughness":float(b.inputs["Roughness"].default_value)})
 out.append(row)
print(json.dumps(out,indent=2))

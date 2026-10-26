import bpy
prop = bpy.types.Material.bl_rna.properties.get("surface_render_method")
print("SURFACE_RENDER_METHODS", [item.identifier for item in prop.enum_items] if prop else None)
mat = bpy.data.materials.new("GlassCapabilityProbe")
mat.use_nodes = True
print("PRINCIPLED_INPUTS", [item.name for item in mat.node_tree.nodes.get("Principled BSDF").inputs])

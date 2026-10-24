import bpy
import os
import sys

targets = {
    "potter_engineering.blend": "POTR",
    "mechanical_engineering.blend": "ME",
    "electrical_engineering.blend": "BHEE",
}
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "modular", "buildings"))

def get_input(bsdf, name):
    return bsdf.inputs.get(name)

for filename, prefix in targets.items():
    path = os.path.join(root, filename)
    bpy.ops.wm.open_mainfile(filepath=path)
    changed = []
    for mat in bpy.data.materials:
        if not mat.name.startswith(prefix) or not mat.use_nodes or not mat.node_tree:
            continue
        name = mat.name.lower()
        # Leave glazing, metals, fabrics, and interior worktops smooth.
        if any(tag in name for tag in ("glass", "metal", "steel", "bronze", "fabric", "carpet", "worktop", "drawerhandles", "stainless")):
            continue
        is_brick = "brick" in name or "tile" in name
        is_roof = "roof" in name or "membrane" in name
        is_stone = any(tag in name for tag in ("limestone", "concrete", "precast", "terrazzo", "enamel"))
        is_paint = "paint" in name or "partition" in name
        if not (is_brick or is_roof or is_stone or is_paint):
            continue
        nt = mat.node_tree
        nodes = nt.nodes
        links = nt.links
        bsdf = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf is None:
            continue
        # Replace the first-pass graph with a meter-scaled, very restrained grain.
        # Generated coordinates stretched the pattern over whole facade objects.
        for n in list(nodes):
            if n.label in ("Procedural surface coordinates", "Subtle material grain", "Fine surface relief"):
                nodes.remove(n)
        texcoord = nodes.new("ShaderNodeTexCoord")
        texcoord.label = "Meter-scaled surface coordinates"
        noise = nodes.new("ShaderNodeTexNoise")
        noise.label = "Low contrast material grain"
        noise.inputs["Scale"].default_value = 7.0 if is_brick else (4.0 if is_stone else 5.0)
        noise.inputs["Detail"].default_value = 1.0
        noise.inputs["Roughness"].default_value = 0.5
        links.new(texcoord.outputs["Object"], noise.inputs["Vector"])
        bump = nodes.new("ShaderNodeBump")
        bump.label = "Fine surface relief"
        bump.inputs["Strength"].default_value = 0.035 if is_brick else 0.022
        bump.inputs["Distance"].default_value = 0.003 if is_brick else 0.0015
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        mat["surface_detail"] = "Low contrast meter-scaled procedural grain; original palette retained"
        changed.append(mat.name)
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print("SURFACE_DETAIL", filename, "materials", len(changed), changed)

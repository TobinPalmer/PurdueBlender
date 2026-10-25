import bpy, json, os
ASSET=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lawson_hall.blend'
bpy.ops.wm.open_mainfile(filepath=ASSET)
# Photo-supported visual treatment: keep Lawson's blue-gray curtain wall reflective,
# but lift its blue-gray tint so the glazed surfaces separate from the dark bronze frames.
changes=[]
for name, color, roughness in [
    ('LWSN_Curtain_Glass', (0.105, 0.155, 0.205, 1.0), 0.23),
    ('LWSN_Rotunda_Glass', (0.105, 0.155, 0.205, 1.0), 0.23),
    ('LWSN_Spandrel_Glass', (0.155, 0.205, 0.225, 1.0), 0.34),
]:
    mat=bpy.data.materials.get(name)
    if not mat or not mat.use_nodes: raise RuntimeError('Missing expected Lawson material: '+name)
    bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not bs: raise RuntimeError('Missing Principled shader: '+name)
    bs.inputs['Base Color'].default_value=color
    bs.inputs['Roughness'].default_value=roughness
    # This remains an opaque reflective exterior-glass approximation, consistent with the existing asset.
    bs.inputs['Metallic'].default_value=0.16 if 'Spandrel' not in name else 0.12
    mat['evidence_status']='Visual material approximation guided by Purdue-published Lawson exterior photographs; not a measured glazing specification'
    mat['source_url']='https://www.purdue.edu/science/about/news/articles/2024/celebrating-2024-top-20-stories-from-the-college-of-science.html'
    changes.append({'material':name,'base_color':list(color[:3]),'roughness':roughness})
for objname in ('LWSN_Window_Glazing','LWSN_Rotunda_Curtain_Glass','LWSN_Rotunda_Spandrel_Panels'):
    ob=bpy.data.objects.get(objname)
    if ob:
        ob['evidence_status']='Photo-supported material appearance only; facade opening rhythm and dimensions remain schematic/unverified'
        ob['source_url']='https://www.purdue.edu/science/about/news/articles/2024/celebrating-2024-top-20-stories-from-the-college-of-science.html'
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.wm.open_mainfile(filepath=ASSET)
print(json.dumps({'reopened':os.path.normcase(os.path.abspath(bpy.path.abspath(bpy.data.filepath)))==os.path.normcase(os.path.abspath(ASSET)),'changes':changes},indent=2))


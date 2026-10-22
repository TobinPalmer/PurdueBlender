import bpy

framing = bpy.data.objects.get("HIKS_Pyramidal_Skylights_Bronze_Framing")
if framing:
    verts = [v.co for v in framing.data.vertices]
    # let's find the peaks
    peak_verts = [v for v in verts if v.z > 3.5]
    print(f"Total verts > 3.5m: {len(peak_verts)}")
    # group peaks
    # Let's find distinct peaks
    peaks = []
    for v in verts:
        if v.z > 3.8:
            # check if near an existing peak
            if not any((v.x - p.x)**2 + (v.y - p.y)**2 < 1.0 for p in peaks):
                peaks.append(v)
    print(f"Found {len(peaks)} skylight peaks:")
    for p in sorted(peaks, key=lambda p: (p.z, p.x), reverse=True):
        print(f"  Peak at ({p.x:.3f}, {p.y:.3f}, z={p.z:.3f})")

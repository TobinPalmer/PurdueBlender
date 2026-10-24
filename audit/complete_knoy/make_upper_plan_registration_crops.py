"""Build enlarged, source-aligned plan/trace comparisons; no blend edits."""
import bpy
import json
from pathlib import Path
import numpy as np

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
DIR = ROOT / 'audit' / 'complete_knoy'
source = bpy.data.images.load(str(DIR / 'knoy_typical_plan_crop.png'), check_existing=False)
width, height = source.size
pixels = np.asarray(source.pixels[:], dtype=np.float32).reshape((height, width, 4))[::-1].copy()
trace = json.loads((DIR / 'upper_plan_wall_trace.json').read_text(encoding='utf-8'))
segments = trace['segments']

def draw_trace(image, crop):
    """Draw registered extracted mesh centerlines on the source raster crop."""
    x0, y0, x1, y1 = crop
    h, w = image.shape[:2]
    for seg in segments:
        (ax, ay), (bx, by) = seg['source_pixels']
        length = max(abs(bx - ax), abs(by - ay))
        n = max(2, int(length * 2))
        for i in range(n + 1):
            t = i / n
            x = round(ax * (1 - t) + bx * t) - x0
            y = round(ay * (1 - t) + by * t) - y0
            if not (0 <= x < w and 0 <= y < h):
                continue
            if 0 <= x < w and 0 <= y < h:
                image[y, x, :3] = image[y, x, :3] * 0.12 + np.array((0.02, 0.48, 0.12)) * 0.88
                image[y, x, 3] = 1
    return image

def save_image(name, rgba):
    h, w = rgba.shape[:2]
    out = bpy.data.images.new(name, width=w, height=h, alpha=True)
    out.pixels[:] = rgba[::-1].astype(np.float32).reshape(-1).tolist()
    out.filepath_raw = str(DIR / f'{name}.png')
    out.file_format = 'PNG'
    out.save()
    bpy.data.images.remove(out)

# The crops focus on independently legible plan regions: the northwest room
# bays, central atrium/corridor, and southeast diagonal room wing.
crops = {
    'knoy_upper_registration_northwest': (95, 140, 355, 520),
    'knoy_upper_registration_central': (170, 430, 490, 850),
    'knoy_upper_registration_diagonal': (275, 770, 555, 1250),
}
metadata = {
    'source': trace['source_image'],
    'source_pdf_page': 24,
    'comparison_method': 'Left panel is the untouched source raster crop. Right panel is the same crop with the registered accepted interior-wall centerline trace drawn in green; the saved Blender partition meshes are extruded from these exact centerlines. This is an overlay of traced geometry, not an independent as-built measurement.',
    'registration_uncertainty': trace['registration'],
    'wall_width_m': 0.13,
    'wall_height_m': 2.8,
    'wall_height_status': 'Estimated; source is a floor plan and provides no partition heights.',
    'unresolved_items': 'Short raster details and door swings remain ambiguous; six L1 candidate openings are still unresolved and are not inferred from this upper-floor overlay.',
    'crops': {},
}
scale = 3
for name, crop in crops.items():
    x0, y0, x1, y1 = crop
    source_crop = pixels[y0:y1, x0:x1].copy()
    model_overlay = draw_trace(source_crop.copy(), crop)
    pair = np.concatenate((source_crop, model_overlay), axis=1)
    pair = np.repeat(np.repeat(pair, scale, axis=0), scale, axis=1)
    save_image(name, pair)
    metadata['crops'][name + '.png'] = {
        'source_pixel_bounds_xyxy': list(crop),
        'upscale': '3x nearest-neighbor for legibility',
        'output': f'audit/complete_knoy/{name}.png',
    }
(DIR / 'upper_plan_registration_crops.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
print(json.dumps(metadata, indent=2))

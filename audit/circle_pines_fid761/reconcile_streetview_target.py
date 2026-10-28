"""Reconcile the supplied Google Street View camera point/view with GIS FID 761."""
import json, math
from pathlib import Path

root = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ring = json.loads((root / "audit/circle_pines_fid761/initial_inspection.json").read_text(encoding="utf-8"))["gis_ring_xy_local_m"]
if ring[0] == ring[-1]:
    ring = ring[:-1]

# Google Maps URL camera coordinate and heading supplied by coordinator for
# pano ytu8Bz_eEp2xCv9QeF0xRw. Project it using the repository's local approx.
cam_lat, cam_lon, pano_yaw = 40.4350711, -86.9250796, 98.54251
cam_x = (cam_lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
cam_y = (cam_lat - 40.4274) * 111040.0

def polygon_centroid(points):
    twice_area = cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
        cross = x1 * y2 - x2 * y1
        twice_area += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    return (cx / (3 * twice_area), cy / (3 * twice_area))

centroid = polygon_centroid(ring)
dx, dy = centroid[0] - cam_x, centroid[1] - cam_y
distance = math.hypot(dx, dy)
bearing = math.degrees(math.atan2(dx, dy)) % 360.0
heading_difference = (bearing - pano_yaw + 180.0) % 360.0 - 180.0

def point_segment_distance(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    wx, wy = p[0] - a[0], p[1] - a[1]
    den = vx * vx + vy * vy
    t = 0.0 if den == 0 else max(0.0, min(1.0, (wx * vx + wy * vy) / den))
    return math.hypot(p[0] - (a[0] + t * vx), p[1] - (a[1] + t * vy))

nearest_edge = min(point_segment_distance((cam_x, cam_y), a, b)
                   for a, b in zip(ring, ring[1:] + ring[:1]))
signed_area = sum(a[0] * b[1] - b[0] * a[1]
                  for a, b in zip(ring, ring[1:] + ring[:1])) / 2.0
camera_vector = (cam_x - centroid[0], cam_y - centroid[1])
camera_norm = math.hypot(*camera_vector)
camera_vector = (camera_vector[0] / camera_norm, camera_vector[1] / camera_norm)
edge_candidates = []
for idx, (a, b) in enumerate(zip(ring, ring[1:] + ring[:1])):
    vx, vy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(vx, vy)
    # Outward normal depends on source ring winding.
    normal = (vy, -vx) if signed_area > 0 else (-vy, vx)
    norm = math.hypot(*normal)
    normal = (normal[0] / norm, normal[1] / norm)
    dot = max(-1.0, min(1.0, normal[0] * camera_vector[0] + normal[1] * camera_vector[1]))
    edge_candidates.append({
        "ring_edge_index": idx,
        "length_m": length,
        "midpoint_local_xy_m": [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2],
        "outward_normal_bearing_deg_clockwise_from_north": math.degrees(math.atan2(normal[0], normal[1])) % 360.0,
        "angle_to_camera_vector_deg": math.degrees(math.acos(dot))
    })
edge_candidates.sort(key=lambda e: (e["angle_to_camera_vector_deg"], -e["length_m"]))
print(json.dumps({
    "provider": "Google Maps Street View",
    "panoid": "ytu8Bz_eEp2xCv9QeF0xRw",
    "capture_date_shown_in_listing": "April 2026",
    "listing_date_note": "Street View listing date from Google Maps UI; not legible in the downloaded thumbnail itself.",
    "retrieved_date": "2026-10-28",
    "maps_listing_url": "https://www.google.com/maps/place/Circle+Pines/@40.4350711,-86.9250796,202a,75y,98.54h,90t/data=!3m7!1e1!3m5!1sytu8Bz_eEp2xCv9QeF0xRw!2e0!6shttps:%2F%2Fstreetviewpixels-pa.clients6.google.com%2Fv1%2Fthumbnail%3Fcb_client%3Dmaps_sv.tactile%26w%3D900%26h%3D600%26pitch%3D0%26panoid%3Dytu8Bz_eEp2xCv9QeF0xRw%26yaw%3D98.54251!7i16384!8i8192",
    "thumbnail_url": "https://streetviewpixels-pa.clients6.google.com/v1/thumbnail?cb_client=maps_sv.tactile&w=900&h=600&pitch=0&panoid=ytu8Bz_eEp2xCv9QeF0xRw&yaw=98.54251",
    "saved_image": "sources/google_streetview_panoid_ytu8Bz_eEp2xCv9QeF0xRw_2026-04.jpg",
    "camera_point_from_maps_url_wgs84": [cam_lat, cam_lon],
    "camera_point_projected_local_xy_m": [cam_x, cam_y],
    "fid_761_ring_centroid_local_xy_m": list(centroid),
    "camera_to_fid_centroid_distance_m": distance,
    "camera_to_fid_centroid_bearing_deg_clockwise_from_north": bearing,
    "maps_heading_deg_clockwise_from_north": pano_yaw,
    "heading_delta_to_centroid_deg": heading_difference,
    "camera_to_fid_polygon_minimum_edge_distance_m": nearest_edge,
    "source_ring_signed_area_m2": signed_area,
    "camera_facing_candidate_edges": edge_candidates[:6],
    "method_limit": "Geographic match uses the project approximate local transform and FID ring; camera point and heading are taken from the coordinator-supplied Google Maps pano URL, not a survey or independent panorama metadata response."
}, indent=2))

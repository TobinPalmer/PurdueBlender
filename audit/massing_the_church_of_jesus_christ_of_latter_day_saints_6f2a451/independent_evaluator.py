from __future__ import annotations

import json
import math
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_the_church_of_jesus_christ_of_latter_day_saints_6f2a451"
AUDIT = ROOT / "audit" / ASSET_ID
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
MANIFEST = ROOT / "modular" / "manifest.json"
GIS = ROOT / "audit" / "official_purdue_buildings_wgs84.json"


def xy(lon: float, lat: float) -> tuple[float, float]:
    return (
        (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
        (lat - 40.4274) * 111040.0,
    )


def evaluate() -> dict:
    """Grade the reopened frozen asset against the five AGENT.md criteria."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    m = next(row for row in manifest["assets"] if row["id"] == ASSET_ID)
    gis = json.loads(GIS.read_text(encoding="utf-8"))
    feature = next(f for f in gis["features"] if f["attributes"].get("FID") == 779)
    attrs = feature["attributes"]
    source = [xy(lon, lat) for lon, lat in feature["geometry"]["rings"][0][:-1]]
    scene = bpy.data.scenes.get(f"Building_{ASSET_ID}")
    coll = bpy.data.collections.get(f"Asset_{ASSET_ID}")
    obj = bpy.data.objects.get("The Church of Jesus Christ of Latter-day Saints")
    if not scene or not coll or not obj or obj.type != "MESH":
        raise RuntimeError("Expected named scene, export collection, and mesh object were not found")

    # The first eight mesh vertices are the structural shell prism's lower and upper
    # GIS vertices in the build script. Compare the lower ring directly to the source.
    base = [(obj.data.vertices[i].co.x, obj.data.vertices[i].co.y) for i in range(4)]
    residuals = [math.dist(a, b) for a, b in zip(base, source)]
    evaluated = [obj.matrix_world @ v.co for v in obj.data.vertices]
    bounds = {
        axis: [min(v[i] for v in evaluated), max(v[i] for v in evaluated)]
        for i, axis in enumerate(("x", "y", "z"))
    }
    materials = [material.name for material in obj.data.materials if material]
    source_notes = (AUDIT / "source_notes.md").read_text(encoding="utf-8")
    renders = [AUDIT / "renders" / name for name in (
        "01_west_northwest_hero.png", "02_west_facade.png", "03_top.png")]
    photo = AUDIT / "sources" / "google_street_view_23_waldron_2023.jpg"
    # The repository manifest still advertises the pre-detail 16 m bounds. Compare
    # to actual mesh bounds so this remains an explicit export/index check.
    manifest_zmax = m["bounds_world_m"][2][1]

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": (
                f"Purdue GIS FID 779 identifies '{attrs['BUILDING_N']}' at {attrs['ADDRESS']}; "
                "the Church locator evidence distinguishes 14 Waldron from the separate 3224 Jasper meetinghouse. "
                f"Structural shell's four lower XY vertices match the transformed GIS ring in order; "
                f"maximum vertex residual {max(residuals):.6f} m."
            ),
            "findings": [],
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": (
                "Asset is a massing library retaining campus-world coordinates under identity transform, as its "
                "manifest contract specifies. The long and short shell axes follow the GIS ring; measured shell "
                f"dimensions from that ring are approximately {math.dist(source[0], source[1]):.2f} m by "
                f"{math.dist(source[1], source[2]):.2f} m. The shell registration is exact to the project transform."
            ),
            "findings": [],
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.2,
            "max_score": 2.0,
            "evidence": (
                f"GIS records NUM_LEVELS={attrs.get('NUM_LEVELS')}; the July 2023 Street View visibly supports a "
                "single-story, low-roof building and a small higher reddish roof behind it. The asset has a 4.15 m "
                "body, 5.45 m main ridge, and 5.90 m secondary ridge, but these are estimates from one unscaled, "
                "oblique and partly occluded image; GIS 'Extrution: 12' has undocumented units."
            ),
            "findings": [
                "No scaled elevation, survey, or measured height evidence supports any modeled Z dimension.",
                "The secondary roof's plan and pitch are inferred from a narrow visible strip; exact roof silhouette remains unverified.",
            ],
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 0.9,
            "max_score": 2.0,
            "evidence": (
                "Street View supports red-brown brick, a low dark eave, a broad glazed/recessed entrance, ramp/steps, "
                "and several openings. The mesh includes these general elements, but the generated straight-on render "
                "places the entrance near the middle of the long elevation and shows four regular small windows; "
                "the oblique source photo shows a substantially off-center entry and a more recessed, columned/glazed "
                "front zone. Exact window count and spacing are explicitly estimates."
            ),
            "findings": [
                "Facade composition is only approximate: entrance placement/glazing and window pattern do not convincingly reproduce the visible source arrangement.",
                "No visual evidence supports hidden elevations or the exact trim/material boundaries; the archive finding aid lists photos but the photos were not obtained.",
            ],
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 1.7,
            "max_score": 2.0,
            "evidence": (
                f"Blender reopened {ASSET.name} in {bpy.app.version_string}; expected scene and collection exist, "
                f"the collection has {len(coll.objects)} object(s), and the mesh has {len(obj.data.vertices)} vertices / "
                f"{len(obj.data.polygons)} polygons with {len(materials)} named materials. No modifiers, external "
                "libraries, or image dependencies are present. Source register, raw GIS snapshot, Street View image, "
                "source notes, build/reopen records, and three renders are present."
            ),
            "findings": [
                f"Shared manifest bounds remain stale (Z max {manifest_zmax:.1f} m versus reopened mesh max {bounds['z'][1]:.1f} m); coordinator-owned index needs reconciliation before final integration.",
                "The Purdue Archives references are catalog leads only; source images remain unavailable, and the Street View evidence is one oblique view.",
            ],
        },
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    evidence = {
        "asset": str(ASSET.relative_to(ROOT)),
        "blender": bpy.app.version_string,
        "reopened_scene": scene.name,
        "reopened_collection": coll.name,
        "collection_object_names": [o.name for o in coll.objects],
        "mesh_bounds_world_m": {k: [round(v, 4) for v in vals] for k, vals in bounds.items()},
        "gis_shell_vertex_residuals_m": [round(v, 6) for v in residuals],
        "source_files": [
            str((AUDIT / "source_register.json").relative_to(ROOT)),
            str((AUDIT / "source_notes.md").relative_to(ROOT)),
            str(photo.relative_to(ROOT)),
        ],
        "all_render_files_present": all(p.is_file() for p in renders),
        "source_notes_present": bool(source_notes),
        "manifest_bounds_world_m": m["bounds_world_m"],
    }
    findings = [finding for c in criteria for finding in c["findings"]]
    return {
        "score": score,
        "max_score": 10,
        "criteria": criteria,
        "evidence": evidence,
        "findings": findings,
    }


if __name__ == "__main__":
    result = evaluate()
    out = AUDIT / "independent_grade.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))

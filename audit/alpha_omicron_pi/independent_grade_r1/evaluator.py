import json
from pathlib import Path

RESULT = {
  "building": "Alpha Omicron Pi, Phi Upsilon chapter house",
  "asset": "modular/buildings/massing_house_970455277_a3fb72a.blend",
  "asset_sha256": "89f51d4f9bff3fdc24c1988017b34328715c20b5b183eed92241030de7256ae0",
  "independent": True,
  "score": 7.6,
  "max_score": 10,
  "threshold": 8,
  "status": "FAIL: revision required",
  "criteria": [
    {
      "name": "Correct identity and source-backed footprint",
      "score": 2.0,
      "max_score": 2.0,
      "evidence": [
        "The current AOII Phi Upsilon chapter house page identifies 242 S Grant St.",
        "The modeled asset is the parcel-aligned OSM way 970455277, rather than the unrelated Purdue GIS FID 756 crosswalk.",
        "Independent transform of the saved OSM WGS84 way ring to the project local XY gives 276.230285 m2; the fresh-open model slab ring is 276.230318 m2, with symmetric vertex Hausdorff distance 0.000018 m."
      ],
      "findings": ["Identity/parcel match is well supported; OSM is a footprint source, not a surveyed as-built plan."]
    },
    {
      "name": "Position, orientation, and scale/dimensions",
      "score": 1.8,
      "max_score": 2.0,
      "evidence": [
        "The asset retains project origin metadata at (308.7021, -719.9723, 0) m and its structural footprint matches the transformed source ring within 0.000018 m.",
        "The saved OSM ring is the source for orientation and plan dimensions; no rescaling was detected in the structural slab."
      ],
      "findings": ["Master placement-marker placement has not yet been independently verified because root integration is still pending."]
    },
    {
      "name": "Evidence-backed height, floors, and roof form",
      "score": 1.1,
      "max_score": 2.0,
      "evidence": [
        "West Lafayette APC 2015 report Z-2618 describes two residential stories over a ground-level parking lot, or three functional levels; the model has a garage/ground level plus two upper levels.",
        "Model levels at approximately 0, 3.1, 6.2, and 9.15 m and total height 9.25 m are estimates, not measured elevations.",
        "The 2015 report describes an open second-level terrace; the model includes a recessed terrace."
      ],
      "findings": [
        "No measured elevations or as-built roof plans were found.",
        "Model uses a broad flat roof with material named dark asphalt shingles; current Street View shows a low-pitched roofline. Roof silhouette/material need source-backed correction or reconciliation."
      ]
    },
    {
      "name": "Facade, entrances, and distinctive architecture/interior",
      "score": 1.0,
      "max_score": 2.0,
      "evidence": [
        "The model contains red-brown brick walls, windows with trim, an entry, an at-grade parking level, terrace, planter walls, and representative interior spaces including 15 bedroom bays and shared kitchen/lounge/study furniture.",
        "The City report supports 15 bedrooms, parking at grade, a terrace, planter walls, street trees, and greenscreen trellises; the official AOII page describes shared living, study, kitchen/dining and patio spaces."
      ],
      "findings": [
        "Direct visual comparison with the March 2026 Google Street View panorama nearest the 242 S Grant parcel shows beige horizontal lap siding on the upper floors, a brick lower/base level, dark window shutters, and a low-pitched roof. The model instead shows two fully red-brick upper floors, lacks the visible dark shutters, and uses a flat roof. This is a material facade/roof mismatch.",
        "Interior arrangement is plausible and contains the reported bedroom count, but exact room partitions, furniture placement, garage stalls, and facade schedule are not supported by measured drawings."
      ]
    },
    {
      "name": "Modular export, portability, and complete evidence",
      "score": 1.7,
      "max_score": 2.0,
      "evidence": [
        "Fresh-opened in Blender 5.2.3 LTS: expected scene and Asset_massing_house_970455277_a3fb72a collection are present; all 614 collection objects are nonempty meshes.",
        "The 12 used materials have Principled BSDF nodes; there are no external image dependencies and no linked objects.",
        "The asset ID, file path, scene name, and collection name remain stable; geometry is recentered into local coordinates with origin metadata."
      ],
      "findings": ["The manifest and master still require coordinator updates for the local-coordinate placement and identity crosswalk before final integration."]
    }
  ],
  "evidence": {
    "fresh_open_probe": "fresh_open_probe.json",
    "footprint_comparison": "footprint_comparison.json",
    "visual_previews": ["../preview_front_west.png", "../preview_entry_isometric.png", "../preview_terrace_aerial.png"],
    "primary_sources": [
      "https://purdue.alphaomicronpi.org/house",
      "https://www.tippecanoe.in.gov/AgendaCenter/ViewFile/Item/198?fileID=184",
      "https://lambertconstructionco.com/project-portfolio/alpha-omicron-pi-sorority/",
      "https://www.openstreetmap.org/way/970455277",
      "https://www.google.com/maps/@40.4209197,-86.9103025,185a,90y,0t/data=!3m7!1e1!3m5!1s7sss79LqLjoubGgmBPYxng!2e0!6shttps:%2F%2Fstreetviewpixels-pa.clients6.google.com%2Fv1%2Fthumbnail%3Fcb_client%3Dmaps_sv.tactile%26w%3D900%26h%3D600%26pitch%3D0%26panoid%3D7sss79LqLjoubGgmBPYxng%26yaw%3D0!7i16384!8i8192"
    ],
    "street_view_capture": "March 2026; panorama 7sss79LqLjoubGgmBPYxng, viewpoint about 21 m west of the candidate footprint"
  },
  "findings": [
    "Revise upper-floor facade material/profile and window shutters to match the nearest current street-level evidence; verify that the panorama is indeed the 242 S Grant facade before locking the change.",
    "Replace or substantiate the flat roof and asphalt-shingle material against street imagery or better as-built evidence.",
    "After the builder revises, perform a fresh independent review and require at least 8/10 before the root integrates the model."
  ]
}

def evaluate():
  assert round(sum(c['score'] for c in RESULT['criteria']), 1) == RESULT['score']
  assert RESULT['score'] < RESULT['threshold']
  return RESULT

if __name__ == '__main__':
  out=Path(__file__).with_name('result.json')
  out.write_text(json.dumps(evaluate(), indent=2), encoding='utf-8')
  print(json.dumps(evaluate(), indent=2))

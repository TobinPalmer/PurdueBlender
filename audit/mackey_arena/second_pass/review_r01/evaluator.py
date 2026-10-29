"""Independent second-pass visual evaluator — Mackey Arena, revision r1.

Run:  python evaluator.py            (from any directory; writes result.json next to this file)

Each criterion's points are assessed independently by the reviewer from direct inspection of the
source photos/aerial and reviewer-generated renders of the saved asset (hash re-verified below).
The script only (a) re-hashes the asset, (b) sums the independently assessed criterion awards
(max minus itemised deductions), (c) records gates, and (d) compares the UNROUNDED total with the
threshold. It never edits or saves the asset.
"""
import hashlib, json, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ASSET_REL = "modular/buildings/mackey_arena.blend"
EXPECTED_SHA = "0ee720103158d666f345f21adfc96aa6ef1f75cd1f6dde6617ff645edee31151"
SP = "audit/mackey_arena/second_pass/"
RV = SP + "review_r01/"

sha = hashlib.sha256(open(os.path.join(REPO, ASSET_REL), "rb").read()).hexdigest()
if sha != EXPECTED_SHA:
    raise SystemExit(f"asset hash {sha} != expected {EXPECTED_SHA}; review not applicable")

colors = json.load(open(os.path.join(HERE, "color_compare.json")))


def C(maxp, awarded_items, deductions, citations):
    ded = round(sum(d["points"] for d in deductions), 4)
    awarded = round(maxp - ded, 4)
    return {"max": maxp, "awarded": awarded, "deducted": ded, "supported_strengths": awarded_items,
            "citations": citations, "deductions": deductions}


criteria = {
    "windows_openings": C(3.0, [
        "Drum: 24 pilaster bays with slot groups in a 2-slotted:1-plain rhythm on S/SW matches Mackey_Arena_Purdue_University_2016_02.jpg and exponent_drone_2025_04.jpg (renders/rv_match_2016_02_SW_ground.png, renders/rv_match_drone04_SW.png).",
        "SW entrance: recessed glazed door banks between brick piers under soffit, consistent with 2016_02 (r1/r1_close_SW_entrance.png).",
        "Wing: punched windows between limestone bands, storefront at ground on the plaza side, four glazed tower/penthouse volumes (r1/r1_elev_E.png).",
    ], [
        {"points": 0.35, "feature": "Drum slot groups (all bays)", "issue": "Modelled as dark glazed slits with aluminium frames spanning z 7.2-16.3 m (~80% of drum height). Photos show light grey louvre panels occupying only the lower ~55-65% of each slotted bay, under full-height recessed vertical brick channels.",
         "source": ["sources/Mackey_Arena_Purdue_University_2016_02.jpg", "crops/2016_02_drum_crop.png", "crops/drone04_drum_crop.png"], "model_view": ["renders2/rv_drum_louver_close.png", "comparisons/cmp_drum_louvers.jpg"]},
        {"points": 0.30, "feature": "SE wing east face (Northwestern Ave, south of east entrance)", "issue": "Model: evenly spaced wide 2-light ground windows and single/pair upper windows, no corner bay. Source: glazed 3-light corner bay with grey metal surround on both floors at the SE tip, then a group of 4 narrow slit windows on each floor aligned vertically, then a recessed ground-floor arcade under a projecting second-floor canopy with storefront behind piers.",
         "source": ["sources/Mackey_Arena_Purdue_University_2016_01.jpg", "crops/2016_01_SEwing_crop.png"], "model_view": ["renders/rv_match_2016_01_SE_ground.png", "r1/r1_close_SE_block.png", "comparisons/cmp_SE_ground_2016_01.jpg"]},
        {"points": 0.30, "feature": "East wing between 2nd and 3rd P towers and north of 3rd P tower", "issue": "Model shows three window tiers over much of this length; drone photo shows two tiers: recessed storefront arcade between brick piers with limestone bases at ground, one row of paired/single upper windows with limestone heads/sills, then a blank banded parapet zone.",
         "source": ["sources/exponent_drone_2025_05.jpg", "crops/drone05_east_wing_north_crop.png"], "model_view": ["renders2/rv_east_north_end.png", "r1/r1_elev_E.png", "comparisons/cmp_east_wing_tiers.jpg"]},
        {"points": 0.25, "feature": "SDAC west (Weist Plaza) facade", "issue": "Model has storefront plus TWO separate rows of punched upper windows; HNTB photo shows storefront plus ONE tier of tall upper windows (single wide gridded units and narrow pairs) under a banded parapet.",
         "source": ["sources/hntb_Purdue-2.jpg"], "model_view": ["renders2/rv_hntb2_plaza_b.png", "renders2/rv_sdac_lobby.png", "comparisons/cmp_plaza_hntb2.jpg"]},
        {"points": 0.10, "feature": "Arena north entrance (Weist Plaza)", "issue": "Modelled as a 2-row grid of small dark panes; source shows full-height storefront entrance with MACKEY ARENA letters above. Evidence is distant/dusk.",
         "source": ["sources/hntb_Purdue-2.jpg"], "model_view": ["renders2/rv_hntb2_plaza_b.png", "renders2/rv_obl_N_high.png"]},
        {"points": 0.10, "feature": "Glass P towers", "issue": "Uniform full-height glass with P; source towers have the P on a grey horizontal-louvre metal band with glazing above/below and storefront at the base.",
         "source": ["sources/exponent_drone_2025_05.jpg", "crops/drone05_east_entrance_crop.png"], "model_view": ["renders/rv_match_drone05_E.png", "renders2/rv_east_north_end.png"]},
        {"points": 0.30, "feature": "Coverage", "issue": "No daylight source for the north elevation/rounded north end, north half of the east facade, west annex facades, or drum north/east bays; their openings are rhythm-assumed and cannot be verified.",
         "source": ["coverage_matrix.md", "reference_index.json"], "model_view": ["renders2/rv_obl_N_high.png", "renders2/rv_west_annex_wide.png", "r1/r1_elev_N.png"]},
    ], ["sources/Mackey_Arena_Purdue_University_2016_02.jpg", "sources/Mackey_Arena_Purdue_University_2016_01.jpg",
        "sources/exponent_drone_2025_04.jpg", "sources/exponent_drone_2025_05.jpg", "sources/hntb_Purdue-2.jpg"]),

    "signature_architecture": C(2.5, [
        "Ribbed copper-tan dome with concentric seam rings and small central cap (sources/mackey_ortho_2023_hr.jpg vs renders/rv_top_overlay_blend.png).",
        "Flared bronze fascia band, 24 limestone pilasters, drum base course (2016_02 vs rv_match_2016_02_SW_ground.png).",
        "SW (Morgan & Kate Burke) entrance with soffit, piers and two-line lettering (2016_02, drone_04 vs r1_close_SW_entrance.png).",
        "East entrance recess with MACKEY ARENA / HOME OF PURDUE BASKETBALL banner, 44 and 59 banners, flanking glass P towers (drone_05 vs rv_match_drone05_E.png).",
        "Concourse ring with water table, two limestone stripes and coping; south block; west annex; four penthouses (ortho, 2016_02).",
    ], [
        {"points": 0.30, "feature": "East entrance bay", "issue": "Source entrance front above the 3-bay portal is CURVED (banner wall in 2025; curved two-storey glass bay in 2016) with large separate 44 and 59 banners on projecting piers and vertical blade banners (MACKEY ARENA / KEADY COURT); model is a flat wall with small side panels and no blade banners.",
         "source": ["sources/exponent_drone_2025_05.jpg", "crops/drone05_east_entrance_crop.png", "crops/2016_01_SEwing_crop.png"], "model_view": ["renders/rv_match_drone05_E.png", "r1/r1_close_east_entrance.png", "comparisons/cmp_E_drone05.jpg"]},
        {"points": 0.25, "feature": "SDAC curved glass lobby (SW corner of SDAC, facing Weist Plaza)", "issue": "Source: prominent convex two-storey curtain-wall lobby with metal fascia. Model: flat dark two-level glazing band set in the brick wall; no curvature.",
         "source": ["sources/hntb_Purdue-2.jpg"], "model_view": ["renders2/rv_sdac_lobby.png", "renders2/rv_hntb2_plaza_b.png"]},
        {"points": 0.10, "feature": "Dome fascia finish", "issue": "Source fascia is a vertically corrugated/ribbed metal band; model is smooth with two reveal lines.",
         "source": ["crops/2016_02_drum_crop.png", "crops/2016_01_drum_SE_crop.png"], "model_view": ["renders/rv_match_2016_02_SW_ground.png"]},
        {"points": 0.10, "feature": "Drum bay articulation", "issue": "Full-height recessed vertical brick channels in slotted bays (visible above the louvres) are missing.",
         "source": ["crops/2016_02_drum_crop.png", "crops/2016_01_drum_SE_crop.png"], "model_view": ["renders2/rv_drum_louver_close.png"]},
        {"points": 0.10, "feature": "P towers / penthouses", "issue": "Composition simplified (no louvre band behind P, no metal-panel penthouse cladding pattern).",
         "source": ["crops/drone05_east_entrance_crop.png", "crops/drone05_east_wing_north_crop.png"], "model_view": ["renders2/rv_east_north_end.png"]},
        {"points": 0.15, "feature": "SE wing details", "issue": "Missing glazed corner bay with metal surround, projecting second-floor canopy over recessed ground-floor arcade, and limestone accent inlays in the attic band.",
         "source": ["crops/2016_01_SEwing_crop.png"], "model_view": ["r1/r1_close_SE_block.png", "renders/rv_match_2016_01_SE_ground.png"]},
        {"points": 0.10, "feature": "North entrance / plaza features", "issue": "No MACKEY ARENA lettering on north entrance; Pyramid of Success and Wooden statue are crude blocks at estimated positions.",
         "source": ["sources/hntb_Purdue-2.jpg"], "model_view": ["renders2/rv_sdac_lobby.png", "renders2/rv_obl_N_high.png"]},
        {"points": 0.10, "feature": "Coverage", "issue": "North rounded end, north half of east facade and west annex details unseen in daylight sources; cannot be credited as verified.",
         "source": ["coverage_matrix.md"], "model_view": ["renders2/rv_obl_N_high.png", "renders2/rv_west_annex_wide.png"]},
    ], ["sources/mackey_ortho_2023_hr.jpg", "sources/Mackey_Arena_Purdue_University_2016_02.jpg", "sources/exponent_drone_2025_05.jpg", "sources/hntb_Purdue-2.jpg"]),

    "proportions_roof_silhouette": C(2.0, [
        "Footprint/plan: reviewer top render registered to the 2023 orthophoto local box aligns closely for drum, wing outline (incl. rounded north end and west concave curve), penthouses, west annex and south block (renders/rv_top_overlay_blend.png).",
        "Shallow ribbed dome form and continuous east/north wing massing (ortho, drone_01/05).",
    ], [
        {"points": 0.50, "feature": "Drum height vs concourse ring / dome crown", "issue": "Visible drum (concourse roof to fascia underside) : concourse wall height is ~1.2 in drone_04 and ~0.8 from the ground in 2016_02, versus ~2.1 and ~1.6 in matched model renders. Drum height : 15-degree bay chord is ~0.79 in 2016_02 / ~0.80 in drone_04 vs ~0.96 in the model. From the 2016_02 ground position the dome crown shows clearly above the fascia; in the matched model view it is hidden. Drum is too tall and/or the concourse ring too low; re-derive drum/concourse/fascia/dome heights.",
         "source": ["sources/Mackey_Arena_Purdue_University_2016_02.jpg", "sources/exponent_drone_2025_04.jpg", "crops/2016_02_drum_crop.png", "crops/drone04_drum_crop.png"], "model_view": ["renders/rv_match_2016_02_SW_ground.png", "renders/rv_match_drone04_SW.png", "comparisons/cmp_SW_ground_2016_02.jpg", "comparisons/cmp_SW_drone04.jpg"]},
        {"points": 0.10, "feature": "Heights", "issue": "All heights (ring 5.8, drum top 17.4, apex 27.9, wing 14.0 m) are photo estimates with no measured datum.",
         "source": ["change_log.md"], "model_view": ["r1/r1_elev_S.png", "r1/r1_elev_E.png"]},
        {"points": 0.15, "feature": "North side massing", "issue": "North lobby/concourse between drum and Brees Center and the rounded north end are seen only in plan (ortho) or distant dusk photo; elevation massing unverified.",
         "source": ["sources/mackey_ortho_2023_hr.jpg", "sources/hntb_Purdue-2.jpg"], "model_view": ["renders2/rv_obl_N_high.png"]},
        {"points": 0.05, "feature": "Curved elements in silhouette", "issue": "Curved east-entrance front and curved SDAC lobby are flat/faceted in silhouette.",
         "source": ["sources/exponent_drone_2025_05.jpg", "sources/hntb_Purdue-2.jpg"], "model_view": ["renders/rv_match_drone05_E.png", "renders2/rv_sdac_lobby.png"]},
    ], ["sources/mackey_ortho_2023_hr.jpg", "sources/exponent_drone_2025_04.jpg", "sources/Mackey_Arena_Purdue_University_2016_02.jpg"]),

    "material_color_surface_depth": C(1.5, [
        f"Drum brick render {colors['render_drumbrick_SWmatch'][0]} vs photo {colors['photo_drumbrick_2016_02'][0]} (hue 25 vs 28 deg, S .37 vs .43, V .64 vs .68): good.",
        f"Limestone pilaster render {colors['render_pilaster_SWmatch'][0]} vs photo {colors['photo_pilaster_2016_02'][0]}: good.",
        f"Wing roof white render {colors['render_wingroof_top'][0]} vs ortho {colors['photo_wingroof_ortho'][0]}: good.",
        f"Dome hue render {colors['render_dome_top'][1]} deg vs photos 18-31 deg: correct copper-tan family.",
    ], [
        {"points": 0.25, "feature": "Drum slot/louvre colour", "issue": f"Model slots render near-black blue-grey {colors['render_slot_SWmatch'][0]} (hue {colors['render_slot_SWmatch'][1]}, V {colors['render_slot_SWmatch'][3]}); photo louvres are light warm grey {colors['photo_louver_2016_02'][0]} (hue {colors['photo_louver_2016_02'][1]}, V {colors['photo_louver_2016_02'][3]}).",
         "source": ["sources/Mackey_Arena_Purdue_University_2016_02.jpg"], "model_view": ["renders/rv_match_2016_02_SW_ground.png", "renders2/rv_drum_louver_close.png"]},
        {"points": 0.10, "feature": "Fascia colour/finish", "issue": f"Render {colors['render_fascia_SWmatch'][0]} S {colors['render_fascia_SWmatch'][2]} vs photo {colors['photo_fascia_2016_02'][0]} S {colors['photo_fascia_2016_02'][2]}: model fascia is greyer/less golden; smooth instead of corrugated.",
         "source": ["sources/Mackey_Arena_Purdue_University_2016_02.jpg"], "model_view": ["renders/rv_match_2016_02_SW_ground.png"]},
        {"points": 0.05, "feature": "Dome value", "issue": f"Render {colors['render_dome_drone05match'][0]} V {colors['render_dome_drone05match'][3]} vs sunlit photo {colors['photo_dome_2016_02'][0]} V {colors['photo_dome_2016_02'][3]} and overcast {colors['photo_dome_drone05'][0]} V {colors['photo_dome_drone05'][3]}: dome reads somewhat dark/grey.",
         "source": ["sources/Mackey_Arena_Purdue_University_2016_02.jpg", "sources/exponent_drone_2025_05.jpg"], "model_view": ["renders/rv_match_drone05_E.png", "renders/rv_match_drone04_SW.png"]},
        {"points": 0.05, "feature": "Concourse ring roof", "issue": f"Render {colors['render_ringroof_top'][0]} V {colors['render_ringroof_top'][3]} vs ortho {colors['photo_ringroof_ortho'][0]} V {colors['photo_ringroof_ortho'][3]}: too dark.",
         "source": ["sources/mackey_ortho_2023_hr.jpg"], "model_view": ["renders/rv_top_ortho_overlay.png"]},
        {"points": 0.05, "feature": "Low/wing brick value", "issue": f"Concourse brick render {colors['render_lowbrick_SWmatch'][0]} vs photo {colors['photo_lowbrick_2016_02'][0]}; wing brick render {colors['render_wingbrick_SEmatch'][0]} vs sunlit 2016_01 {colors['photo_wingbrick_2016_01'][0]}: hue right, value low (partly lighting).",
         "source": ["sources/Mackey_Arena_Purdue_University_2016_02.jpg", "sources/Mackey_Arena_Purdue_University_2016_01.jpg"], "model_view": ["renders/rv_match_2016_02_SW_ground.png", "renders/rv_match_2016_01_SE_ground.png"]},
        {"points": 0.15, "feature": "Facade depth", "issue": "Missing recessed ground-floor arcades/canopy on the east wing and SE wing, louvre-in-channel depth on the drum, curved glass depth.",
         "source": ["crops/2016_01_SEwing_crop.png", "crops/drone05_east_wing_north_crop.png"], "model_view": ["renders2/rv_east_north_end.png", "r1/r1_close_SE_block.png"]},
        {"points": 0.05, "feature": "P-tower materials", "issue": "Blue-grey glass panel instead of grey metal louvre band plus greenish glazing.",
         "source": ["crops/drone05_east_entrance_crop.png"], "model_view": ["renders/rv_match_drone05_E.png"]},
    ], ["sources/color_samples.json", "review_r01/color_compare.json"]),

    "whole_building_consistency": C(1.0, [
        "SW obliques (2016_02, drone_04) and top view read as Mackey Arena; dome/fascia/pilaster vocabulary consistent around the drum.",
    ], [
        {"points": 0.15, "feature": "SW matched views", "issue": "Drum proportion and louvre colour differ visibly at matched SW ground and drone views.",
         "source": ["sources/Mackey_Arena_Purdue_University_2016_02.jpg", "sources/exponent_drone_2025_04.jpg"], "model_view": ["comparisons/cmp_SW_ground_2016_02.jpg", "comparisons/cmp_SW_drone04.jpg"]},
        {"points": 0.10, "feature": "SE matched view", "issue": "SE wing fenestration/corner bay/arcade differ.",
         "source": ["sources/Mackey_Arena_Purdue_University_2016_01.jpg"], "model_view": ["comparisons/cmp_SE_ground_2016_01.jpg"]},
        {"points": 0.10, "feature": "E matched view", "issue": "Flat entrance front and 3-tier fenestration vs 2 tiers in source.",
         "source": ["sources/exponent_drone_2025_05.jpg"], "model_view": ["comparisons/cmp_E_drone05.jpg"]},
        {"points": 0.05, "feature": "Plaza matched view", "issue": "Tier count and missing curved lobby.",
         "source": ["sources/hntb_Purdue-2.jpg"], "model_view": ["comparisons/cmp_plaza_hntb2.jpg"]},
        {"points": 0.10, "feature": "N / NE / NW", "issue": "No current daylight matched source for north and north-east obliques; NW source (MackeyA.jpg) is pre-renovation 2009.",
         "source": ["sources/MackeyA.jpg", "coverage_matrix.md"], "model_view": ["renders2/rv_obl_N_high.png", "r1/r1_obl_NE.png"]},
    ], ["review_r01/comparisons/"]),
}

score = round(sum(c["awarded"] for c in criteria.values()), 6)  # unrounded sum of awards (exact to 0.05 steps)

gates = {
    "correct_identity": {"pass": True, "reason": "Asset is Mackey Arena (dome/drum/SW and east entrances match Commons, Exponent and HNTB photos); reviewer top render registers to the 2023 IndianaMap orthophoto; Brees Center and Lambert Fieldhouse correctly excluded."},
    "adequate_exterior_reference_coverage": {"pass": False, "reason": "No current daylight photo of the north elevation/rounded north end, north half of the east facade, west annex facades or drum north/east bays; north source is distant dusk (hntb_Purdue-2) or pre-renovation 2009 (MackeyA). Coverage matrix itself lists these as E/U."},
    "no_unresolved_material_exterior_discrepancies": {"pass": False, "reason": "Unresolved: drum height/concourse proportion; drum slots dark glass instead of light louvres in brick channels; flat east entrance front (curved in source); SDAC curved lobby missing; 3-tier vs 2-tier fenestration on east wing and SDAC; SE wing corner bay/arcade missing."},
    "saved_file_reopen": {"pass": True, "reason": f"Reviewer opened the exact saved file headlessly in Blender 5.2.3 (reviewer_inspect.py, reviewer_render.py) without saving; SHA-256 {sha} verified before and after; 311 objects load."},
    "expected_collection_export": {"pass": True, "reason": "Single collection Asset_mackey_arena containing all 311 objects, AssetRoot_mackey_arena at origin with identity transform, scene Building_mackey_arena. Note for coordinator: modular/manifest.json object list/object_count (391) and bounds still describe r0."},
    "portable_dependencies": {"pass": True, "reason": "No linked libraries, no images, no text blocks/auto-run scripts, no external absolute paths (reviewer_inspect_output.json)."},
    "no_regression_footprint_orientation_scale": {"pass": True, "reason": "Local frame and manifest placement origin (-209.59, 671.84) unchanged; drum centre/radius retained; wing outline now matches the 2023 orthophoto better than r0 (renders/rv_top_overlay_blend.png). Local bounds x -63.9..65.5, y -73.9..139.5 m."},
}

findings = [
    {"severity": 1, "facade": "Drum (all)", "feature": "Drum/concourse/dome proportions", "correction": "Re-derive heights from matched views: visible drum ~1.2x concourse wall height (drone_04), dome crown visible above fascia from SW ground (2016_02). Lower drum top and/or raise concourse ring so drum height ≈ 0.8 of a 15° bay chord; re-check fascia depth and dome rise."},
    {"severity": 2, "facade": "Drum (all slotted bays)", "feature": "Slot groups", "correction": "Replace dark glazed slits with light warm-grey louvre panels (sRGB ≈150,146,132) confined to the lower ~55-65% of the bay, set inside full-height recessed vertical brick channels."},
    {"severity": 3, "facade": "East (Northwestern Ave)", "feature": "East entrance front", "correction": "Make the facade above the 3-bay portal follow a curve (convex arc) as in drone_05/2016_01; enlarge 44 and 59 banners as separate tall panels on projecting piers with sub-captions; add vertical MACKEY ARENA / KEADY COURT blade banners."},
    {"severity": 4, "facade": "East wing between P towers and north of 3rd P", "feature": "Window tiers", "correction": "Use two tiers (recessed ground storefront arcade between brick piers with limestone bases + one row of paired/single upper windows with limestone heads/sills) and a blank banded parapet, per drone_05."},
    {"severity": 5, "facade": "SDAC west (Weist Plaza)", "feature": "Window tiers", "correction": "Storefront + one tier of tall upper windows (wide gridded units alternating with narrow pairs) per hntb_Purdue-2; remove the extra upper row."},
    {"severity": 6, "facade": "SDAC SW corner", "feature": "Curved glass lobby", "correction": "Model the convex two-storey curtain-wall lobby with mullion grid and metal fascia band facing Weist Plaza."},
    {"severity": 7, "facade": "SE wing (south tip and east face)", "feature": "Corner bay, slit windows, arcade", "correction": "Add glazed corner bay with grey metal surround on both floors; 4 aligned narrow slits per floor; projecting second-floor canopy over recessed ground-floor arcade with storefront; limestone accent inlays in attic band."},
    {"severity": 8, "facade": "Dome fascia", "feature": "Finish and colour", "correction": "Vertically corrugated fascia; shift colour toward sampled (188,158,112) (more saturated golden bronze)."},
    {"severity": 9, "facade": "P towers", "feature": "Cladding", "correction": "P mounted on a grey horizontal-louvre metal band with glazing above/below and storefront base; penthouse metal-panel cladding."},
    {"severity": 10, "facade": "North (Weist Plaza) / north end / west annex", "feature": "Coverage + north entrance", "correction": "Obtain current daylight photos of the north elevation, rounded north end, east facade north half and west annex; add MACKEY ARENA lettering and full-height storefront at the north entrance; refine plaza monuments."},
    {"severity": 11, "facade": "Roofs / masonry", "feature": "Colour values", "correction": "Lighten concourse ring roof toward ortho (167,162,154); slightly raise dome and concourse/wing brick value toward sunlit samples while keeping hue."},
    {"severity": 12, "facade": "Coordinator", "feature": "Manifest", "correction": "After acceptance, update modular/manifest.json object list/count/bounds for the r1+ asset (coordinator-owned)."},
]

result = {
    "building_id": "mackey_arena",
    "revision": "r1",
    "asset_path": ASSET_REL,
    "asset_sha256": sha,
    "reviewer": "independent second-pass visual review agent (Claude, subagent; did not author r1)",
    "reviewed_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "score": score,
    "max_score": 10,
    "criteria": criteria,
    "evidence": {
        "sources_inspected_directly": ["sources/Mackey_Arena_Purdue_University_2016_01.jpg", "sources/Mackey_Arena_Purdue_University_2016_02.jpg",
                                       "sources/exponent_drone_2025_01.jpg", "sources/exponent_drone_2025_02.jpg", "sources/exponent_drone_2025_03.jpg",
                                       "sources/exponent_drone_2025_04.jpg", "sources/exponent_drone_2025_05.jpg", "sources/hntb_Purdue-2.jpg",
                                       "sources/MackeyA.jpg", "sources/mackey_ortho_2023_hr.jpg (+ .json transform)"],
        "not_exterior_evidence": ["sources/Mackey_Arena.jpg", "sources/Purdue_MackeyArena.jpg", "sources/hntb_Purdue-1-1.jpg", "sources/hntb_Purdue-3.jpg"],
        "reviewer_tools": ["review_r01/reviewer_inspect.py", "review_r01/reviewer_render.py", "review_r01/color_compare.json"],
        "modeler_documents_treated_as_claims": ["coverage_matrix.md", "discrepancy_checklist.md", "change_log.md", "r1/validation_r1.json"],
        "prior_findings_context": "audit/mackey_arena/INDEPENDENT_REVIEW_round3.md (first-pass rubric, 8.0/10; not used for this grade)",
    },
    "reviewed_views": {
        "reviewer_renders": sorted(["review_r01/renders/" + f for f in os.listdir(os.path.join(HERE, "renders")) if f.endswith((".png", ".jpg"))] +
                                   ["review_r01/renders2/" + f for f in os.listdir(os.path.join(HERE, "renders2")) if f.endswith(".png")]),
        "comparisons": sorted("review_r01/comparisons/" + f for f in os.listdir(os.path.join(HERE, "comparisons"))),
        "modeler_r1_renders_checked": ["r1/r1_elev_E.png", "r1/r1_obl_SW.png", "r1/r1_top.png", "r1/r1_close_SW_entrance.png",
                                       "r1/r1_close_SE_block.png", "r1/r1_close_east_entrance.png", "comparisons_r1/obl_SE_ref_before_after.jpg",
                                       "comparisons_r1/top_ref_before_after.jpg"],
    },
    "findings": findings,
    "uncertainties": [
        "Source camera positions (Commons GPS) and panorama projection of 2016_01/02 are approximate; proportion finding relies on ratios measured in several sources, not absolute heights.",
        "Colour comparisons mix sunlit 2016 photos, overcast/dusk 2025 drone shots and a 2023 orthophoto; brick/dome value differences of ~0.1 V are within lighting uncertainty and were deducted lightly.",
        "2016 vs 2025 east-entrance state: curved glass bay (2016) appears covered by curved banner wall (2025); curvature is supported by both.",
        "Whether the SDAC tall upper windows span two floors internally is unknown; the exterior shows one tier.",
        "North elevation, rounded north end, east facade north half, west annex facades and drum N/E bays remain unverified.",
    ],
    "gates": gates,
    "acceptance_threshold": 9.9,
    "threshold_approval": None,
}
result["all_gates_pass"] = all(g["pass"] for g in gates.values())
result["accepted"] = bool(score >= result["acceptance_threshold"] and result["all_gates_pass"])
json.dump(result, open(os.path.join(HERE, "result.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("score", score, "accepted", result["accepted"], {k: v["pass"] for k, v in gates.items()})

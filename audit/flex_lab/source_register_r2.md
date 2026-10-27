# Flex Lab R2 source register

Retrieved 2026-10-27. The revision retains the existing local coordinate frame, manifest collection name (`Asset_flex_lab`), and GIS-derived structural outline. The new facade opening follows the references below. Photometric fixture positions and the visualized interior remain illustrative because published interior plans were not available.

| Evidence | Provider / URL | Local evidence | Supports | Limits |
|---|---|---|---|---|
| Flex Lab project description and facade photography | Ennead Architects, https://www.ennead.com/work/purdue/ | `sources/ennead_AW06_curtainwall.jpg`, `ennead_AW07_interior.jpg`, `ennead_AW12_context.jpg`, `ennead_AW13_context.jpg`, `ennead_AW19_entry.jpg` | Exterior AW06/AW19/AW12/AW13 support curtainwall, brick-plane composition and entry; AW07 is an interior view and is used only for interior context | Published photographs, not dimensioned elevations; detailed heights and bay widths remain estimated |
| Flex Lab structural project record | CE Solutions, https://www.cesolutionsinc.com/flex-lab-1 | `sources/ce_solutions_entry.jpg` | Three stories plus basement, steel vestibule, entry canopy with a 20-foot cantilever | 20 ft canopy projection is a documented length; its other dimensions and precise attachment are modeled estimates |
| Facility identity and use | Purdue Engineering, https://engineering.purdue.edu/FlexLab | Existing downloaded source was not retained separately in this audit folder | Purdue Flex Lab identity and engineering research use | Does not establish facade measurements |
| Existing GIS-based structural shell | Purdue campus building GIS, feature FID 909; raw response retained in `audit/batch_b_buildings/flex_lab_gis_feature.json` and source metadata in `modular/manifest.json` (retrieved 2026-10-22; response EPSG:4326; project local transform is approximate) | `flex_lab_before_r2.blend`; mesh object `FLEX structural shell | GIS outline`; `shell_faces.json` | Preserved structural footprint, local frame and the stepped long-facade bay rhythm | This revision opened wall faces in the existing shell and preserved its measured coordinates; GIS source date/accuracy are unpublished, and absolute campus placement is controlled by the manifest Placement marker |

## R2 geometry edits

- Removed the opaque south GIS wall face to reveal the documented recessed glazed entrance.
- Removed 11 long-facade wall faces at existing stepped bays and replaced them with curtainwall glazing, floor spandrels, mullions and projecting fins.
- Removed overlapping curtainwall, brick-pier and canopy systems from the previous asset.
- Retained a single 6.10 m entry canopy corresponding to the documented 20 ft projection.
- Tuned the curtainwall glass mix and prepared brighter review lighting in the render script. Review lighting is evidence-only; no unsupported light fixtures were added to the saved asset.
- Preserved the existing shell vertex coordinates and matrix transform; face removals create the openings. No dimensioned elevations were available to verify exact heights or interior room layout.

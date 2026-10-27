# Pi Beta Phi (FID 774) source register

Retrieval date for live web and GIS pages: **2026-10-27**. The current asset models the main chapter house at **1012 State Street**, not the separate, much smaller FID 841 polygon that also carries a Pi Beta Phi label in Purdue GIS.

| Claim | Source and feature | Date / CRS | Method and uncertainty |
| --- | --- | --- | --- |
| FID 774 is the main Pi Beta Phi house | [Purdue BuildingShapesZip4 ArcGIS feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), FID 774; live query saved as [`purdue_arcgis_fids_774_841_wgs84.json`](sources/purdue_arcgis_fids_774_841_wgs84.json) | Retrieved 2026-10-27; query output WKID 4326; converted to the project's approximate local meters | Feature attributes say Pi Beta Phi, address “1012 State St,” abbreviation SOPBF; area 1200.9 m² in Purdue's projected service data. The polygon is an official campus-map footprint, not a certified survey. FID 841 is a distinct ~266 m² polygon labeled Pi Beta Phi / 1012 W. State St., likely an adjacent/secondary structure or duplicate map record; it is intentionally excluded from this building's model. |
| Current chapter identity | [Purdue FSCL Panhellenic chapter directory](https://www.purdue.edu/fscl/councils/pha/chapters.php), Pi Beta Phi / Indiana Delta; raw HTML snapshot saved in `sources/purdue_fscl_pha_chapters.html`; [current chapter website](https://purdue.pibetaphi.org/about), saved in `sources/pi_beta_phi_about.html` | Retrieved 2026-10-27 | FSCL links the active Purdue chapter to its Indiana Delta site. The direct legacy URL now resolves through the site's current `/about` page. The current address is independently shown by Google Maps and the current chapter newsletter. |
| Chapter uses 1012 State Street | [Spring 2026 Purdue Pi Beta Phi chapter newsletter](https://fliphtml5.com/ngqes/ugqj/The_Tiny_Arrow%3A_Pi_Beta_Phi_Purdue_Chapter_Spring_2026/); [Spring 2004 chapter newsletter](https://web.ics.purdue.edu/~piphi/spring04_history.pdf), p. 10; [Pi Beta Phi current Google Maps listing and March 2026 Street View](https://www.google.com/maps/place/Pi+Beta+Phi/@40.4241352,-86.9186216,191a,75y,342.02h,90t/data=!3m7!1e1!3m5!1sy7STh3iQONkOklWyDYT8-w!2e0!6shttps:%2F%2Fstreetviewpixels-pa.clients6.google.com%2Fv1%2Fthumbnail%3Fcb_client%3Dmaps_sv.tactile%26w%3D900%26h%3D600%26pitch%3D0%26panoid%3Dy7STh3iQONkOklWyDYT8-w%26yaw%3D342.01508!7i16384!8i8192) | Current newsletter Spring 2026; Google imagery captured March 2026 | The Google Maps listing reports 1012 W State St and the Street View image shows the brick chapter house from its south frontage. Street View viewpoint is 40.4241352, -86.9186216; pano ID `y7STh3iQONkOklWyDYT8-w`, heading 342.015°. The 2004 Purdue newsletter locates the house at the State/Russell corner and describes it as home to over 80 residents. No image bytes were copied from Google Maps. |
| Exterior materials and entry | March 2026 Google Street View above; [Pennington & Company chapter-house campaign](https://www.penningtonco.com/campaigns/pi-beta-phi-purdue-university), saved in `sources/pennington_house_campaign.html`; [Two Tulips Purdue sorority-house illustration](https://twotulips.com/products/purdue-sorority-custom-house-drawing) | Retrieved 2026-10-27 | Street View visibly supports a red-brick, two-story main elevation, white entry portico/columns and white upper cornice. The campaign describes repairs to the main entry stairs/banister, door, and pillars. The illustration supports a classical entry and symmetrical windows but is stylized, so it was not used as dimension evidence. |
| Interior room types | Pennington & Company campaign above; [Spring 2025 Purdue Pi Beta Phi newsletter](https://fliphtml5.com/ngqes/ilxb/Purdue_PBP_Spring_2025_NewsletterREV/) | Retrieved 2026-10-27; 2025 chapter newsletter | Sources mention study rooms, kitchen, cold dorm, a house director's suite, living room, lounge, alcove, library and blue bathroom. They do not provide measured room plans. The modeled room positions, counts and furniture are conceptual estimates, not measured interior data. |

## Transform and footprint comparison

The original massing source was in project campus coordinates and retained the correct broad location. Its base polygon had **0.9465 IoU**, **2.287 m symmetric Hausdorff distance**, and approximately **0.03 m centroid offset** against Purdue FID 774 after inverse-Web-Mercator conversion and the project conversion (`X=(lon+86.9137)*111412.84*cos(40.4274°)`, `Y=(lat-40.4274)*111040`). The detailed library now stores the FID 774 ring in local coordinates centered at the official polygon center:

| Value | Result |
| --- | ---: |
| Master placement origin XY | `(-429.577785, -311.880381)` m |
| Local footprint X bounds | `[-11.9515, 15.7936]` m |
| Local footprint Y bounds | `[-20.8982, 16.5197]` m |
| GIS horizontal extent | `27.744 × 37.418` m |
| Shell footprint | exact FID 774 ring in the project's approximate local-metre projection |

This is a local projection conversion, not survey-grade georeferencing. Root integration must switch the master reference to a `Placement_massing_house_301838781_891384f` marker at the listed XY and set the manifest record to detailed/local-coordinate behavior. Do not alter the placement origin to force a fit.

## Geometry changes and unresolved evidence

- Replaced the single rough massing extrude with a GIS-ring shell, procedural red brick, 698 modeled objects, window/frame rhythm, white cornice, central columned portico, entry doors/transom, address/letters, stairs and landing, flat screened roof, and a concept interior.
- The March 2026 view shows two occupied brick floors; exact story heights, foundation datum, roof construction and height remain unverified. The model uses a 7.25 m estimated brick wall and 0.72 m white parapet, with small attic openings.
- No floor plans were available. Interior partitions, room locations, bed count, and kitchen/dining/study furniture are illustrative, based on documented room types only.
- A separate small FID 841 polygon at 1012 W State Street is not included. Its relationship to the main house was not established; avoid merging it into this asset without further source-backed identity work.

Rendered inspection views: [`view_front.png`](view_front.png), [`view_three_quarter.png`](view_three_quarter.png), and [`view_interior_cutaway.png`](view_interior_cutaway.png). The interior image is a temporary cutaway render; the saved library itself keeps its outer shell visible.

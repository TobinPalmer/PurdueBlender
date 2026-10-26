# Family Express, 1812 Northwestern Ave evidence notes

Retrieved 2026-10-26. Stable project ID: `massing_family_express_a07e1fb`; asset collection and scene names remain the manifest values.

## Identity and location

- Address and business identity are corroborated by the official Family Express FAQ, which lists the Purdue store at 1812 Northwestern Avenue, West Lafayette, Indiana: https://familyexpress.zendesk.com/hc/en-us/articles/360018927412-Where-are-the-Pet-Washes-located-what-are-the-hours-offered
- Indiana Department of Health retail inspection listing includes Family Express at 1812 Northwestern Ave with coordinates 40.445427, -86.920457: https://secure.in.gov/health/food-protection/files/inspection-results-10162024.pdf
- OpenStreetMap way 374563309 identifies the retail building as Family Express, 1812 Northwestern Avenue, and `shop=convenience`: https://www.openstreetmap.org/way/374563309 . The retrieved full API snapshot, including node coordinates and edit metadata, is `sources/osm_way_374563309_2026-10-26.json`.

## Exterior reference

- Address-matched business page with its gallery: https://www.mapquest.com/us/indiana/family-express-378696207
- Specific image returned for the 1812 Northwestern Ave listing: https://a.mktgcdn.com/p/Q6dWIcLGo--LQCuVeEj1P7dUFpVXkHcROmqnBpKyuqE/2048x1362.jpg
- The photo shows a one-story red/brown brick shop with a low charcoal hip roof, broad storefront glazing and entrance doors, pale roof trim, a white fuel canopy, blue accents and black steel canopy supports. It is a location-level reference supplied by MapQuest's gallery; the exact date and photographer are not exposed in the listing.
- Family Express corporate/about page shows the broader chain's current white canopy, blue branding and food-service format: https://www.familyexpress.com/about-us . It is contextual brand evidence, not a measured elevation for this branch.
- Family Express official FAQ lists the Purdue location as a pet-wash site, but the task's target footprint identifies the retail building; no separate pet-wash geometry was added without a source-backed local footprint.

## Footprint and coordinate method

- Feature: OSM way 374563309, current as retrieved 2026-10-26; way edit timestamp in the API snapshot is 2024-01-17T03:51:07Z. The nine unique projected corners define the wall ring; its min/max extents agree with the existing master massing bounds to rounding (<0.00001 m).
- Source coordinates: EPSG:4326 latitude/longitude, ordered OSM way ring. OSM is community-mapped and is not a surveyed wall outline; its lineage/accuracy is not stated.
- Project transform from `modular/AGENTS.md`: X=(longitude+86.9137)*111412.84*cos(radians(40.4274)); Y=(latitude-40.4274)*111040.0. This is the project's local approximation, not a surveyed CRS.
- The tagged retail polygon is modeled directly in campus coordinates so the existing simple-massing master link stays at its current placement. Footprint extents: X -578.0182 to -552.4478 m; Y 1992.7016 to 2019.9286 m. The model's wall eaves are about 4.95 m and roof peak about 8.40 m, estimated from the photo; no measured elevation, story height, or roof plan was found.
- The observed image shows a fuel canopy and pumps in front of the store. Their positions and dimensions are not represented in the tagged OSM building ring; model canopy placement, column count, pump spacing, and interior arrangement are visual estimates. Treat those as unverified detail during independent review.

## Modeling / validation

The build script creates a textured brick wall shell on the source polygon, a charcoal hipped roof, retail storefront and side glazing, entry canopy/signage, fuel canopy with six dispensers, safety bollards, and a simple grocery/convenience interior visible through the storefront. Materials are procedural and do not rely on external files. Exports remain in `Asset_massing_family_express_a07e1fb`; the master-positioning contract is unchanged.

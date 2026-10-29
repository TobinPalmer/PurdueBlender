# Exterior research, before model building

User-directed research-only phase, 2026-10-28. There are 231 not-yet-second-passed buildings in the revised queue. Research proceeds in ascending new rank. No model, builder, placement or master asset is edited by this phase.

The [root queue](../../README.md#second-pass-exterior-ranking) is the order authority. Modeling owners are preserved by stable asset IDs; research authorization covers all rows. [Prior work](prior_work.md) and [the previous order](previous_queue_2026-10-28.json) remain separate from unfinished research.

**Research status: 6 dossiers prepared with explicit gaps; 0 in progress; 225 queued. Next: rank 7, Electrical Engineering.** Research will create one actual building-specific document at `buildings/<stable_id>/README.md`, with source snapshots, a viewpoint/face coverage matrix, observed architectural features, material references, GIS/LiDAR metadata and unresolved gaps. Queued buildings do not receive empty reports presented as completed research.

Location now contributes **70%**, campus prominence **20%**, and existing first-pass score shortfall **10%**. WALC/Centennial Mall and Purdue Mall are the primary planning focal points, with Memorial Mall a secondary core. This deliberately brings central academic buildings ahead of distant athletics and peripheral facilities. These weights are project planning judgments, not measured pedestrian traffic or a new visual grade.

Locations use identifiable Purdue GIS footprint centroids where matched; unresolved rows use explicitly labeled manifest proxies. Conflicting positions use the less-central interpretation until researched, except the football performance complex whose official KFPC footprint/address clearly contradicts the near-origin model placement. The audit data preserves both positions. Distances are approximate straight-line project metres, not walking routes. The duplicated Beering MODEL is excluded as before; official GIS FID251 remains the valid Beering location reference.

`priority = 70 × centrality + 20 × (importance−1)/4 + 10 × clamp((9.9−first_pass_grade)/1.9,0,1)`

For each focal point, centrality stays at its cap within 100 m, then decreases linearly to zero at 1100 m. Use the greatest resulting value across the three focal points. WALC/Purdue Mall caps are 1.0; Memorial Mall cap is 0.9. Exact planning coordinates, calculations, source matches, unknowns and conflicts are retained in [queue data](queue.json) and [location evidence](shared/official_location_matches.json). Sort by unrounded priority descending, centrality descending, importance descending, first-pass grade ascending, then name/path. Display rounding never changes the order.

| Rank | Building | Research document | Status |
| ---: | --- | --- | --- |
| 1 | Walc | [Research](buildings/walc/README.md) | Prepared with gaps |
| 2 | Mechanical Engineering | [Research](buildings/mechanical_engineering/README.md) | Prepared with gaps |
| 3 | Bell Tower | [Research](buildings/bell_tower/README.md) | Prepared with gaps |
| 4 | R. B. Wetherill Laboratory of Chemistry | [Research](buildings/wetherill_laboratory_of_chemistry/README.md) | Prepared with gaps |
| 5 | University Hall | [Research](buildings/university_hall/README.md) | Prepared with gaps |
| 6 | Hovde Hall | [Research](buildings/hovde_hall/README.md) | Prepared with gaps |
| 7 | Electrical Engineering | — | Queued |
| 8 | Potter Engineering | — | Queued |
| 9 | Stanley Coulter Hall | — | Queued |
| 10 | Lambertus Hall | — | Queued |
| 11 | Beering Hall | — | Queued |
| 12 | Materials Science and Electrical Engineering | — | Queued |
| 13 | Purdue Memorial Union | — | Queued |
| 14 | Forney Hall of Chemical Engineering | — | Queued |
| 15 | Dudley Hall | — | Queued |
| 16 | Stewart Center | — | Queued |
| 17 | Armory | — | Queued |
| 18 | Neil Armstrong Hall | — | Queued |
| 19 | Stone Hall (STON) | — | Queued |
| 20 | Knoy Hall | — | Queued |
| 21 | Hall of Data Science and AI | — | Queued |
| 22 | American Railway Building | — | Queued |
| 23 | Brown Laboratory of Chemistry | — | Queued |
| 24 | Psychological Sciences Building | — | Queued |
| 25 | Class Of 1950 | — | Queued |
| 26 | Lawson Hall | — | Queued |
| 27 | Grissom Hall | — | Queued |
| 28 | Hicks Library | — | Queued |
| 29 | Helen B. Schleman Hall | — | Queued |
| 30 | Math Sciences | — | Queued |
| 31 | Physics Building | — | Queued |
| 32 | Union Club Hotel | — | Queued |
| 33 | Hampton Hall of Civil Engineering (HAMP) | — | Queued |
| 34 | Peirce Hall | — | Queued |
| 35 | Wang Hall | — | Queued |
| 36 | Matthews Hall (MTHW) | — | Queued |
| 37 | Heine Pharmacy | — | Queued |
| 38 | Agricultural Administration Building | — | Queued |
| 39 | University Lutheran Church | — | Queued |
| 40 | Yue-Kong Pao Hall | — | Queued |
| 41 | Marriott Hall | — | Queued |
| 42 | Purdue Graduate Student Center | — | Queued |
| 43 | Student Health Center (PUSH) | — | Queued |
| 44 | Ralph & Bettye Bailey Hall (BALY) | — | Queued |
| 45 | Krannert Building | — | Queued |
| 46 | Triangle | — | Queued |
| 47 | St. Thomas Aquinas Center | — | Queued |
| 48 | Native American Educational and Cultural Center | — | Queued |
| 49 | Pi Kappa Phi (Omega) | — | Queued |
| 50 | Johnson Hall of Nursing (JNSN) | — | Queued |
| 51 | Delta Tau Delta | — | Queued |
| 52 | University Church | — | Queued |
| 53 | Shoemaker Cooperative | — | Queued |
| 54 | Zeta Tau Alpha | — | Queued |
| 55 | Phi Delta Theta | — | Queued |
| 56 | Purdue Lutheran Ministry | — | Queued |
| 57 | Delta Sigma Phi | — | Queued |
| 58 | The Church of Jesus Christ of Latter-day Saints Institute of Religion | — | Queued |
| 59 | Lilly Hall of Life Sciences | — | Queued |
| 60 | Twin Pines Cooperative | — | Queued |
| 61 | Hillel | — | Queued |
| 62 | Kappa Delta | — | Queued |
| 63 | Telecommunications Building (TEL) | — | Queued |
| 64 | Glenwood Cooperative | — | Queued |
| 65 | Hansen Life Sciences | — | Queued |
| 66 | The Moosehead Lounge | — | Queued |
| 67 | Hawkins Hall | — | Queued |
| 68 | University Book Store | — | Queued |
| 69 | Alpha Xi Delta | — | Queued |
| 70 | Smith Hall | — | Queued |
| 71 | Asian American and Asian Resource and Cultural Center | — | Queued |
| 72 | Kappa Sigma | — | Queued |
| 73 | Cary Quadrangle East (CQE) | — | Queued |
| 74 | Alpha Kappa Lambda | — | Queued |
| 75 | Chi Omega | — | Queued |
| 76 | Delta Gamma | — | Queued |
| 77 | Mackey Arena | — | Queued |
| 78 | Roy L. Whistler Hall of Agricultural Research (WSLR) | — | Queued |
| 79 | University Street Parking Garage | — | Queued |
| 80 | Agricultural and Biological Engineering | — | Queued |
| 81 | Marc and Sharon Hagle Hall (HAGL) | — | Queued |
| 82 | Biochemistry Building | — | Queued |
| 83 | Alpha Gamma Rho | — | Queued |
| 84 | Bechtel Innovation Design Center | — | Queued |
| 85 | Phi Mu | — | Queued |
| 86 | Sigma Pi | — | Queued |
| 87 | Islamic Society of Greater Lafayette (ISGL) | — | Queued |
| 88 | Rawls Hall | — | Queued |
| 89 | Grant Street Parking Garage (PGG) | — | Queued |
| 90 | Beta Sigma Psi | — | Queued |
| 91 | Black Cultural Center | — | Queued |
| 92 | Kappa Kappa Gamma | — | Queued |
| 93 | Ward L. Lambert Fieldhouse and Gymnasium | — | Queued |
| 94 | Honors College and Residences South | — | Queued |
| 95 | Baptist Student Foundation | — | Queued |
| 96 | Honors College and Residences North | — | Queued |
| 97 | Cary Quadrangle South (CQS) | — | Queued |
| 98 | Acacia | — | Queued |
| 99 | Pi Beta Phi | — | Queued |
| 100 | Our Saviour Lutheran Church | — | Queued |
| 101 | McDonald's | — | Queued |
| 102 | Windsor Halls | — | Queued |
| 103 | Frieda Parker Hall | — | Queued |
| 104 | Alpha Tau Omega | — | Queued |
| 105 | Horticulture Building | — | Queued |
| 106 | Life Science Plant and Soils Laboratory | — | Queued |
| 107 | Alpha Chi Rho | — | Queued |
| 108 | Pi Kappa Alpha (Pike) | — | Queued |
| 109 | FarmHouse Fraternity, Purdue Chapter | — | Queued |
| 110 | Winifred Parker Hall | — | Queued |
| 111 | Lyles-Porter Hall | — | Queued |
| 112 | Sigma Phi Epsilon | — | Queued |
| 113 | Ernest C. Young Hall (YONG) | — | Queued |
| 114 | Dauch Alumni Center | — | Queued |
| 115 | Philip E. Nelson Hall of Food Science (NLSN) | — | Queued |
| 116 | MRI Modular Facility (MRI1 / PMRI) | — | Queued |
| 117 | Sigma Kappa | — | Queued |
| 118 | Delta Chi | — | Queued |
| 119 | Wiley Dining Court (WDCT) | — | Queued |
| 120 | Life Science Ranges Greenhouse & Service Building (LSR) | — | Queued |
| 121 | FUSE | — | Queued |
| 122 | Cary Quadrangle West (CQW) | — | Queued |
| 123 | Wiley Hall | — | Queued |
| 124 | Von’s Shops | — | Queued |
| 125 | Hi Vine | — | Queued |
| 126 | Kappa Alpha Theta | — | Queued |
| 127 | Phi Gamma Delta | — | Queued |
| 128 | Krach Leadership Center | — | Queued |
| 129 | Frances M. Shealy Residence Hall | — | Queued |
| 130 | Tarkington Hall | — | Queued |
| 131 | Latino Cultural Center (current, FID 925) | — | Queued |
| 132 | Purdue Drug Discovery Facility | — | Queued |
| 133 | Duhme (Ophelia) Residence Hall | — | Queued |
| 134 | Martin C. Jischke Hall of Biomedical Engineering | — | Queued |
| 135 | France A. Córdova Recreational Sports Center | — | Queued |
| 136 | Henni's Hair Shop | — | Queued |
| 137 | Maclure Cooperative | — | Queued |
| 138 | Ray W. Herrick Laboratories | — | Queued |
| 139 | Stewart Cooperative House | — | Queued |
| 140 | Ross Ade | — | Queued |
| 141 | Jimmy John's | — | Queued |
| 142 | Veterinary Pathology Building | — | Queued |
| 143 | Creighton Hall of Animal Sciences | — | Queued |
| 144 | Wood Street Parking Garage | — | Queued |
| 145 | Campus Edge | — | Queued |
| 146 | Herrick Laboratories (HERL) | — | Queued |
| 147 | Harrison Street Parking Garage | — | Queued |
| 148 | National Soil Erosion Laboratory | — | Queued |
| 149 | Owen Hall | — | Queued |
| 150 | Chauncey Cooperative | — | Queued |
| 151 | Slayter Center for Performing Arts | — | Queued |
| 152 | Hanley Hall | — | Queued |
| 153 | Hockmeyer Hall of Structural Biology (HOCK) | — | Queued |
| 154 | Drew and Brittany Brees Student Athletic Academic Center | — | Queued |
| 155 | Veterinary Animal Isolation Building 2 (VA2) | — | Queued |
| 156 | Mann Hall | — | Queued |
| 157 | Burton D. Morgan Center for Entrepreneurship | — | Queued |
| 158 | Unitarian Universalist Church of Tippecanoe County | — | Queued |
| 159 | Purdue Police Department (TERY) | — | Queued |
| 160 | Morgan J. Burke Boilermaker Aquatic Center | — | Queued |
| 161 | Animal Holding Facility | — | Queued |
| 162 | Smalley Center | — | Queued |
| 163 | First Street Towers, East (FSTE) | — | Queued |
| 164 | Virginia C. Meredith Residence Hall | — | Queued |
| 165 | Earhart Hall | — | Queued |
| 166 | Birck Nanotechnology Center | — | Queued |
| 167 | Turf Recreation Exercise Center (TREC) | — | Queued |
| 168 | Animal Disease Diagnostic Laboratory | — | Queued |
| 169 | Shreve Hall | — | Queued |
| 170 | Veterinary Medicine Isolation Facility | — | Queued |
| 171 | Gemini Cooperative | — | Queued |
| 172 | Bindley Bioscience Center | — | Queued |
| 173 | Purdue Fire Department | — | Queued |
| 174 | First Street Towers, Central (FSTC) | — | Queued |
| 175 | David and Bonnie Brunner Farm Animal Hospital | — | Queued |
| 176 | Sigma Chi | — | Queued |
| 177 | Marwood Cooperative | — | Queued |
| 178 | Beta Theta Pi | — | Queued |
| 179 | Purdue Football Performance Complex (Kozuch Football Performance Center) | — | Queued |
| 180 | Flex Lab | — | Queued |
| 181 | Bob & Trudy Hull “All-American” Marching Band Complex | — | Queued |
| 182 | Phi Kappa Sigma | — | Queued |
| 183 | West Lafayette Junior-Senior High School | — | Queued |
| 184 | Utility Plant Office Facility | — | Queued |
| 185 | Hillenbrand Hall | — | Queued |
| 186 | Sigma Alpha Epsilon | — | Queued |
| 187 | Kappa Delta Rho | — | Queued |
| 188 | First Street Towers, West (FSTW) | — | Queued |
| 189 | Purdue Village Administration Building | — | Queued |
| 190 | Mccutcheon Hall | — | Queued |
| 191 | South Hall | — | Queued |
| 192 | SAMARA (John and Catherine Christian House) | — | Queued |
| 193 | Benjamin Harrison Hall | — | Queued |
| 194 | Delta Delta Delta | — | Queued |
| 195 | Delta Zeta | — | Queued |
| 196 | Faith West Community Center | — | Queued |
| 197 | Niswonger Aviation Tech | — | Queued |
| 198 | Redeemer Lutheran Church | — | Queued |
| 199 | Sigma Nu | — | Queued |
| 200 | Alpha Phi | — | Queued |
| 201 | 3rd and West | — | Queued |
| 202 | Alpha Chi Omega | — | Queued |
| 203 | Alpha Gamma Delta | — | Queued |
| 204 | Chi Psi | — | Queued |
| 205 | Crosswalk Commons | — | Queued |
| 206 | Fairway Cooperative | — | Queued |
| 207 | Northwest Chiller Plant | — | Queued |
| 208 | Convergence Center for Innovation and Collaboration | — | Queued |
| 209 | Alpha Sigma Phi | — | Queued |
| 210 | Alpha Epsilon Pi | — | Queued |
| 211 | Circle Pines | — | Queued |
| 212 | Gamma Phi Beta | — | Queued |
| 213 | Phi Kappa Tau | — | Queued |
| 214 | Alpha Omicron Pi | — | Queued |
| 215 | Delta Upsilon | — | Queued |
| 216 | Evans Scholars House | — | Queued |
| 217 | Pete Dye Clubhouse | — | Queued |
| 218 | Phi Kappa Psi / Indiana Delta | — | Queued |
| 219 | Purdue Center for Regional Development (Schowe House) | — | Queued |
| 220 | Theta Chi | — | Queued |
| 221 | Zeta Beta Tau | — | Queued |
| 222 | Purdue University Daniel Turf Center | — | Queued |
| 223 | Joyful Journeys | — | Queued |
| 224 | Zundo Family Dentistry | — | Queued |
| 225 | Riverside Covenant Church | — | Queued |
| 226 | The Caretaker’s Cottage | — | Queued |
| 227 | Provenance Apartments 005 | — | Queued |
| 228 | Family Express | — | Queued |
| 229 | West Lafayette Intermediate School | — | Queued |
| 230 | Village Bottle Shoppe | — | Queued |
| 231 | Horizon Bank | — | Queued |

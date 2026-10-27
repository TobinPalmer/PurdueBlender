# Zeta Psi / Chi Psi occupancy recheck — third pass


> **Correction note — 2026-10-27:** Earlier wording in this audit incorrectly attributed a 2022 house move to Tau Gamma. The official May 15, 2023 *Zeta Psi Circle* report lists Tau Gamma / Purdue with “Chapter update not available at press time”; the adjacent “This year we moved our chapter house” paragraph is for Tau Theta / University of Ontario Institute of Technology. Source: `sources/zetapsi_tau_gamma_2023_chapter_report.pdf`, printed p. 9 (PDF page 10); see also `occupancy_recheck_2026-10-27_addendum10.md`. This note records the prior misreading for provenance; it must not be used as evidence.

**Review date:** 2026-10-26 (America/Indiana/Indianapolis)  
**Question:** Does current public evidence resolve who occupies the single GIS-matched building at 950 David Ross Road (Purdue GIS FID 748)?  
**Disposition:** No. New first-party evidence confirms that Chi Psi's Purdue Alpha was classified nationally as a rental chapter for both 2024–25 and 2025–26, while the Purdue-linked Tau Gamma account currently self-lists 950 David Ross Road and Zeta Psi's housing association reported an active Purdue student-housing program for the fiscal year ending May 2025. These records support ongoing housing activity and the overlapping address claims, but do not identify the rental property, landlord, current residents, or whether the two chapters share/overlap at the site. Keep the assignment unresolved and the FID-to-address link spatial only.

## New primary-source evidence

### Zeta Psi housing activity continued through FY2025

The IRS's 2025 electronic Form 990 index has an entry for Indiana Association of Zeta Psi Inc (EIN 35-1525397), tax period 202505, return type 990, XML batch `2025_TEOS_XML_10A`. The exact index row is preserved in `sources/irs_990_index_row_351525397_2025.csv`. The matching return XML is preserved as `sources/indiana_association_zeta_psi_irs_filing_2025.xml`; it is the public IRS return object `202522699349300602_public.xml` from that batch. The IRS describes its Form 990 XML downloads and public disclosure access on its [Form 990 series downloads page](https://www.irs.gov/charities-non-profits/form-990-series-downloads) and [Tax Exempt Organization Search](https://www.irs.gov/charities-non-profits/tax-exempt-organization-search).

The filed return says the association operates “a college fraternity house at Purdue University providing room and board for up to 25 students” and reports $147,088 in program-service revenue with the revenue activity described as “Student housing.” This is strong evidence the housing corporation continued a Purdue housing program during the fiscal year ending May 31, 2025. The return's principal office is in Lake Oswego, Oregon; it does not state that the Purdue house is at 950 David Ross Road or otherwise name a street address. The program description must not be used as proof of FID 748's occupant.

### Chi Psi national classification

Chi Psi's official [2024–25 dues and fees schedule](https://chipsi.org/wp-content/uploads/2025/07/Chi-Psi-Fraternity-Dues-Fees-24-25.pdf) and [2025–26 dues and fees schedule](https://chipsi.org/wp-content/uploads/2025/08/Dues-Fees-25-26.pdf) both place Epsilon Tau (Purdue) in the **Rental** category. The latter PDF is saved at `sources/chi_psi_fraternity_dues_fees_2025-26.pdf`; the earlier official schedule is already retained at `sources/`.

This classification supports that Chi Psi's Purdue Alpha was treated nationally as renting its housing in both academic years. It does not name a street address or landlord and does not establish that the rental is the building at 950 David Ross Road. “Rental” also does not contradict the chapter's use of “Lodge” for a rented chapter facility.

### Address claims remain simultaneous

The current Purdue IFC roster (retrieved 2026-10-26, saved at `sources/purdue_ifc_current_chapters.html`) lists both Chi Psi and Zeta Psi and links the respective local accounts. The linked [Tau Gamma Instagram profile](https://www.instagram.com/zetapsipurdue/) currently displays “950 David Ross Rd” and “Rechartered 2024” (raw capture at `sources/zetapsipurdue_instagram_profile_2026-10-26.html`). This is current-looking first-party self-report, but the profile does not date when its bio was last changed.

Chi Psi's official July 17, 2024 newsletter (saved at `sources/chipsi_alumni_newsletter_summer_2024.pdf`) announces a new lodge, gives 950 David Ross Road, and invites alumni to its September 14 opening ceremony. Its text says the chapter expected to move into the lodge in the coming months; the source supports a planned move and lodge association at that address, but does not independently verify actual or continuing occupancy after the opening.

Correction: the May 15, 2023 official report (`sources/zetapsi_tau_gamma_2023_chapter_report.pdf`, printed p. 9; PDF page 10) lists Tau Gamma / Purdue with “Chapter update not available at press time.” The nearby house-move sentence belongs to Tau Theta / Ontario Tech; it is not a Tau Gamma move report. Purdue GIS FID 748, Tippecanoe parcel GIS, and the 2018 Indiana LiDAR footprint still support that 950 David Ross Road is one physical building; those spatial records do not establish the occupants. The existing evidence and geometry calculations remain in `crosswalk_resolution.md` and `footprint_comparison.json`.

## Assessment

The newly verified IRS return makes it less safe to infer that Zeta Psi simply ceased housing activity when Chi Psi announced its lodge. The two consecutive Chi Psi rental classifications show its Purdue Alpha had rental housing status, while Zeta Psi's corporation reported operating student housing on Purdue's campus for FY2025. Together with Tau Gamma's uncensored current-looking profile at 950, the records are consistent with several arrangements: both groups have some relationship to the same property; one entity rents space to the other; an account/address is stale; or one/both housing programs use facilities elsewhere while retaining a 950 association. Public sources located in this pass do not choose among those explanations.

**Exact remaining evidence gap:** a dated statement from Purdue FSCL, Tau Gamma/Indiana Association of Zeta Psi, or Chi Psi's Alpha Epsilon Tau organization that identifies who occupied 950 David Ross Road in 2024–25 and 2025–26, whether Chi Psi leased all or part of it, and whether Tau Gamma's listed address refers to this same property. If either organization currently occupies a different facility, a dated address is needed before selecting another GIS footprint.

No person was contacted. No geometry, asset, manifest, shared tracker, or master blend was edited. No assignment completion is recommended from this recheck.

## Source snapshots added

- `sources/indiana_association_zeta_psi_irs_filing_2025.xml` — exact FY2025 IRS public return XML, matched by object ID to the IRS-published `2025_TEOS_XML_10A` batch.
- `sources/irs_990_index_row_351525397_2025.csv` — the exact organization's row from the IRS 2025 return index.
- `sources/chi_psi_fraternity_dues_fees_2025-26.pdf` — official Chi Psi fee schedule, showing Epsilon Tau in the rental category.

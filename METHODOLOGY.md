# Methodology

Question: For waste originating in Gibson County, does last year’s same-quarter shipment to the same facility beat a distance-weighted split of this year’s quarterly total on held-out 2024?

This file is the contract. If a later run disagrees with it, the run is wrong.

## What a row is

One row is Gibson origin × receiving facility × calendar quarter.

Tons are the sum of everything IDEM reports received that quarter from Gibson County:

- municipal solid waste
- construction/demolition
- foundry
- coal ash
- flue-gas desulfurization waste
- other non-municipal
- alternate daily cover / reuse

Types are pooled on purpose. The on-site Restricted Waste Site Type I at the generating-station landfill (26-06) is included. A version that drops that site and keeps real MSW only is a different question and a different git.

Filters:

- Drop out-of-state origins.
- Unmatched county names fail closed.
- Same public IDEM XLSX join as the statewide parent (`5800fc3`), then restrict origin to Gibson.

## Data

Source: public IDEM quarterly waste-received XLSX, 2021 through 2025. The lock is the file, not a live Re-TRAC login.

Facility coordinates: IndianaMap authorized operating solid-waste facilities, name-matched. If the GIS name is missing, use the host-county centroid from the facility ID prefix (`XX-YY`). Report how many Gibson destinations are points vs centroids.

CRS: GIS query `outSR=4326`. County centroids stored as WGS84 lon/lat. No warping. Missing CRS is refused.

Population: 2020 Census `ESTIMATESBASE2020`, frozen. In this Gibson-only contest it cancels in the shares, but the name of the bar stays mileage-plus-population because that is what the parent locked.

## The two contestants

### Last year, same quarter

`last_ijq = tons from Gibson to facility j in quarter q-4`

Skip the cell if last year is missing. The win is scored only on the intersection: cells that exist in both years.

### The bar (mileage-plus-population)

Facility set J = Indiana facilities that received Gibson-origin tons in train (2021 Q1 through 2023 Q4).

Holdout and confirmation cannot add destinations. A brand-new 2024 facility gets bar mass 0.

For each Gibson quarter with observed total `T_q`, split across J with

`w_j = pop_Gibson / (miles_j + 1)`

`hat_jq = T_q * w_j / sum_k w_k`

`miles_j` is great-circle miles from the Gibson county centroid to the facility.

ε = 1 mile so a facility sitting on the centroid does not explode.

Origin population is the same for every destination, so it cancels. The bar is inverse-distance wearing the parent’s name.

The bar is scaled to the observed quarterly total, so origin-total bar RMSE is 0 by construction. That is a definition.

## Split

| Block | Quarters | Role |
|-------|----------|------|
| Train | 2021 Q1 through 2023 Q4 | Define facility set J from Gibson-origin rows. Not a model fit. |
| Holdout | 2024 Q1 through 2024 Q4 | The product. Last year is 2023. |
| Confirmation | 2025 Q1 through 2025 Q4 | Out of train and out of J. Reopen only if 2025 reverses the holdout cell sign. A worse-or-same 2025 does not reopen the page. |

## How to keep score

Three results. Do not average the first two. Do not bury the third.

1. Cell assignment. Holdout RMSE in tons on Gibson origin-facility-quarter cells where last year exists. Report MAE next to it. Bar RMSE on all reported 2024 Gibson cells (including 2024-only destinations) is a second line. Do not fold it into the win.
2. Quarterly totals. RMSE on the four Gibson origin-quarter totals. Last year can miss this year’s volume. The bar cannot, because it is handed the volume.
3. What the tons are. Share of reported 2024 Gibson-origin tons at 26-06, Restricted Waste Site Type I (Duke CCR), not MSW.

Parent `5800fc3` is a statewide citation only. That lock’s Gibson row used a statewide destination set (152 receivers; Gibson last-year RMSE 15597 vs bar 76281). This tree does not restamp it and does not promote a statewide win. Facility set J here is the 21 train-era Gibson destinations.

## Figures

One figure file. Two panels.

Holdout scatter: last year and the bar vs observed tons on the intersection, 1:1 line. Left panel is full scale. Right panel zooms to the cells below the 26-06 cluster. Caption is tons of error.

## Residuals that have to stay on the page

26-06 is a centroid, not a surveyed point.
Miles are great-circle, not truck miles.
Out-of-state origin rows are dropped.

## Fixture

One synthetic origin with planted last-year persistence and a 2024-only destination. The toy problem exists so the pipeline can fail closed. Passing the fixture does not prove the live numbers.

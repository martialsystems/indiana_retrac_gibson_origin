# Methodology: Gibson origin last-year shipments vs mileage-plus-population

Question: On Gibson origin-facility-quarter cells, do last year’s same-quarter shipments beat mileage-plus-population on held-out 2024?

## Label

Rows: Gibson origin × receiving facility × calendar quarter.

Tons: sum of Municipal Solid Waste, Construction/Demolition, Foundry, Coal Ash, Flue Gas Desulfurization Waste, Other Non-Municipal, and Alternate Daily Cover/Reuse received that quarter from Gibson County. Types stay pooled. On-site Restricted Waste Site Type I at the generating-station landfill is in that pool. A filtered MSW object, dropping Restricted Waste Site Type I, is a new question and a new lock.

Out-of-state origin is dropped. Unmatched county names fail closed. The join is the same public IDEM XLSX join as parent `5800fc3`, then restricted to origin = Gibson.

## Stream

Public IDEM quarterly waste-received XLSX, 2021 through 2025. The science lock is that file, not a live Re-TRAC Connect login.

Facility coordinates: IndianaMap authorized operating solid waste facilities, name-matched. If the GIS name is missing, the host-county centroid from the facility ID prefix `XX-YY`. Report `n_point` versus `n_centroid` on the Gibson destination set.

CRS: GIS query `outSR=4326`. County centroids stored as WGS84 lon/lat. Warp is none. Missing CRS is refused.

Origin population: 2020 Census `ESTIMATESBASE2020`, frozen.

## Contestant

Last year, same quarter: `last_ijq = tons_{Gibson,j,q-4}`. Skip when that cell is missing. Win is scored on the intersection.

## Bar

Facility set J: Indiana facilities that received Gibson-origin tons in train (2021 Q1 through 2023 Q4). Holdout and confirmation do not add a destination. A new 2024 facility gets bar mass 0.

For each Gibson quarter with observed total `T_q`, split tons across J with weights

`w_j = pop_Gibson / (miles_j + ε)` with `ε = 1` mile.

`miles_j`: great-circle miles from the Gibson county centroid to facility coordinates.

Assignment: `hat_jq = T_q * w_j / sum_{k in J} w_k`.

Origin population is in the numerator of every destination, so it cancels inside this origin’s shares. For one origin the bar is inverse-miles. The name stays mileage-plus-population as locked in the parent.

When scoring the Gibson quarterly total, the bar is scaled to the observed Gibson quarterly total, so origin-total bar RMSE is 0 by construction.

## Split

| Block | Quarters | Role |
|-------|----------|------|
| Train | 2021 Q1 through 2023 Q4 | Facility set J from Gibson-origin rows. Not a fit. |
| Holdout | 2024 Q1 through 2024 Q4 | Product. Last year is 2023. |
| Confirmation | 2025 Q1 through 2025 Q4 | Out of train and out of J. Reopens only if it reverses the holdout cell sign. |

## Metrics

Three sentences. Do not average the first two. Do not omit the third.

1. Holdout RMSE in tons on Gibson origin-facility-quarter cells where last year is present (intersection). MAE second. Bar RMSE on all reported Gibson holdout cells is a second line, not mixed into the win.
2. Gibson origin-quarter total RMSE. Last year can miss this year’s tonnage. The bar cannot.
3. Share of reported 2024 Gibson-origin tons at 26-06, a Restricted Waste Site Type I (Duke CCR), not MSW.

Parent `5800fc3` is a statewide citation only. That lock’s Gibson row used statewide J. This tree does not restamp it and does not promote a statewide win.

## Figures

1. Holdout scatter: last year and the bar vs observed tons on the intersection, 1:1. Caption: tons of error.
2. Destination rank: 2023 share versus 2024 share by receiving facility. Caption: rank of plants.

Two figures max.

## Residual

26-06 is a centroid.
Miles are great-circle.
Out-of-state origin rows are dropped.

## Fixture

One synthetic origin with planted last-year persistence and a 2024-only destination. Fixture skill does not rescue live.

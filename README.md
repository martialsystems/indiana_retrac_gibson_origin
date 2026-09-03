# Gibson County waste shipments: last year vs distance

For waste that originated in Gibson County, Indiana, does "same facility, same quarter, last year" beat a simple distance-weighted split of this year’s total when you hold out 2024?

Short answer: Last year wins the cell-by-cell assignment. It loses the quarterly totals (because the distance model is forced to hit this year’s total exactly). And almost none of this is household trash: 97.8% of reported 2024 Gibson-origin tons went to the Gibson Generating Station restricted-waste landfill (coal combustion residual), facility 26-06.

Locked at commit `c89de5b`. Frozen on purpose.

## What this actually is

Indiana IDEM publishes quarterly waste-received spreadsheets. Each row is roughly: origin county → receiving facility → quarter → tons, with several waste types pooled (MSW, C&D, foundry, coal ash, FGD, other non-municipal, ADC/reuse). On-site restricted waste at the generating-station landfill is included. Out-of-state origins are dropped.

The only public waste siblings are this repo and the statewide parent [`indiana_retrac_last_year`](https://github.com/martialsystems/indiana_retrac_last_year), lock `5800fc3`. In that parent’s largest-origins table, Gibson is the fourth-biggest 2024 origin (1,540,946 tons, 35 cells). Statewide last-year RMSE there is 15597 vs bar 76281. That bar splits Gibson’s total across 152 statewide receivers. This child rebuilds facility set J as the 21 train-era Gibson destinations only. Same contestant, tighter destination set, and a third sentence the parent does not need: almost all of the tonnage is on-site coal ash at 26-06. Parent lock `5800fc3` itself: last year wins assignment on intersection cells (6504.7 vs 16633.0, n=4370); last year loses origin-quarter totals (23313.3 vs 0.0). This tree does not restamp that parent and does not promote a statewide win.

Two models, one holdout:

| Model | What it does |
|-------|----------------|
| Last year | Copy 2023 same-quarter tons to the same facility. If that cell did not exist last year, last year sits out. |
| Mileage-plus-population (the bar) | Take the observed 2024 Gibson quarterly total and split it across facilities that received Gibson waste in 2021 through 2023. Weight is 1 / (great-circle miles + 1). Origin population cancels because there is only one origin, so this is inverse-distance. Scaled to the actual quarter total, so error on the four quarterly totals is 0 by construction. |

Train: 2021 Q1 through 2023 Q4 (only used to define the destination set).
Holdout: 2024.
2025 is confirmation only. It does not reopen the page.

Coordinates: IndianaMap points when a name match exists; otherwise the host-county centroid. CRS is EPSG:4326, no warping. 26-06 is a centroid. Miles are great-circle.

![Figure 1. Holdout scatter](logs/in_live/scatter.png)

Figure 1. Holdout tons. Last year RMSE 15596.8 vs mileage-plus-population 35014.7. Tons of error.

![Figure 2. Destination rank](logs/in_live/dest_rank.png)

Figure 2. 2023 share versus 2024 share by receiving facility. 26-06 holds 97.8% of 2024 reported tons.

## The three results

Do not average them.

1. Where last year exists (35 cells): last-year RMSE 15,596.8 tons vs bar 35,014.7. MAE 4,329.1 vs 17,462.2. Last year wins assignment.
2. The four Gibson quarter totals: last-year RMSE 45,939.1 vs bar 0.0. Last year copies last year’s volume. The bar is handed this year’s volume and only has to guess where. Different question.
3. What the tons actually are: 97.8% of 2024 reported Gibson-origin tons went to 26-06, Restricted Waste Site Type I (Duke CCR), not an MSW landfill.

Bar RMSE on all 48 reported 2024 Gibson cells (including cells with no 2023 twin): 30039.5. That is a second line, not mixed into the win.

2025 confirmation, not used for the call: last-year RMSE 22855.3 vs bar 36332.2. Same sign as 2024. Still not reopening the page.

Locked from `logs/in_live/stage_c_report.json`. RMSE in tons.

| Universe | Last year RMSE | Bar RMSE | n |
|----------|---------------:|---------:|--:|
| Intersection cells (last year present) | 15596.8 | 35014.7 | 35 |
| All reported Gibson holdout cells | | 30039.5 | 48 |
| Gibson origin-quarter totals | 45939.1 | 0.0 | 4 |

## Where the 2024 tons went

| ID | Facility | Type | 2024 tons | Share | Location |
|----|----------|------|----------:|------:|----------|
| 26-06 | Gibson Generating Station RWS 1 South Landfill | Restricted Waste Site Type I (Duke CCR) | 1,507,685.0 | 97.8% | centroid |
| 63-04 | Advanced Disposal Services Blackfoot Landfill | MSW landfill | 19,988.5 | 1.3% | point |
| 63-07 | Velpen CD Landfill | C&D | 4,559.0 | 0.3% | centroid |
| 82-02 | Laubscher Meadows Landfill | MSW landfill | 4,426.3 | 0.3% | point |
| 82-20 | Evansville Transfer Station | Transfer | 2,161.8 | 0.1% | point |
| … | everything else | mixed | under 1,300 each | ~0% | mixed |

If you filter this object down to real MSW only, that is a different question and a different repo.

## Caveats worth saying out loud

26-06 is a centroid, not a surveyed landfill point.
Miles are great-circle, not truck routing.
Out-of-state origin rows are dropped (31965 rows in the statewide join).
Types are pooled. Coal ash and household garbage sit in the same ton column.
The bar cannot miss the quarterly total. Last year can. Comparing those two RMSEs as if they were the same contest is how you lie with this table.

## Run it

Public IDEM XLSX only. No live Re-TRAC login. Empty file, unmatched county, missing coordinates, or missing CRS: `run_live.py` exits 2.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# synthetic fixture first. Passing the toy problem does not prove the live one
PYTHONPATH=src:. python3 scripts/run_fixture.py logs/stage0_fixture
.venv/bin/python -m pytest tests -q

# live (do not overwrite logs/in_live; that lock is frozen)
PYTHONPATH=src:. python3 scripts/run_live.py logs/in_live data/raw
```

Two figures max: holdout scatter, and 2023-vs-2024 destination shares.

## Files

| File | What it is |
|------|------------|
| [METHODOLOGY.md](METHODOLOGY.md) | The contract: labels, split, metrics, what win means |
| [AGENTS.md](AGENTS.md) | Agent rules |
| [CHECKLIST.md](CHECKLIST.md) | Operator list so nobody improves the frozen numbers |
| `src/gibson/` | Join, inverse-miles bar, last-year copy, figures |
| `gibsonforge/` | GraphForge pin |
| `logs/in_live/` | Locked 2024 report and the two plots |

Parent statewide lock (`5800fc3`) is a citation only. This tree does not promote it.

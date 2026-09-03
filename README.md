# Indiana Gibson origin Re-TRAC sheet

On Gibson origin-facility-quarter cells, do last year’s same-quarter shipments beat mileage-plus-population on held-out 2024?

Sheet lock `c89de5b`. Two answers on all reported Gibson-origin tons, including on-site Restricted Waste Site Type I. Last year wins assignment. Last year loses the observed quarterly total. Do not average them. On the 35 cells where last year exists, last-year RMSE is 15596.8 tons against mileage-plus-population 35014.7. MAE is 4329.1 against 17462.2. Bar RMSE on all 48 reported 2024 Gibson cells is 30039.5, a second line, not mixed into the win. Origin-quarter RMSE 45939.1 against 0.0 is the second answer: the bar is scaled to the observed quarterly total. 97.8% of 2024 reported tons is on-site restricted waste. That is the extract. It is not a SWMD MSW product. Last year is a lag-4 copy of last year’s total. Origin population cancels inside one origin’s shares. Confirmation 2025 last-year RMSE 22855.3 against 36332.2 does not reopen the page. Fixture skill does not rescue live.

Parent `5800fc3` ([indiana_retrac_last_year](https://github.com/martialsystems/indiana_retrac_last_year)) is the statewide baseline citation only. Maps lane writeup: https://gist.github.com/martialsystems/16584e78d079666f7e8994b4cc6158be. That lock: last year wins assignment on intersection cells (RMSE 6504.7 vs 16633.0, n=4370); last year loses origin-quarter totals (23313.3 vs 0.0, bar scaled to the observed county total). That lock’s Gibson row used statewide facility set J: last-year RMSE 15597 vs bar 76281; holdout tons 1540946; n=35. This tree does not restamp `5800fc3` and does not promote a statewide win. Facility set J here is the 21 train-era Gibson destinations. 18 of the Gibson destination set sit on IndianaMap points; 9 use the host-county centroid. CRS is EPSG:4326, warp none.

The buyer packet is `delivery/gibson_origin_2024_sheet.pdf`, `delivery/gibson_origin_2024_cells.csv`, `delivery/cover_letter.txt`, and `delivery/cover_email.txt`. County rows are on the PDF and CSV. They are not this README. Private. All rights reserved.

Science lock: public IDEM waste-received XLSX 2021 through 2025 (`e4a8ece1b09c…`). Not a live Re-TRAC login. Train: 2021 Q1 through 2023 Q4. Holdout: 2024. Confirmation 2025 is out of train and out of J. 31965 out-of-state source rows dropped from the lead.

## Live skill (held-out 2024, Gibson origin)

Locked from `logs/in_live/stage_c_report.json`. RMSE in tons.

| Universe | Last year RMSE | Bar RMSE | n |
|----------|---------------:|---------:|--:|
| Intersection cells (last year present) | 15596.8 | 35014.7 | 35 |
| All reported Gibson holdout cells | | 30039.5 | 48 |
| Gibson origin-quarter totals | 45939.1 | 0.0 | 4 |

## Stage 0

One synthetic origin with planted last-year persistence. Fixture skill does not rescue live.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src:. python3 scripts/run_fixture.py logs/stage0_fixture
.venv/bin/python -m pytest tests -q
PYTHONPATH=src:. python3 scripts/run_live.py logs/in_live data/raw
```

Empty IDEM XLSX, unmatched origin county, missing facility coordinates, or missing CRS stops (`run_live.py` exit 2). Stage 0 fixture before live. Two figures max, on the buyer sheet. Do not re-run live onto `logs/in_live` or overwrite the buyer PDF: the sheet is frozen at `c89de5b`.

| File | Role |
|------|------|
| [METHODOLOGY.md](METHODOLOGY.md) | Locked contract |
| [AGENTS.md](AGENTS.md) | Agent rules |
| [CHECKLIST.md](CHECKLIST.md) | Operator list |
| `src/gibson/` | XLSX join, inverse-miles bar, last year, buyer sheet |
| `gibsonforge/` | GraphForge tripwire |
| `delivery/gibson_origin_2024_sheet.pdf` | Buyer PDF: director page 1, 48-row table, two figures |
| `delivery/gibson_origin_2024_cells.csv` | Same 48 rows, same columns, for sorting |
| `delivery/cover_letter.txt` | Full cover letter |
| `delivery/cover_email.txt` | Five-line note |

Research index: https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3

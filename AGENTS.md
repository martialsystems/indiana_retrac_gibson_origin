# Agent notes: indiana_retrac_gibson_origin

Public GitHub. MIT. Question: For waste that originated in Gibson County, Indiana, does "same facility, same quarter, last year" beat a simple distance-weighted split of this year’s total when you hold out 2024?

Live lock `c89de5b`. Three results. Last year wins the cell-by-cell assignment. It loses the quarterly totals (the bar is handed this year’s total). 97.8% of 2024 reported Gibson-origin tons went to 26-06, Restricted Waste Site Type I (Duke CCR), not an MSW landfill. Do not average the first two. Do not omit the third. Parent science lock `5800fc3` is a statewide citation only. Do not restamp it. Do not touch that git. Do not unpark `indiana_hazmat_floodplain`. `indiana_research_console` stays empty. Winter Pages stay off.

The public waste family is three repos: statewide parent `indiana_retrac_last_year` (`5800fc3`), this Gibson child, and `indiana_retrac_msw_only` (`19ac5fa`). Gibson is its own git because the parent’s Gibson row used statewide facility set J (152 receivers; 15,597 vs 76,281 on 35 cells, 1,540,946 tons). This tree rebuilds J as the 21 train-era Gibson destinations and adds the 26-06 type sentence. Do not start an inbound-host sequel here. Do not average cell assignment with the quarterly total. Do not promote a statewide win. Do not filter to MSW and call that this lock.

The extract is all reported Gibson-origin tons, including Restricted Waste Site Type I at 26-06. A filtered MSW object is a new question, new bar, new n, a new git. Parent `5800fc3` stays unfiltered.

Contestant is last year, same quarter. Bar is origin population over great-circle miles, J restricted to Gibson train-era destinations. Origin population cancels. Confirmation 2025 is out of train and out of J. The science lock is the public IDEM quarterly XLSX, not `app.re-trac.com`. Empty XLSX, unmatched origin county, missing facility coordinates, or missing CRS stop (`run_live.py` exit 2). Stage 0 fixture before live. One figure: holdout scatter, full scale plus zoom.

Science lock `c89de5b`. Confirmation 2025 stays out. Do not re-run live onto `logs/in_live`.

`gibsonforge/` is the GraphForge pin. It refuses: Stage 0 missing before live; two answers averaged; README missing the three-sentence lock; restamp of `5800fc3` or `c89de5b`; claim bans (casualties, climate attribution, population-at-risk, logistics optimized, truck routing, next-year Gibson total). Fixture RMSE and figure styling stay on pytest and vbd_gate.

Readable lock is this README. Index gist `66b896b0` lists Re-TRAC. Lane gist `1b6d686320adea674727af588e77bf80`. Stay off Site / `indiana_wx_pages`.

## Verify

`python3 ~/agent_laws_verify_before_done/vbd_gate.py check --app-root . --claim-done`

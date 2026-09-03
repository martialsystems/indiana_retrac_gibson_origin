# Operator checklist

1. Fixture Stage 0 green. Fixture does not rescue live.
2. Freeze the public IDEM 2021 through 2025 waste-received XLSX. Do not log into Re-TRAC Connect for the science lock. Refuse missing CRS.
3. Join origin county, facility ID, quarter, pooled tons. Restrict to origin = Gibson after the same join as `5800fc3`. Train-era Gibson receivers need coordinates (GIS point or host-county centroid). Report `n_point` versus `n_centroid`.
4. Train 2021 Q1 through 2023 Q4 sets Gibson facility set J. Holdout 2024. Confirmation 2025 is out of J. Reopen only if 2025 reverses the holdout cell sign.
5. Two answers. Do not average them. Win is intersection last-year RMSE versus bar. Bar-on-all-reported-Gibson-cells is a second line. Origin-total bar RMSE is 0 by construction. Cite `5800fc3` as statewide baseline only. Do not restamp it. Origin population cancels. Leave residuals in residual: great-circle miles, host-county centroids, 2024-only facilities.
6. Buyer packet: operator PDF, one CSV of the same 48 rows, five-line cover email. Not a git clone. README has no county rows. Sheet lock `c89de5b`. Write the packet from the frozen JSON. Do not rescore `logs/in_live`.
7. GraphForge tripwire in `gibsonforge/`. Stage 0 before live. Two answers not averaged. README has no county rows. Buyer PDF is the only Gibson table. Do not restamp `5800fc3`. Do not refresh `c89de5b`. Claim bans as in AGENTS. Fixture RMSE, figure styling, and gist presence stay on pytest and vbd_gate.
8. Two figures. Stay off the winter page. Do not restamp weather SHAs. Stay off `indiana_research_console`. Confirmation 2025 stays out. Do not start Vermillion inbound.

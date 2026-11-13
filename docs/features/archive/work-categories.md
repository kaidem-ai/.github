# Work categories

## Summary and requirements
Classify Work cards by explicitly configured repository as Clients or Own. Unknown repositories stay uncategorised and visible. Reconcile all open issues, including those on other projects, and report failed or missing automation in the local dashboard.

## Boundaries and data sources
GitHub issues remain authoritative. Only Work membership and Category may change; never alter issue state, status, archived cards or existing unrelated fields. Mapping in boards.json is authoritative; unknown is not inferred. Existing archived cards are not modified. Paginate all project items, repositories and their issues; abort on incomplete or unsafe data.

## Acceptance criteria
Existing non-archived cards for mapped repositories have the configured category; unknowns remain visible. Repeated execution is idempotent. New issues on other boards are eligible. Pagination, errors, unknown repositories and conflicting categories are tested. Dashboard warns on failed, missing or stale workflow runs.

## Open Questions
[RESOLVED] Use explicit mapping rather than guessing; company and product repositories map to Own and observed client repositories to Clients. Unknowns require classification. Do not change existing archive state.

## Checks and implementation plan
Inventory and snapshot; implement and test reconciliation with mock API; create field and views; run migration and independently compare results; enable workflow and inspect its run; update dashboard and documentation; commit and verify.

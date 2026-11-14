# Explicit Work categories and company website routing

## Summary
Preserve explicitly selected Work categories for repositories without a public mapping, and route the company website repository to Work as Own.

## Boundaries and sources
Work project and boards.json remain sources; mapped categories remain authoritative. Unknown repositories without an explicit valid category stay unclassified. No private repository names are added to public configuration.

## Acceptance Criteria
- Known mapped repositories are reconciled as before; archived cards are unchanged.
- An unmapped card with explicit Clients/Own retains it and is not reported unclassified; missing or invalid category remains reported.
- The existing website entry is removed from exclusions and mapped to Own.
- Tests cover mapped, unmapped, archived, valid and missing categories without modifying real issues.

## Open Questions
[RESOLVED] Manually categorised items need no public repository mapping; only categories Clients and Own are accepted. Existing website repository name was already in public exclusions and is now routed to Own.

## Checks
Python unit tests, JSON parse, diff validation and post-merge readback.

## Implementation Plan
Add a failing test, adjust reconciliation, update website mapping and documentation, run tests and deliver via PR.

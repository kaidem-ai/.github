# Work reliability

## Summary and requirements
Provide a local periodic reconciliation using existing authenticated gh plus the cloud fallback. Expose GitHub's open issue dependencies in a saved view and clarify status descriptions. Preserve statuses and archived cards.

## Boundaries and data sources
The existing repository reconciliation script and boards.json at one verified main commit are authoritative. The local runner only runs while the Mac user session is awake and online. No new credential or organisation access is created. GitHub native dependency metadata supplies the dependency view. It does not infer undocumented blockers or decisions. Local state records success and time without issue content.

## Acceptance criteria
A LaunchAgent invokes the source-controlled runner periodically, starts with login, avoids overlapping local runs and reports success or failure. It fetches both files at one commit and runs the same reconciliation as cloud. The dependency view finds the known blocked catalogue issues. Existing statuses and card IDs remain unchanged.

## Open Questions
[RESOLVED] Organisation-wide issue events need additional integration and access. Use the existing GitHub credential and a Mac timer, with cloud workflow as fallback; this is periodic, not event-driven, and cannot run on a sleeping Mac. Next action and responsible party cannot be reliably inferred from dependency links and remain human/agent decisions.

## Checks and implementation plan
Test pinned file retrieval, lock and failure behavior; run runner manually; load and inspect launchd; verify actual timer launch via state; verify view filter and status descriptions. Record limitation and safe recovery. Keep the Command Center unchanged.

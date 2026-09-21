# PTime Repository Instructions

- Public repository: only synthetic contact fixtures. Never commit real contacts,
  messages, meeting records, relationship notes, API tokens or exported recommendations.
- Read README.md, AGENT.md, VERSION, CHANGELOG.md and TODO.md first.
- V2.0 remains an on-demand local CLI, not a scheduler or an outreach sender.
- Use IANA zones and timezone-aware instants. Reject ambiguous/nonexistent naive
  local timestamps; require an explicit numeric offset to disambiguate.
- Priority must never override quiet hours, do-not-contact or same-day follow-up gates.
- Only explicit expected replies/preferred late friend windows and confirmed meeting
  intervals may use the narrow timing exceptions documented in AGENT.md.
- Scores are explainable heuristics, not actual availability or response probabilities.
- No APIs, scraping, background jobs, network calls, calendar invites or messages in runtime.
- Keep P-Global, P-Connection and P-LinkedIn source repositories unchanged.
- Run pytest, all four CLI commands and wheel packaging smoke tests before publishing.

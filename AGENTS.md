# PTime Repository Instructions

- Public repository: only synthetic contact fixtures. Never commit real contacts,
  messages, meeting records, relationship notes, API tokens or exported recommendations.
- Read README.md, AGENT.md, VERSION, CHANGELOG.md and TODO.md first.
- V2.0/V2.1 remain an on-demand local CLI, not a scheduler or an outreach sender.
- Use IANA zones and timezone-aware instants. Reject ambiguous/nonexistent naive
  local timestamps; require an explicit numeric offset to disambiguate.
- Priority must never override quiet hours, do-not-contact or same-day follow-up gates.
- Only explicit expected replies/preferred late friend windows and confirmed meeting
  intervals may use the narrow timing exceptions documented in AGENT.md.
- Scores are explainable heuristics, not actual availability or response probabilities.
- No APIs, scraping, background jobs, network calls, calendar invites or messages in runtime.
- Keep P-Global, P-Connection and P-LinkedIn source repositories unchanged.
- Run pytest, all eight CLI commands and wheel packaging smoke tests before publishing.
- V2.1 festival recommendations need explicit contact opt-in, cycle deduplication,
  recent-contact controls and reply/user-action gating. Region alone is insufficient.
- Preserve V2 hard blocks and add sender-rest protection; no frequency override
  can authorize messaging. Historical source/plan docs remain unchanged.

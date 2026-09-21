# Privacy and Public Repository Boundary

PTime is a public software repository, not a public contact database.

- Only fictional, visibly synthetic contact fixtures belong in Git.
- Real profiles, relationship notes, opportunities, exports and output belong in ignored
  local `private/`, `exports/` or `local/` directories.
- `data/` is ignored except for the reviewed synthetic example and resource initializer.
- Secrets, email addresses, phone numbers, credentials and session data are unnecessary.
- No runtime HTTP client, authentication, scraping, telemetry or message delivery is included.
- Reading a selected private file is explicit. Other project databases are not scanned.
- Text and JSON output may reveal contact data. Do not share it without permission.
- `.gitignore` is a safeguard, not access control or encryption. Inspect every staged diff;
  do not use `git add -f` for private material.
- `do_not_contact` always suppresses recommendations. Eligibility does not establish consent
  or verified personal availability.

If private data is accidentally committed, stop publication, remove it from the working
tree and Git history as appropriate, and rotate any exposed credentials. Deleting one file
in a later commit does not remove earlier versions.

# Security Policy

## Supported versions

Only the latest release (see the `VERSION` file and the
[Releases page](https://github.com/BuiltByAmirali/SoftUpdater/releases))
is supported with security fixes.

## Reporting a vulnerability

Please do **not** open a public issue for security problems. Use
GitHub's "Report a vulnerability" (Security tab of this repository) so
the report stays private until a fix is ready. Reports in English or
Persian are welcome; you will get an answer within a few days.

## What is in scope

- Anything that makes the app execute a downloaded file (SoftUpdater
  must **only ever save** installers, never run them).
- Download URL manipulation (an update check pointing to a
  non-official source).
- Privacy leaks (the app must stay telemetry-free).
- Crashes / data loss caused by malformed vendor data.

## What to expect from the app by design

- **No telemetry, no analytics, no accounts.** Nothing is uploaded.
- The app talks only to: the official sources of your apps (vendor
  feeds / api.github.com), the official download servers when *you*
  click download, and the public UniGetUI icon CDN for prettier rows.
- Logs stay local in `%LOCALAPPDATA%\SoftUpdater\logs\`.

## Beware of fake builds

Official installers are published **only** on the Releases page of this
repository, each accompanied by a `SHA256SUMS.txt`. The app itself shows
the official repository under **Settings → About**. If a copy you
downloaded elsewhere points to a different repository or donation page,
it is not official.

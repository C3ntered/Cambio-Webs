# Security Policy

## Supported Versions

Cambio is currently maintained as a continuously deployed web application and
does not publish versioned long-term-support releases. Security fixes are made
against the latest production release and the current `main` branch.

| Version | Supported |
| --- | --- |
| Latest production release / `main` | :white_check_mark: |
| Older commits, deployments, and forks | :x: |

Users should reproduce a suspected vulnerability against the latest deployed
version or the current `main` branch before reporting it.

## Reporting a Vulnerability

Please report security vulnerabilities privately through
[GitHub Private Vulnerability Reporting](https://github.com/C3ntered/Cambio-Webs/security/advisories/new).
Do not open a public issue, discussion, or pull request containing vulnerability
details before a fix is available.

If private vulnerability reporting is unavailable, use the contact information
on the [maintainer's GitHub profile](https://github.com/C3ntered) to request a
private communication channel before sending technical details.

Include as much of the following information as possible:

- A clear description of the vulnerability and its potential impact.
- The affected page, API endpoint, WebSocket action, or source file.
- Steps to reproduce the issue with a minimal proof of concept.
- Any required room settings, player roles, browser details, or environment
  information.
- Suggested mitigations, if known.

Please avoid including real player data, credentials, access tokens, or room
information belonging to other users.

## What to Expect

- The report should be acknowledged within 3 business days.
- An initial assessment or request for more information should follow within 7
  business days.
- While a confirmed issue is being addressed, updates should be provided at
  least every 7 business days when practical.
- If the report is accepted, the maintainer will coordinate remediation and
  public disclosure with the reporter. Credit will be offered unless the
  reporter prefers to remain anonymous.
- If the report is declined, the maintainer will explain why it is not
  considered a security vulnerability or why it is out of scope.

Response and remediation times depend on severity, complexity, and maintainer
availability. Please allow a reasonable period for a fix before publishing any
details.

## Scope

Security reports may include, but are not limited to:

- Unauthorized access to a room or another player's private game information.
- Exposure of face-down cards, private deck draws, room data, or player data.
- Authentication, authorization, or room-isolation failures.
- Cross-site scripting, injection, request forgery, or unsafe input handling.
- WebSocket message manipulation that bypasses server-side game validation.
- Denial-of-service issues that can be demonstrated safely and with limited
  traffic.

The following are generally out of scope unless they demonstrate meaningful
security impact:

- Gameplay bugs, rule disagreements, or visual defects without a security
  consequence.
- Social engineering, phishing, or attacks requiring physical access.
- Findings that only affect unsupported browsers, old commits, or third-party
  forks.
- Automated high-volume testing, distributed denial-of-service testing, or
  actions that disrupt the live service.
- Reports generated only by automated scanners without a reproducible impact.

## Safe Research Guidelines

When investigating a potential issue:

- Use accounts, rooms, and test data that you control.
- Do not access, modify, retain, or disclose another user's data.
- Do not degrade service availability or generate excessive traffic.
- Stop testing and report the issue if you gain unintended access to sensitive
  information.
- Make only the minimum requests needed to confirm the vulnerability.

Good-faith research that follows these guidelines will be treated respectfully.
This policy does not authorize testing that violates applicable law or affects
systems and data outside this project's control.

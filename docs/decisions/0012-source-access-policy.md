# 0012. Source access policy: allow and deny lists

- **Status:** Accepted
- **Date:** 2026-11-01
- **Extends:** [0008](0008-source-priority.md)

## Context
Some organizations do not want certain sources used at all, for example no results
from PubChem or Wikidata. How restrictive they are varies: some want to block a few
sources, others want to permit only an approved list.

Blocking is also a security concern, not only a display preference. Querying a public
service sends it the structure or name being looked up. For an organization, sending
an unpublished compound to a public service can disclose intellectual property.

Source priority (ADR 0008) controls the order sources are used in, and follows the
usual "most specific setting wins" layering. That layering is wrong for access
control: a personal setting must not be able to re-enable a source the organization
has blocked.

## Decision
- Profiles may define a source access policy:
  - `deny`: these sources are blocked;
  - `allow`: only these sources may be used; everything else, including sources added
    in future pharmakon versions, is blocked.
- Policies combine strictly: a lower layer (personal profile, per-request setting) can
  only make the policy stricter, never looser.
- Policy is enforced where sources are loaded and inside the shared HTTP client
  (ADR 0005), so a blocked source never receives a network request.
- Results state which sources were skipped because of policy, so missing data is
  explained.

## Consequences
- Organizations can choose a permissive (deny list) or restrictive (allow list) posture.
- Allow lists are safe by default against new sources.
- Policy enforcement must be tested by proving that no network request is made, not
  only that results are hidden.

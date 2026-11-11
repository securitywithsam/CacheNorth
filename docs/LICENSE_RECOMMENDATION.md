# Choosing a license for CacheNorth's original code (decision pending)

No license has been applied. Until Security With Sam publishes one, the code is **all rights reserved**: people may read it on GitHub but have no permission to copy, modify, or redistribute it. Choose before making the repository public if you want people to build and share it.

## Recommendation: Apache-2.0 for the code, plus a separate brand policy

- Lets viewers download, build, modify, and share CacheNorth, which is your stated goal.
- Includes an explicit patent grant and requires keeping attribution (`NOTICE`) in copies.
- **Does not grant trademark rights** (Apache-2.0 section 6). Pair it with a short `TRADEMARKS.md` saying "CacheNorth", "Security With Sam", and the logos may not be used for modified or unofficial builds without permission. That keeps your brand protected while the code stays open.
- Compatible with every bundled Python dependency (BSD/MIT/ZPL/Apache/PSF).

## Alternatives

| License | Effect | When to choose it |
|---|---|---|
| MIT | Simplest permissive license; no patent clause | You want minimal text and don't care about patents |
| GPL-3.0 | Anyone who distributes a modified CacheNorth must publish their source under GPL | You want improvements to stay open |
| AGPL-3.0 | Like GPL, and also covers network use | Matches KoboldCpp's license; strongest "keep it open" option |
| Source-available (e.g. PolyForm Noncommercial) | People can read and use it personally but cannot sell it | You want to keep commercial rights exclusive. Not "open source", and GitHub will not label it as such |

## Compatibility notes

- **KoboldCpp (AGPL-3.0)** runs as a separate program that CacheNorth starts and talks to over a local HTTP API. CacheNorth's code is not linked with it, so CacheNorth's own license can be any of the above. **Anyone distributing a built package** (which contains KoboldCpp) must still meet KoboldCpp's AGPL obligations for that component, including source availability.
- **GPXSee and Kiwix (GPL-3.0)** are separate programs that users add; the same reasoning applies.
- **Selling copies:** permissive and GPL-family licenses both allow you, and others, to sell builds. Only a non-open-source license prevents others from selling. Content restrictions (iFixit non-commercial, unresolved archives) apply regardless of the code license.
- Once code is published under an open license, that grant cannot be withdrawn for already-published versions.

This is guidance, not legal advice. If commercial sales are planned, have a lawyer review the final choice and the third-party obligations in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

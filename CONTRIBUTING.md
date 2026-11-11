# Contributing to CacheNorth

Thanks for helping improve portable offline computing.

## Before contributing

1. Check for an existing issue describing the same bug or idea.
2. Open an issue before large architecture or packaging changes.
3. Keep modifications scoped, explain the behavior, and add regression tests when practical.
4. Respect the repository's eventual license and all third-party notices.

## Bug reports

Please provide the CacheNorth version, Windows version, CPU/RAM/GPU, mode (CPU/automatic/manual GPU), model filename or family, expected result, actual result, and steps to reproduce. Redact usernames, chat content, API tokens, session URLs, and personal document paths from logs.

## Development workflow

- Work in a branch and submit a pull request.
- Keep USB drives and personal data out of tests; use temporary fixtures.
- Test packaged application behavior as well as Python source behavior, especially for CPU detection, native launch, shutdown, and file paths.
- Preserve drive-letter independence and paths containing spaces.
- Include before/after evidence for performance and temp-storage changes.
- Do not include model weights, ZIM archives, map datasets, third-party binaries, or private data unless redistribution rights are established and approved.

Exact local build and test commands will be added after reviewing the final source repository.

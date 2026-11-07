# Security Policy

## Reporting a vulnerability

Please avoid posting exploitable security details or sensitive tokens in a public issue. Use GitHub's private vulnerability reporting feature if it is enabled for this repository. Otherwise contact the project maintainer privately through an official Security With Sam contact channel listed on the published project profile.

Include a minimal reproduction, affected version, expected security boundary, and impact. Remove personal conversation contents, identifiable file paths, tokens, and sensitive documents.

## Supported versions

Public version support has not yet been announced. Until then, development and personal-test builds should not be considered production security releases.

## Security principles

- Local AI services bind only to a loopback interface.
- Keep Windows security controls enabled; do not disable Smart App Control or Defender to make optional acceleration work.
- Keep third-party components current and verify their source and hashes.
- Do not assume removable media encrypts stored chats or indexed documents.
- Do not submit customer data, logs containing tokens, or signing credentials in issues or pull requests.

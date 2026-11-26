# Security Policy — LUMINARK CodeWriter Prototype

## Support status

This repository is an experimental prototype. Security reports are reviewed on a best-effort basis; no acknowledgment, remediation, or disclosure timeline is guaranteed.

## Reporting a vulnerability

Do not publish exploitable vulnerabilities in a public issue. Report them privately to:

**LuminarkMeridian@gmail.com**

Include the affected commit, reproduction steps, impact, and any suggested mitigation.

## API authentication

The API has no built-in credentials. Authenticated endpoints return HTTP 503 until `CODEWRITER_API_KEY` is configured with a random secret of at least 32 characters. An optional `CODEWRITER_DEMO_KEY` is development-only and is rejected in production. Do not commit credentials.

Production mode (`ENVIRONMENT=production`) requires Docker execution mode, a strong API key, and explicit HTTPS CORS origins. Local execution mode is permitted only in development.

## Sandbox behavior

Docker execution applies the following controls to each submitted code task:

- Network disabled (`--network none`)
- Memory and CPU limits
- PID limit
- Read-only container root filesystem
- Non-root UID/GID 1001
- All Linux capabilities dropped
- `no-new-privileges`
- Read-only bind mount for the submitted source file
- Temporary `/tmp` filesystem with no-exec and no-suid options
- Process limits applied by `entrypoint.sh`

If the Docker executable is missing, Docker mode now fails closed. It does not automatically execute submitted code on the host.

These controls reduce risk but do not prove complete isolation. Do not treat the sandbox as a security boundary for a multi-tenant public service without independent container-escape testing and an appropriate isolation runtime.

## Known limitations

1. **LOCAL mode executes submitted Python directly on the host.** It is for trusted development tests only and must never be used for untrusted code or production requests.
2. The bridge service in the supplied Compose configuration mounts the host Docker socket. Access to that socket is effectively root-equivalent on the host. The development Compose ports are bound to localhost, but this does not make Docker-socket access safe for an internet-facing deployment.
3. The heuristic Lyapunov/NSDT checks do not certify code correctness, security, or safe behavior. A `PASS` is only a pass against configured model thresholds.
4. Repair logic is heuristic and does not call an integrated language model. It may add comments without changing faulty program behavior.
5. The sandbox does not establish protection against all kernel/container escape vulnerabilities or side-channel attacks.

© 2026 Richard L. Stanfield / Meridian Axiom Alignment Technologies

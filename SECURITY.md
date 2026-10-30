# Security Policy

**Contact:** br4yangil006@gmail.com
**GitHub:** github.com/Bryanhackz
**LinkedIn:** linkedin.com/in/brayan-gil-68b70338b

## Scope
`consistent-hashing-cache` is a distributed cache simulating sharding via multiple SQLite files and a consistent hash ring.

**In scope:**
- HTTP endpoints for cache operations and admin.
- Hash ring algorithm and key routing.
- API-key authentication and rate limiting.

**Out of scope:**
- Multi-node network replication (gossip).
- Redis/Memcached protocol compatibility.
- Operator infrastructure.

## SLA
- Initial acknowledgment: **≤ 48 hours**.
- Mitigation plan: **≤ 7 days**.
- CRITICAL severity patch: **highest priority**.

## Responsible disclosure
Do **not** open a public issue. Email `br4yangil006@gmail.com` with steps to reproduce. Confirmation within ≤ 48h. Public disclosure coordinated after patch.

## Supported versions
Only the latest release on `main` receives security patches.

## Project security practices
- Zero external dependencies.
- API keys hashed with `scrypt` (N=2**14, r=8, p=1, 16-byte salt).
- Constant-time secret comparison via `hmac.compare_digest`.
- Security headers (CSP, COOP, CORP) on every response.
- Parameterized SQL only.
- Static file serving restricted to `templates/` and `static/`.
# LUMINARK CodeWriter
## SAP-based code analysis and repair prototype

**Conceptual framework and project direction:** Richard Stanfield, according to the project owner  
**Software implementation:** AI-generated code, directed and reviewed by the project owner

---

## What is LUMINARK CodeWriter?

LUMINARK CodeWriter is an experimental application intended to inspect Python code, classify selected execution or code-quality conditions using the owner's 0-9-0 / Stanfield's Axiom of Perpetuity framework, and generate repair guidance.

The implementation includes a CLI, FastAPI service, sandbox-related components, SAP stage classification, NSDT calculations, and an optional governance loop. Its current code and tests should be treated as a prototype—not as an independently validated code-security, reliability, or correctness product.

The project owner states that the underlying 0-9-0 framework, CodeWriter concept, and ideas for this application originated with him. AI systems generated the software code and suggested technical mechanisms. NSDT and the Container Rule were introduced by AI as supporting implementation mechanisms within the owner's framework, not as independent conceptual origins. This records the owner's account and is not a legal determination of copyright ownership, inventorship, or exclusive rights.

---

## Intended Governance Flow

The repository is designed around this general flow:

1. Accept code and task context.
2. Execute or inspect the supplied code through the selected execution mode.
3. Extract or estimate a five-dimensional NSDT representation.
4. Apply the repository's SAP stage-classification and scoring rules.
5. Produce a verdict, diagnostic information, and possible repair guidance.
6. Optionally repeat execution after a repair attempt.

These steps describe the intended application workflow. They do not guarantee that all failures will be detected, that repairs will preserve program behavior, or that a PASS verdict means code is safe or correct.

---

## Architecture

The repository includes:
- CLI entry points and a FastAPI service
- SAP geometry, Bayesian-style scoring, energy, and stage-classification modules
- A live-bridge orchestration layer
- Docker-related sandbox configuration
- Automated tests

The repository contains both root-level modules and a `luminark/` package. The packaging and import structure still requires a complete installation test before distribution.

### Execution and security boundaries

- Docker mode applies network, memory, CPU, PID, filesystem, capability, and user restrictions to submitted code. These controls reduce risk but do not prove complete isolation.
- If Docker is unavailable, Docker mode now fails closed. It no longer falls back to running submitted code directly on the host.
- LOCAL mode executes code directly on the host and is only for trusted development tests.
- The API has no built-in credentials. Authenticated routes require a configured `CODEWRITER_API_KEY` of at least 32 characters. A demo key is development-only and rejected in production.
- Production configuration requires Docker mode and explicit HTTPS CORS origins.
- The bridge container in Docker Compose mounts the host Docker socket, which grants root-equivalent access to the host. The supplied Compose ports are bound to localhost for development. This architecture is not appropriate for an internet-facing multi-tenant service without a separate sandbox host or isolation runtime.
- A `PASS` verdict means only that the project's heuristic thresholds were met. It does not certify code correctness, security, or safe behavior.
- Repair logic is heuristic. It does not call an integrated language model and may add comments without fixing the underlying defect.

---

## Stage Reference

| Stage | Canonical Name |
|-------|---------------|
| 0 | PLENARA |
| 1 | SPARK OF NAVIGATION |
| 2 | FORGE OF POLARITY |
| 3 | ENGINE OF EXPRESSION |
| 4 | CRUCIBLE OF EQUILIBRIUM |
| 5 | DYNAMO OF WILL |
| 6 | NEXUS OF HARMONY |
| 7 | LENS OF DISTILLATION |
| 8 | VESSEL OF GROUNDING |
| 9 | TRANSPARENCY OF THE GUIDE |

The stage mapping and associated constraints are implementation rules derived from the project's framework. Their presence in code does not demonstrate that they are established measures of software quality or stability.

---

## Installation and Development

The repository currently documents a Python 3.11+ development setup. Follow the dependency and environment instructions in the project files, then run the test suite:

```bash
pytest tests/ -v
```

The exact installation and packaging path should be verified against the current dependency configuration before distribution.

---

## Test Suite and Evidence

The repository includes unit and integration-style tests, including a file named `tests/test_nsdt_scenarios.py`. This is a software scenario test suite using synthetic/programmed inputs and expected outputs. It is not a clinical trial, does not involve human participants, and provides no clinical or medical evidence.

Passing software tests demonstrates only the behavior covered by those tests. It does not establish that the system reliably detects vulnerabilities, prevents production failures, or generates safe repairs. Independent benchmarks and adversarial testing would be required to support such claims.

---

## Commercial and Technical Status

This repository is a prototype requiring further engineering review. Before any production deployment or commercial transfer, the following should be verified:
- Package installation and dependency resolution
- Correctness and completeness of the execution sandbox
- Network, filesystem, process, and resource isolation
- API authentication and authorization
- Whether generated repairs preserve intended behavior
- Test coverage, false-positive/false-negative rates, and benchmark performance
- Third-party dependency licenses and AI-service terms

No independent accuracy, security, or production-readiness claim is made in this README.

---

## Attribution and Rights Review

## Attribution and Rights Review

The repository has no root `LICENSE` file. The package metadata labels the project proprietary, but no license text is supplied. Do not assume a third-party reuse or redistribution license. Third-party components, AI-service terms, and code provenance require review before licensing or sale.

*Project contact: LuminarkMeridian@gmail.com*

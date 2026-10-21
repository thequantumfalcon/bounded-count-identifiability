# Contributing

Counterexamples, clearer proofs, prior-art references and reproducibility fixes
are especially useful. Read the [claim map](../docs/claims.md),
[roadmap](../docs/roadmap.md) and [reproduction guide](../docs/reproduction.md).

Use an issue for a mathematical or software defect; include the precise claim,
assumptions, smallest example, commands and observed output. Use Discussions
for open-ended questions. Report exploitable software defects privately through
the route in [SECURITY.md](SECURITY.md).

## Development

Use Python 3.11.4 or newer in a virtual environment. The shared command catalog is
`python tools/tasks.py help`; `make help` exposes the same tasks. Install the
locked development dependencies, run lint and installed-package tests, build
both distributions, and test the actual wheel before requesting review.
Proof changes additionally require the pinned Lean build and axiom checks.

Keep changes focused. A pull request should explain the problem, the final
change, the evidence and remaining uncertainty. Use a Conventional Commit title,
such as `fix: reject negative background rates` or `docs: clarify support bound`.
Do not label a finite computation a universal proof or an automated check an
independent human review. Credit mathematical sources, including prior art
that weakens an originality claim.

## Assisted contributions

Tools may assist development, but a contributor remains responsible for the
submission and must be able to explain the changed code or argument. Disclose
material assistance or limitations in the review description when relevant to
assessing the contribution. Unchecked generated output is not sufficient
evidence. This is process disclosure, not authorship credit for a tool.

By submitting a contribution, you confirm that you have the right to contribute
it under the applicable project license. Do not include third-party text or code
without the necessary permission and attribution. The project's conduct policy
applies to all participation. No response deadline or acceptance is promised.

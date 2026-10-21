# Finite probability-law connection

[CountProbabilityBridge.lean](CountProbabilityBridge.lean) constructs actual
mathlib PMFs and probability measures from the core bounded mass vectors,
proves finite expectation formulas, and transfers identification to those
measures. The [source manifest](source_manifest.json) lists all seven roots.

The construction includes zero masses and `D=0`. It does not formalize
independent Poisson addition or the analytic-log derivative interpretation.
See the [extension guide](../../../docs/probability-extensions.md) for scope
and the `--suite research` reproduction command.

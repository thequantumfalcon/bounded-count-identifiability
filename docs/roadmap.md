# Next proof and validation obligations

The [core theorem and sharpness](theorem.md) already have universal arguments and formal implementations. The next steps should strengthen specific remaining claims rather than treat more computation as a substitute for missing assumptions.

The [D=1 deterministic stability bound](../lean/extensions/d1/README.md) is also
formalized: justified errors $\varepsilon$ in the algebraic second cumulant and
$\delta$ in the mean imply parameter error at most $\sqrt{\varepsilon}$ and
background error at most $\delta+\sqrt{\varepsilon}$. This does not supply those
error guarantees from data or complete the inference procedure below.

The [Bernoulli finite-law connection](../lean/extensions/d1-law/README.md) is
also formalized, including endpoint mass validity and the connection to the
core formal observed cumulants. The analytic extension now proves their
all-order equality with logarithm derivatives of actual generating expectations
and states observed-source identification in those analytic terms.

The [probability and sampling extensions](probability-extensions.md) additionally
formalize actual finite probability measures, expectation identities, variance
algebra, conditional coverage and the sample-mean variance calculation under
within-family pairwise independence. Measurable transforms preserve that
independence, and the combined coverage theorem includes zero ceilings.
The actual independent-Poisson generating identity, including a canonical
product probability space, is also formalized. Actual Poisson and
Bernoulli-plus-Poisson factorial moments, quadratic-transform square
integrability, exact single-window variances, sample-mean coverage from the
actual laws, and the exact D=1 projection formula with clipping and empty
cases are formalized in separate extensions. A bounded second-cumulant
perturbation has a formal D=1 stability bound. The remaining tasks below exclude
these completed pieces.

The [originality follow-up](originality-review.md) distinguishes related
results from established priority. A [focused review request](reviewer-request.md)
gives outside mathematicians a self-contained statement and specific questions;
preparing or publishing that request is not evidence that review has occurred.

| Priority | Work | Completion criterion |
| --- | --- | --- |
| 1 | Verify the executable D=1 inference procedure. | Connect executable acceptance, witnesses and emptiness certificates to the formally defined region. The analytic cumulant connection, actual factorial moments, quadratic-transform square integrability and interval elimination are proved; they do not verify Python/Sage execution or its arithmetic library. |
| 2 | Prove robustness to specified deviations. | Connect the formal second-cumulant perturbation bound to an actual mixed-Poisson construction and justified rate-variance control. Extend to stated tail-moment, detector-response or temporal-dependence conditions. Identify nonidentifiability when assumptions are insufficient. |
| 3 | Extend constructive inference. | Develop a general-$D$ feasible-region solver with checkable witnesses or emptiness certificates, and formalize the global continuity estimate. State arithmetic precision, termination and complexity limits. |
| 4 | Improve statistical efficiency. | Compare justified confidence procedures on identical, saved synthetic data; then derive sharper concentration or likelihood guarantees. Keep coverage, computation time and interval width separate. Do not infer optimality from a favorable simulation. |
| 5 | Broaden prior-art and external review. | Obtain independent scrutiny of the exact theorem, proof, formal statement and references. Search older and differently named results. Attribute the established sharpness construction throughout. No originality conclusion follows from an unsuccessful search. |

The [population-centered scale diagnostic](claims.md#population-centered-scale-diagnostic)
makes the current confidence bound's conservatism explicit for one fixed
parameter choice. It is reproducible with exact rational enclosures, but does
not establish typical-data performance or a sample-size lower bound. The
required Sage CI job now supplies repeatable finite boundary, membership and
witness controls; formal verification of executable behavior remains priority 1.

Formal work can proceed locally on these statements. The completed analytic
cumulant connection closes a specification gap; it does not establish detector
assumptions. Source review, a reproducible build and additional checkers improve
confidence, but cannot provide external human review on their own.

## A physical study needs its own evidence

The target must first be specified as the bounded count immediately before background addition. Without calibrated efficiency, this need not be the emitted count. A common background parameter is an expected count per observation window: for constant arrival intensity $\lambda$ and duration $T$, $b=\lambda T$. Realized background counts still fluctuate.

| Assumption | Evidence to collect | Limit of that evidence |
| --- | --- | --- |
| A known bound on the source count and faithful recording. | Independently justified source preparation; raw event times, window definitions, overflow flags and response calibration. | A ceiling imposed by electronics does not establish a source bound. Total counts above $D$ may be background. |
| A common fixed Poisson background parameter. | Interleaved source-off records at matched settings, preserved temporal order, and predefined drift and distribution checks. | A matching mean and variance, or a finite set of matching cumulants, cannot establish the full distribution. |
| Source–background independence within a window. | Labeled component measurements or calibrated controls that vary background independently while holding the source fixed. | Zero covariance alone is insufficient; totals alone do not reveal a unique physical decomposition. |
| An additive detector response. | Pulse-delay and rate sweeps, dark records and checks for dead time, saturation and afterpulsing. | Correcting an average count need not correct higher moments. |
| Pairwise-independent observed windows with common marginal laws for the current confidence theorem; IID windows suffice. | Time-ordered records, predefined windows and lag/block diagnostics, with a justified sampling model or an explicit dependent-data analysis. | Small pair correlations do not establish pairwise independence; pairwise independence does not imply joint independence. |

Detector calibration has its own established methods. [Ware and colleagues](https://www.nist.gov/publications/calibrating-photon-counting-detectors-high-accuracy-background-and-deadtime-issues-0) treat background and dead-time coupling; [Wayne and colleagues](https://www.nist.gov/publications/simple-autocorrelation-method-thoroughly-characterizing-single-photon-detectors) use correlations of time-tagged detections to characterize detector behavior. These references motivate a study; they do not validate an instrument for this project.

Preselect the support bound, background ceiling, window duration, sample size, error level, exclusions and diagnostic tests, or supply a valid analysis of their adaptive selection. An uncertain calibration bound needs its own error accounting. Preserve raw observations and provenance so others can assess the assumptions.

## What can be settled in this setting

Further universal mathematics, formal proofs, exact counterexamples, separately written implementations and reproducible synthetic benchmarks are feasible. They can establish conditional results and reveal failures of proposed claims.

They cannot prove that an unmeasured instrument obeys the model, that a finite record excludes every alternative distribution, or that a theorem is historically original. No finite amount of additional simulation turns those questions into completed proofs. A useful stopping point for each task is its explicit completion criterion, with remaining assumptions and unsuccessful checks retained in the record.

The implementation and illustrative data live in [src/bounded_counts](../src/bounded_counts/) and [examples](../examples/). Current evidence boundaries are maintained in the [claim map](claims.md).

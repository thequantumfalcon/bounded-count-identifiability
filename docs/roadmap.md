# Next proof and validation obligations

The [core theorem and sharpness](theorem.md) already have universal arguments and formal implementations. The next steps should strengthen specific remaining claims rather than treat more computation as a substitute for missing assumptions.

The [D=1 deterministic stability bound](../lean/extensions/d1/README.md) is also
formalized: justified errors $\varepsilon$ in the algebraic second cumulant and
$\delta$ in the mean imply parameter error at most $\sqrt{\varepsilon}$ and
background error at most $\delta+\sqrt{\varepsilon}$. This does not supply those
error guarantees from data or complete the inference procedure below.

The [Bernoulli finite-law connection](../lean/extensions/d1-law/README.md) is
also formalized, including endpoint mass validity and the connection to the
core formal observed cumulants. The remaining probability and analytic
interpretation work in priority 1 is broader than this finite-law connection.

The [probability and sampling extensions](probability-extensions.md) additionally
formalize actual finite probability measures, expectation identities, variance
algebra, conditional coverage and the sample-mean variance calculation under
within-family pairwise independence. A bounded second-cumulant perturbation
also has a formal D=1 stability bound. The remaining tasks below exclude these
completed pieces and retain their unproved distributional connections.

The [originality follow-up](originality-review.md) distinguishes related
results from established priority. A [focused review request](reviewer-request.md)
gives outside mathematicians a self-contained statement and specific questions;
preparing or publishing that request is not evidence that review has occurred.

| Priority | Work | Completion criterion |
| --- | --- | --- |
| 1 | Complete the probability and analytic connections. | Prove independent Poisson addition with nonnegative rate gives the generating-function product, then connect analytic logarithm derivatives to the core formal cumulants. The finite source law and its expectation encoding are already formalized. |
| 2 | Complete the D=1 inference procedure. | Derive the actual factorial moments of the single-window Bernoulli-plus-Poisson count and the necessary independence of transformed observations; join the zero and positive ceiling cases; formalize the elimination formula in [claims.md](claims.md). Verify that software acceptance and emptiness certificates represent that region. |
| 3 | Prove robustness to specified deviations. | Connect the formal second-cumulant perturbation bound to an actual mixed-Poisson construction and justified rate-variance control. Extend to stated tail-moment, detector-response or temporal-dependence conditions. Identify nonidentifiability when assumptions are insufficient. |
| 4 | Extend constructive inference. | Develop a general-$D$ feasible-region solver with checkable witnesses or emptiness certificates, and formalize the global continuity estimate. State arithmetic precision, termination and complexity limits. |
| 5 | Improve statistical efficiency. | Compare justified confidence procedures on identical, saved synthetic data; then derive sharper concentration or likelihood guarantees. Keep coverage, computation time and interval width separate. Do not infer optimality from a favorable simulation. |
| 6 | Broaden prior-art and external review. | Obtain independent scrutiny of the exact theorem, proof, formal statement and references. Search older and differently named results. Attribute the established sharpness construction throughout. No originality conclusion follows from an unsuccessful search. |

Formal work can proceed locally on these statements. A full probability bridge would close a specification gap; it would not itself establish detector assumptions. Source review, a reproducible build and additional checkers improve confidence, but cannot provide external human review on their own.

## A physical study needs its own evidence

The target must first be specified as the bounded count immediately before background addition. Without calibrated efficiency, this need not be the emitted count. A common background parameter is an expected count per observation window: for constant arrival intensity $\lambda$ and duration $T$, $b=\lambda T$. Realized background counts still fluctuate.

| Assumption | Evidence to collect | Limit of that evidence |
| --- | --- | --- |
| A known bound on the source count and faithful recording. | Independently justified source preparation; raw event times, window definitions, overflow flags and response calibration. | A ceiling imposed by electronics does not establish a source bound. Total counts above $D$ may be background. |
| A common fixed Poisson background parameter. | Interleaved source-off records at matched settings, preserved temporal order, and predefined drift and distribution checks. | A matching mean and variance, or a finite set of matching cumulants, cannot establish the full distribution. |
| Source–background independence within a window. | Labeled component measurements or calibrated controls that vary background independently while holding the source fixed. | Zero covariance alone is insufficient; totals alone do not reveal a unique physical decomposition. |
| An additive detector response. | Pulse-delay and rate sweeps, dark records and checks for dead time, saturation and afterpulsing. | Correcting an average count need not correct higher moments. |
| IID windows for the current confidence procedure. | Time-ordered records, predefined windows and lag/block diagnostics, with a justified memory bound or an explicit dependent-data model. | Pairwise independence or small pair correlations do not imply joint independence. |

Detector calibration has its own established methods. [Ware and colleagues](https://www.nist.gov/publications/calibrating-photon-counting-detectors-high-accuracy-background-and-deadtime-issues-0) treat background and dead-time coupling; [Wayne and colleagues](https://www.nist.gov/publications/simple-autocorrelation-method-thoroughly-characterizing-single-photon-detectors) use correlations of time-tagged detections to characterize detector behavior. These references motivate a study; they do not validate an instrument for this project.

Preselect the support bound, background ceiling, window duration, sample size, error level, exclusions and diagnostic tests, or supply a valid analysis of their adaptive selection. An uncertain calibration bound needs its own error accounting. Preserve raw observations and provenance so others can assess the assumptions.

## What can be settled in this setting

Further universal mathematics, formal proofs, exact counterexamples, separately written implementations and reproducible synthetic benchmarks are feasible. They can establish conditional results and reveal failures of proposed claims.

They cannot prove that an unmeasured instrument obeys the model, that a finite record excludes every alternative distribution, or that a theorem is historically original. No finite amount of additional simulation turns those questions into completed proofs. A useful stopping point for each task is its explicit completion criterion, with remaining assumptions and unsuccessful checks retained in the record.

The implementation and illustrative data live in [src/bounded_counts](../src/bounded_counts/) and [examples](../examples/). Current evidence boundaries are maintained in the [claim map](claims.md).

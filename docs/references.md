# References and prior-art boundary

These references establish relevant constructions and methods. They are not a claim that the general $D+1$ identification theorem is new. The review was targeted, not exhaustive: older books, non-English work, subscription literature and alternative terminology remain incompletely covered. Access notes distinguish inspected text from citation-chain leads.

## Sharpness distribution

**G. Afendras and N. Papadatos.** *A factorial moment distance and an application to the matching problem.* Theory of Probability and Its Applications **62**(3), 496–504 (2018); preprint arXiv:1411.1165 (2014). [Primary preprint](https://arxiv.org/pdf/1411.1165), [publisher record and DOI](https://epubs.siam.org/doi/10.1137/S0040585X97T988769).

The inspected preprint's equation (3.1) and Lemma 3.1, PDF page 7, give the generalized matching probabilities and their factorial moments. Set $n=D$ and $\lambda=h$ to obtain the sharpness family used here. Lemma 2.1, equation (2.5), PDF page 5, gives factorial-moment inversion. The paper credits Niermann for the distribution. The project claims no originality for that family or its matching property.

**Stefan Niermann.** *A generalization of the matching distribution.* Statistical Papers **40**, 233–238 (1999). [Publisher record, DOI 10.1007/BF02925521](https://link.springer.com/article/10.1007/BF02925521).

The publisher metadata and abstract were inspected. The full article was not accessed; the precise formula attribution is supported by the accessible Afendras–Papadatos preprint. This distinction avoids implying a direct full-text check of Niermann's article.

**Saeed Golnabi, Martin S. Levy and James J. Cochran.** *Finitizing power series
distributions.* Statistics & Probability Letters **79**(17), 1829–1832 (2009).
DOI 10.1016/j.spl.2009.05.007.
[Publisher preview](https://www.sciencedirect.com/science/article/abs/pii/S0167715209001886).

**James J. Cochran, Martin S. Levy and Saeed Golnabi.** *Matching the finitized
Poisson distribution to the matching distributions.* Statistics & Probability
Letters **83**(6), 1484–1489 (2013). DOI 10.1016/j.spl.2013.02.013.
[Publisher preview](https://www.sciencedirect.com/science/article/abs/pii/S0167715213000564).

Publisher-indexed previews were inspected; direct access was blocked and full
text was not retrieved. The 2013 preview's equivalence section and matching-law
formula support the additional terminology. The accessible Afendras–Papadatos
preprint remains the full-text source for the exact formula and factorial
moments. See the [comparison](originality-review.md#additional-terminology-finitized-poisson-laws).

## Factorial cumulants and Poisson translation

**Bent Jørgensen and Célestin C. Kokonendji.** *Discrete Dispersion Models and their Tweedie Asymptotics.* arXiv:1409.7482. [Primary preprint](https://arxiv.org/pdf/1409.7482).

Section 2.2, equations (2.9)–(2.10), defines the linear factorial-cumulant contribution of Poisson translation and admissible subtraction. Section 2.3 discusses factorial cumulants and thinning. These are established ingredients of the observation model. The inspected statements do not give the specific universal finite $D+1$ cutoff. The accessible document has a 2014 arXiv banner and a later internal date; no version-priority inference is made from that discrepancy.

## Estimation

**Joachim D. Müller.** *Cumulant Analysis in Fluorescence Fluctuation Spectroscopy.* Biophysical Journal **86**(6), 3981–3992 (2004). DOI 10.1529/biophysj.103.037887. [Author-hosted primary PDF](https://groups.spa.umn.edu/2-photon/publications/JM04BJ.pdf).

Appendix B, equations (37) and (39), PDF page 11, gives an unbiased second factorial-cumulant estimator and its exact finite-sample variance in ordinary cumulants. Equations (40)–(41) distinguish the large-sample approximation. This supports the established estimator context, not the bounded-source identification theorem or a claim of competitive performance for this implementation.

## Detector assumptions

**Michael Ware, Alan L. Migdall, Joshua Bienfang and Sergey Polyakov.** *Calibrating Photon-Counting Detectors to High Accuracy: Background and Deadtime Issues.* Journal of Modern Optics **54** (2007). [NIST publication record](https://www.nist.gov/publications/calibrating-photon-counting-detectors-high-accuracy-background-and-deadtime-issues-0).

The NIST abstract describes calibration that accounts for background, dead time, pulse timing and afterpulsing. The public record was inspected; this citation motivates calibration requirements rather than asserting that its procedure has been implemented here.

**Michael Wayne, Joshua Bienfang and Sergey Polyakov.** *A simple autocorrelation method for thoroughly characterizing single-photon detectors.* Optics Express **25**(17) (2017). DOI 10.1364/OE.25.020352. [NIST publication record](https://www.nist.gov/publications/simple-autocorrelation-method-thoroughly-characterizing-single-photon-detectors).

The inspected NIST record describes multi-order correlations of time-tagged events under calibrated illumination. This is a physical-method reference, not evidence from an experiment performed by this project.

## Aggregate recovery

**Laura T. Knoll and colleagues.** *Photon Statistics Modal Reconstruction by
Detected and Undetected Light.* Advanced Quantum Technologies **6**, 2300062
(2023), DOI 10.1002/qute.202300062.
[Publisher full text](https://advanced.onlinelibrary.wiley.com/doi/10.1002/qute.202300062);
[public data deposit](https://zenodo.org/records/7495159).

Equations (7)–(15) model photon-number components, detector response and modal
reconstruction. The inspected deposit has one spreadsheet of aggregate expected
and reconstructed means for 15 configurations; it has no raw time-ordered
counts. This establishes related experimental methodology, not validation of our
confidence procedure or priority of the finite-order theorem. The
[calibration note](calibration.md#photon-counts-and-detector-clicks) explains
why clicks and additive photon counts need separate treatment.

**Nic Fishman, Gokul Gowri, Tanush Kumar, Jiaqi Lu, Valentin de Bortoli,
Jonathan S. Gootenberg and Omar Abudayyeh.** *Count Bridges enable Modeling and
Deconvolving Transcriptomic Data.* arXiv:2603.04730v1 (2026).
[Primary text, Appendix B.2](https://arxiv.org/html/2603.04730v1#A2.SS2).

Definition B.8, Lemma B.9 and Theorem B.10 were inspected. The
[originality review](originality-review.md#aggregate-recovery-from-full-generating-functions)
compares their assumptions with this project's finite-order statement.

## What remains unresolved

**Philipp Stegmann and Jürgen König.** *Inverse counting statistics based on
generalized factorial cumulants.* arXiv:1611.02043v2 (2017).
[Primary preprint](https://arxiv.org/pdf/1611.02043v2).
Sections 2–3, equations (8)–(13), were inspected. The
[originality review](originality-review.md#what-the-search-establishes)
compares the long-time stochastic-generator reconstruction with the bounded
count-law statement and records the paper's uniqueness limitation.

The [follow-up originality review](originality-review.md) examines
Melánová, Sturmfels and Winter's *Recovery from Power Sums*, Proposition 24,
and explains its implication for the Poisson-binomial subclass. That overlap
does not by itself establish priority for the arbitrary bounded-law statement.

No exact statement of identification of every law on $0,\ldots,D$ from factorial cumulants $2,\ldots,D+1$ was located in the inspected material. That is a report of search scope, not proof of novelty. Full-law generating-function uniqueness, moment inversion and generic polynomial-root recovery must be distinguished from the finite-order positivity argument. The known matching family already supplies the lower-order counterexample by a direct calculation.

Corrections and primary references that sharpen this attribution are welcome. Mathematical correctness, historical priority, software correctness and physical validity require different evidence.

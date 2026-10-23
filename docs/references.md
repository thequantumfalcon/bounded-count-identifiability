# References and prior-art boundary

These references establish relevant constructions and methods. They are not a claim that the general $D+1$ identification theorem is new. The review was targeted, not exhaustive: older books, non-English work, subscription literature and alternative terminology remain incompletely covered. Access notes distinguish inspected text from citation-chain leads.

## Sharpness distribution

**G. Afendras and N. Papadatos.** *A factorial moment distance and an application to the matching problem.* Theory of Probability and Its Applications **62**(3), 496–504 (2018); preprint arXiv:1411.1165 (2014). [Primary preprint](https://arxiv.org/pdf/1411.1165), [publisher record and DOI](https://epubs.siam.org/doi/10.1137/S0040585X97T988769).

The inspected preprint's equation (3.1) and Lemma 3.1, PDF page 7, give the generalized matching probabilities and their factorial moments. Set $n=D$ and $\lambda=h$ to obtain the sharpness family used here. Lemma 2.1, equation (2.5), PDF page 5, gives factorial-moment inversion. The paper credits Niermann for the distribution. The project claims no originality for that family or its matching property.

**Stefan Niermann.** *A generalization of the matching distribution.* Statistical Papers **40**, 233–238 (1999). [Publisher record, DOI 10.1007/BF02925521](https://link.springer.com/article/10.1007/BF02925521).

The publisher metadata and abstract were inspected. The full article was not accessed; the precise formula attribution is supported by the accessible Afendras–Papadatos preprint. A renewed access check on 23 October 2026 still found a subscription preview; the [author-affiliated publication list](https://ewas.de/publikationen.html) supplied no full-text link. This distinction avoids implying a direct full-text check of Niermann's article.

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

## Emitter counting by photon coincidences

**Kenneth D. Weston, Martina Dyck, Philip Tinnefeld, Christian Müller,
Dirk P. Herten and Markus Sauer.** *Measuring the Number of Independent
Emitters in Single-Molecule Fluorescence Images and Trajectories Using
Coincident Photons.* Analytical Chemistry **74**(20), 5342–5349 (2002).
DOI 10.1021/ac025730z. [Publisher record](https://doi.org/10.1021/ac025730z).

The publisher-indexed abstract and metadata were inspected. The abstract
reports experimental inference of independent emitter numbers from time-tagged
coincident photons on two detectors. Full text remained purchase-only or
inaccessible; no equation-level comparison is claimed. This is an established
experimental antecedent to the emitter-counting application.

**Haisen Ta, Jürgen Wolfrum and Dirk-Peter Herten.** *An extended scheme for
counting fluorescent molecules by photon-antibunching.* Laser Physics
**20**(1), 119–124 (2010); published online 2009.
DOI 10.1134/S1054660X09170204.
[Publisher record](https://link.springer.com/article/10.1134/S1054660X09170204).

The inspected publisher abstract describes a statistical counting scheme with
pulsed excitation and four avalanche photodiodes. Its accuracy statement is
theoretical, not a measurement reproduced here. Subscription full text was not
obtained.

**Anton Kurz, Jürgen J. Schmied, Kristin S. Grußmayer, Phil Holzmeister,
Philip Tinnefeld and Dirk-Peter Herten.** *Counting Fluorescent Dye Molecules
on DNA Origami by Means of Photon Statistics.* Small **9**(23), 4061–4068
(2013). DOI 10.1002/smll.201300619.
[Publisher record](https://onlinelibrary.wiley.com/doi/abs/10.1002/smll.201300619).

Publisher-indexed and author-affiliated abstracts were inspected; the full
article and supplement were not obtained. The abstracts describe experimental
counting by photon statistics (CoPS) using DNA origami with controlled labeling
and equal dye brightness, including counting precision and acquisition
requirements. These are results for the studied setups, not validation of this
repository's synthetic model or estimator.

**Kristin S. Grußmayer and Dirk-Peter Herten.** *Time-resolved molecule
counting by photon statistics across the visible spectrum.* Physical Chemistry
Chemical Physics **19**(13), 8962–8969 (2017). DOI 10.1039/C7CP00363C.
[Publisher record](https://doi.org/10.1039/C7CP00363C),
[primary supplement](https://www.rsc.org/suppdata/c7/cp/c7cp00363c/c7cp00363c1.pdf).

The abstract and indexed opening of the primary supplement were inspected;
direct full-text retrieval failed. They describe CoPS simulations and
experiments, four-detector event probabilities, optical geometry and a weak
background detection component. The supplement's equations S1–S7 were not
retrieved, so no equation-level equivalence to our additive
binomial-plus-Poisson model is asserted. The [synthetic study](emitter-counting.md)
does not reproduce or benchmark the Weston or CoPS methods.

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

## Power sums and injectivity

**Dania Kambly, Christian Flindt and Markus Büttiker.** *Factorial cumulants
reveal interactions in counting statistics.* Physical Review B **83**, 075432
(2011). DOI 10.1103/PhysRevB.83.075432.
[Primary preprint, arXiv:1012.0750v2](https://arxiv.org/pdf/1012.0750v2),
[publisher record](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.83.075432).

Section II.C, equation (14), PDF page 4, gives the generalized-binomial
factorial-cumulant power sums. Appendix B, equation (B1), PDF page 11, extracts
a dominant conjugate singularity pair using high-order asymptotics. These
locations were inspected on 23 October 2026; see the
[hypothesis comparison](originality-review.md#a-closer-overlap-the-poisson-binomial-subclass).

**Hana Melánová, Bernd Sturmfels and Rosa Winter.** *Recovery from Power Sums.*
Experimental Mathematics **33**(2), 225–234 (2024); published online 2022.
DOI 10.1080/10586458.2022.2061650.
[Inspected preprint, arXiv:2106.13981v1](https://arxiv.org/pdf/2106.13981v1),
[publisher record](https://doi.org/10.1080/10586458.2022.2061650).

Proposition 24, PDF page 12, identifies a nonnegative $D$-vector up to
permutation from any $D$ distinct positive-integer power sums. The
[originality review](originality-review.md#a-closer-overlap-the-poisson-binomial-subclass)
derives its implication for sums of independent Bernoulli variables and
explains why that substitution does not cover every bounded law. The statement
and its cited injectivity source were rechecked on 23 October 2026; no
independent audit of the proposition's proof is claimed. Direct publisher
access remained unavailable; the comparison is pinned to the preprint version.

**Stefan Müller, Elisenda Feliu, Georg Regensburger, Carsten Conradi, Anne Shiu
and Alicia Dickenstein.** *Sign conditions for injectivity of generalized
polynomial maps with applications to chemical reaction networks and real
algebraic geometry.* Foundations of Computational Mathematics **16**, 69–97
(2016). DOI 10.1007/s10208-014-9239-3.
[Primary preprint, arXiv:1311.5493v2](https://arxiv.org/pdf/1311.5493v2).

Definitions 1.1–1.3 and Theorem 1.4, PDF pages 2–3, were inspected on
23 October 2026 by following the reference in *Recovery from Power Sums*,
Proposition 24. The theorem gives equivalent injectivity, Jacobian and sign
conditions for a family of generalized polynomial maps on the positive
orthant. Its conditions quantify over all positive coefficient parameters.
No reduction of the arbitrary bounded-law cumulant map, including its boundary
laws, to these hypotheses was established. This is an explicit further-review
lead, not evidence that the universal missing-mean theorem is new or already
covered.

## What remains unresolved

**Philipp Stegmann and Jürgen König.** *Inverse counting statistics based on
generalized factorial cumulants.* arXiv:1611.02043v2 (2017).
[Primary preprint](https://arxiv.org/pdf/1611.02043v2).
Sections 2–3, equations (8)–(13), were inspected. The
[originality review](originality-review.md#what-the-search-establishes)
compares the long-time stochastic-generator reconstruction with the bounded
count-law statement and records the paper's uniqueness limitation.

No exact statement of identification of every law on $0,\ldots,D$ from factorial cumulants $2,\ldots,D+1$ was located in the inspected material. That is a report of search scope, not proof of novelty. Full-law generating-function uniqueness, moment inversion and generic polynomial-root recovery must be distinguished from the finite-order positivity argument. The known matching family already supplies the lower-order counterexample by a direct calculation.

The [publication decision](originality-review.md#publication-decision), updated
23 October 2026, is to present the short proof and attributed sharpness without
a novelty claim. The review records the exact outstanding questions needed to
change that decision.

Corrections and primary references that sharpen this attribution are welcome. Mathematical correctness, historical priority, software correctness and physical validity require different evidence.

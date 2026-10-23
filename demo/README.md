# Interactive bounded-count demo

[Open the live demo](https://bounded-count-explorer.thomasalbrecht2024.chatgpt.site).
It is publicly viewable without signing in.

This static browser companion illustrates three population calculations:
independent fixed-Poisson background leaves higher factorial cumulants unchanged;
the established generalized matching family explains why order `D+1` is needed
in general; and a Bernoulli source has an explicit inverse from its mean and
second factorial cumulant. Read the [theorem](../docs/theorem.md) and
[claim map](../docs/claims.md) for the universal statements and assumptions.

## Run locally

From the repository root, with Python 3.11.4 or newer:

```sh
python -m http.server 8765 --bind 127.0.0.1 --directory demo
```

Open [the local demo](http://127.0.0.1:8765/). The page uses local HTML, CSS,
JavaScript and SVG files, with no build step or runtime package installation.
Its calculations work offline; links to research sources require a connection.
Stop the server with `Ctrl+C`. Opening `index.html` directly may block JavaScript
modules, so use the local server.

## Mathematical scope

Inputs represent chosen population quantities, not experimental measurements.
The support bound applies to the source count. The observed count has unbounded
support whenever the Poisson background is positive; probability plots account
for the tail beyond the displayed integer counts.

Rational inputs and factorial-cumulant identities use exact arithmetic. The
Bernoulli inverse tests feasibility using rational comparisons before displaying
square roots. Irrational inverse values, Poisson probabilities and graphical
coordinates are numerical approximations; displayed decimal values are rounded.
Plots do not supply the cumulants used in the mathematical comparisons.

A compatible inverse does not establish that an observed process obeys the
model. Source/background independence, a fixed nonnegative Poisson rate and the
source support bound are assumptions. Finite-sample uncertainty, physical
calibration and historical priority remain separate. The browser implementation
is not formally verified; the [proof guide](../lean/README.md) describes the
encoded results and trusted components. The [process disclaimer](../PROVENANCE.md)
also applies to this companion.

## Check the implementation

The page itself has no runtime dependencies. Tests use Node.js 24 and the exact
development versions in [package-lock.json](package-lock.json). From `demo/`:

```sh
npm ci --ignore-scripts
npm test
npx --no-install playwright install chromium firefox webkit
```

On Linux, install browser system dependencies with
`npx --no-install playwright install --with-deps chromium firefox webkit`.
Dependency and browser installation require network access.

For the browser checks, serve the repository root in a separate terminal:

```sh
python -m http.server 8765 --bind 127.0.0.1
```

Then run `npm run test:browser` from `demo/`. The runner opens
`http://127.0.0.1:8765/demo/`; stop an earlier server on the same port first.
Set `DEMO_URL` to test another local preview, including the standalone server
above. `DEMO_BROWSERS` and `DEMO_WIDTHS` can narrow a diagnostic run; the default
matrix uses Chromium, Firefox and WebKit at widths 1440, 1280, 768, 390 and 320.

The [Python fixture generator](../tools/generate_demo_fixtures.py) compares the
committed rational fixtures with the installed `bounded_counts` package. From
the repository root, after the [development setup](../.github/CONTRIBUTING.md):

```sh
python tools/generate_demo_fixtures.py --check
```

The math tests compare exact results and exercise invalid inputs and boundaries.
Browser checks exercise the controls, exports, keyboard access, responsive
layout and the page without JavaScript. They retain screenshots, automated
accessibility findings and a JSON report in `build/demo-qa/` by default. Override
that destination with `DEMO_QA_OUTPUT`.

The required `demo` CI job runs these checks and uploads `demo-browser-qa`,
including available failure diagnostics, for 14 days. Consult the completed run
for the exact commit inspected. A configured check or a saved screenshot is not
evidence that a person visually reviewed it. Automated accessibility checks are
partial, and finite browser tests neither prove general software correctness
nor replace the mathematical proofs.

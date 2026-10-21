UPSTREAM PROVENANCE

The project pins Lean 4.35.0 and mathlib revision
56a005855ea17e0b0958f73ec801ae140b0a1679.

provenance.json records all nine package revisions: mathlib and its eight
transitive dependencies. Their revision identities were checked against the
local source snapshots. The lock file was assembled from mathlib's existing
lake-manifest.json, with those packages inherited by the new top-level project.

The license texts in licenses/ are exact copies from the inspected dependency
distributions. They are included for attribution and review; dependency source
code, compiled libraries, and tool binaries are not bundled in this project.
These notices do not imply endorsement by any upstream author or organization.

Lean's release additionally includes notices for bundled components, copied as
Lean-bundled-LICENSES.txt. Consult that file if redistributing a Lean toolchain.

The license governing this project's own proof sources and tooling is set by
the repository's top-level license, independently of these upstream notices.

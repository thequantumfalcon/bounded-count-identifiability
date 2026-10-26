# Derivatives of the location polynomial

[CountRootStructure.lean](CountRootStructure.lean) imports the
[largest-root module](../largest-root/README.md). It defines a polynomial in
the displacement from the mean, proves its equality to `topCoeff`, and identifies
its coefficients and derivatives. For a law supported on $0,\ldots,D$, the
first derivative at zero displacement equals $p_D$.

The derivatives are those of the explicitly defined location polynomial.
The module does not state a root-multiplicity theorem in terms of the maximum
support point, prove an implicit-function theorem for the cumulant inverse,
or establish a finite-sample error bound. These distinctions matter at padded
supports, where $p_D$ can be zero.

The [source manifest](source_manifest.json) binds this module and these roots:

- `CountRootStructure.locPoly_eval`
- `CountRootStructure.locPoly_coeff`
- `CountRootStructure.locPoly_iterate_derivative_eval_zero`
- `CountRootStructure.law_derivative_at_mean`

Use the [shared research verification and replay commands](../largest-root/README.md#reproduce).
They rebuild the imported core and largest-root module into fresh outputs,
then audit these roots separately. No additional axiom is introduced.

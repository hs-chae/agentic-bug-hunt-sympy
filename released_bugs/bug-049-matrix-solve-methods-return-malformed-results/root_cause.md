# Root Cause Diagnosis

## Candidate

Matrix.solve methods return malformed results on singular systems

## Source-Level Diagnosis

Matrix.solve dispatches directly to method-specific solvers without a singularity/rank guard; Cramer divides by det(M), which is zero.

## Missing Guard

The implementation accepts or simplifies a candidate without preserving the domain, branch, support, or singularity condition described in the bug report.

## Patch Target

Add the missing guard or residual validation at the affected subsystem listed in the artifact README.

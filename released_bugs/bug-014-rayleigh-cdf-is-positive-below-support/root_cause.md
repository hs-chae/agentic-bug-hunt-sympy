# Root Cause Diagnosis

## Candidate

Rayleigh CDF is positive below support

## Source-Level Diagnosis

RayleighDistribution declares nonnegative support, but its custom _cdf returns an unguarded formula and bypasses generic support enforcement.

## Missing Guard

The implementation accepts or simplifies a candidate without preserving the domain, branch, support, or singularity condition described in the bug report.

## Patch Target

Add the missing guard or residual validation at the affected subsystem listed in the artifact README.

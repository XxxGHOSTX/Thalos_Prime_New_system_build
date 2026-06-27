# THALOS Core Formalism

This document defines the canonical core for THALOS Prime.

## Purpose

THALOS Prime must be a single formal system, not a collection of unrelated modules. The core must define the objects, operations, invariants, and tests that every higher-level layer depends on.

## Primitive objects

- Fact
- Observation
- Assumption
- Inference
- Contradiction
- Unresolved gap
- Provenance record
- Confidence / uncertainty model

## Allowed operations

- ingest
- validate
- transform
- merge
- reject
- quarantine
- revise

## Invariants

1. Every output must trace to inputs or declared assumptions.
2. Contradictions must be explicit.
3. Confidence must be bounded and explainable.
4. Invalid state transitions must fail loudly.
5. No feature may bypass provenance or validation.

## Required implementation shape

- A single authoritative Python package for the core.
- One CLI command that loads sample inputs and emits traced outputs.
- One test file that verifies invalid transitions are rejected.
- The reasoning layer must depend on the kernel, not replace it.

## Minimum validation suite

- Deterministic fixtures.
- Contradiction cases.
- Missing-data cases.
- Provenance checks.
- Regression tests for transformations.

## Current gap

The repository contains useful modules and orchestration, but it does not yet define a canonical epistemic kernel. That is the missing foundation.

## Next build step

Implement the smallest runnable version of this formalism and make every higher-level module depend on it.
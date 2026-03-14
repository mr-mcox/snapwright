# Prototype: Recall Safes

**Question**: What does a Wing snapshot recall look like at different points in the service
lifecycle — and which parameters need safe protection for mid-service recall to be
non-disruptive?

**Started**: 2026-03-12
**Status**: not started

---

## Background

The renderer currently writes nothing to `ce_data.safes`; Init.snap's "no safes" state
passes through. Monitor faders are designed to drift each service (musicians adjust in-ear
and wedge levels during rehearsal), so a full recall mid-service would reset them to DSL
starting points — disorienting at best, feedback risk at worst.

The encoding is known (one ASCII character per parameter in a string; empty = unprotected).
The policy is not: which parameters actually need protection, and does the answer differ
between a pre-service load and a mid-service recall?

**Rig context**: Snapshots are not currently recalled mid-service. This is exploratory —
understanding what safe protection would need to cover if that behavior were introduced.

---

## Exploration Paths

1. **Pre-service load**: Load a fresh snapshot before the team arrives. What resets? What
   do volunteers have to manually restore? Is a pre-service load benign without any safes?

2. **Mid-service recall**: Simulate a mid-service recall (during rehearsal or after service
   starts). What jumps? Monitor faders, send levels, DCA assignments — what else?

3. **Minimum safe mask**: Given observations from (1) and (2), what is the smallest set of
   protected parameters that makes a recall safe at any service phase?

4. **Pre-service vs. during-service distinction**: Is one safe mask correct for both phases,
   or do you want different behavior depending on when the recall happens?

---

## Learnings

(entries added as experiments are run)

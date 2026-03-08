---
feature: priscilla-spelling
date: 2026-03-08
commit: 9b4bb7b
branch: main
status: implementing
read-when: "just do it"
---

## Problem

The musician file `data/dsl/musicians/priscilla-vox.yaml` has `name: Pricilla` (missing an L). This typo propagates to all rendered snapshots and Wing fader labels. Confirmed as typo by Matthew.

## Not Doing

- No other musician name audit (Investigation E found no other spelling issues)
- No snapshot regeneration in this ticket — that happens when other features land

## Constraints

- Fix the name field in `priscilla-vox.yaml` to `Priscilla`
- Check if any test fixtures reference the misspelled name and update them

## Escalation Triggers

- None — this is a one-line fix

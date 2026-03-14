---
feature: left-center-surface
date: 2026-03-12
commit: 7c801d5
branch: main
status: problem-space
read-when: "starting problem space — one open design question before brief can be written"
---

## Problem

The left (24-strip) and center (16-strip) surfaces receive only a selected-page indicator
from the renderer — no strip content is written. Volunteers working from either surface see
Init layout. The right surface USER1 page (Handheld, Headset, STREAM, HOUSE) covers the
trained send-on-fader workflow, but the left and center surfaces are used for fader riding
and DCA control and currently have no renderer-owned layout.

## Open Design Question

The James reference shows a clear pattern — L: channels 1–12 in order; C: DCAs 1–8 in
order. Center is straightforward (DCAs are infrastructure-level and fixed). Left is the
question: does the left USER1 page show a **fixed infra-level list** (same for all teams,
regardless of assembly), or does it **derive from the assembly channel order** (follows the
team, shifts as musicians change)?

James has 12 assembly channels occupying 1–12 and the reference shows exactly that. But if
a team has fewer channels or in a different order, a fixed list would show gaps or wrong
channels. Assembly-derived is more correct but adds a renderer dependency between
infrastructure rendering and the assembly; it also means left layout is a team-level
concern, not purely infrastructure.

## Not Doing

(TBD — pending resolution of the design question above)

## Constraints

(TBD)

## Escalation Triggers

(TBD)

## Decisions

(populated during implementation)

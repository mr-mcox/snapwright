# Evolution Module — Prototype Learnings

What the prototype taught us before the TDD rewrite. This is the "what carries forward"
document. The prototype code in `snapwright/evolution/` will be deleted after tests are
written.

---

## What the module needs to do

1. **Flatten a Wing channel dict** into a `path → value` map for tractable comparison.
   Only tracked sections matter: `fdr`, `mute`, `flt`, `eq`, `dyn`, `gate`, `send`, `in`.
   Sends to unnamed/vestigial buses should be excluded.

2. **Diff two flattened channels** with Wing's 3-sig-fig float tolerance.
   Produce a list of changed paths with old/new values.

3. **Translate a Wing path + values into audio-meaningful terms**.
   This is the most knowledge-dense piece. Key learnings:
   - EQ params need the model in context (STD bands vs SOUL/E88 4-band vs PULSAR)
   - Dynamics params need the model (ECL33 has separate leveler/comp params; LA has
     `ingain`="gain" and `peak`="peak reduction"; NSTR has `in`/`out`)
   - Gate params need the model (PSE has `depth`; RIDE has `tgt`/`spd`)
   - Send level involving -144 (Wing's off sentinel) should suppress the numeric delta —
     the on/off state is the meaningful signal, not the ±136 dB swing
   - Frequency formatting: comma-separated integer Hz (12,000 Hz not 1.2e+04)
   - dB formatting: always signed (+1.0 dB, -3.2 dB)

4. **Significance thresholds** — changes below these are noise, not surfaced:
   - Fader / send level: ≥ 2 dB
   - EQ gain: ≥ 1.5 dB
   - EQ / filter frequency: ≥ 10% relative shift
   - Dynamics threshold: ≥ 2 dB
   - Dynamics ratio: ≥ 0.5
   - Gate range: ≥ 3 dB
   - Input trim: ≥ 2 dB
   - Boolean changes (on/off, mute, model): always significant

5. **Pattern detection** across N SnapshotDiffs:
   - Key is (channel_name, channel_num, path) — channel_num disambiguates same-named
     channels (James appears as both ch13 instrument and ch25 vocal)
   - `consistent_direction`: all numeric deltas same sign
   - `constant_offset`: all numeric deltas identical (within rounding) — signals stale
     baseline, not genuine recurring adjustment; worth surfacing but distinct signal
   - `recent_count`: occurrences in second half of batch — recency is a quality signal
   - Sort order: consistent + recent + high count first

6. **Report** is markdown with two main sections:
   - Patterns grouped by channel, annotated with count/recency/direction/offset flag
   - Suggestions as "Consider [action] **Channel Section label** to value (Nx)"
   - Per-snapshot detail for reference

---

## Natural seams

- **Significance** belongs as a first-class concept, not inline in translate. Tests should
  be able to say "this delta is significant for this path" independently of translation.

- **Translation** (path + values → human label) is pure and should be fully unit-testable
  with no Wing snapshot loading.

- **Flattening** (channel dict → path/value map) is a pure function on a dict.

- **Diff** = flatten both channels + filter by significance + translate. Depends on the
  above three. Channel-level and snapshot-level aggregation are thin wrappers.

- **Pattern detection** operates on diffs, not raw Wing data. Pure data transformation.

- **Report rendering** is formatting only. Low test value; integration test via CLI is
  sufficient.

---

## Edge cases worth encoding in tests

- Channel named "James" appears twice (ch13, ch25) — patterns must not collide
- Send level change involving -144: delta suppressed, significance still applies to on/off
- EQ model change: always significant regardless of value
- Float near-equality: 3.330078125 and -3.33 are the same (3 sig figs)
- EQ shelf Q stored as string "LOW" in some model states (not a float)
- Frequency delta display: relative threshold (10%) not absolute
- Bus names: only named buses tracked; bus 7/8 excluded
- Unnamed channels (empty name string): excluded from diff entirely

---

## What the prototype got wrong (or awkward)

- Significance thresholds scattered inline in `translate._is_significant` — hard to test
  in isolation, hard to read as a policy
- `_fmt` path-matching was fragile (string substring checks on path strings)
- `set_line` edit tool produced duplicate lines in report.py — symptom of tangled concerns
- EQ "avoid doubling" logic had a subtle bug: "eq" is a substring of "freq", so "high
  shelf freq" labels had their section stripped incorrectly
- No separation between "is this change significant?" and "how do I label this change?"

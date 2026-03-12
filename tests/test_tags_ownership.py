"""Tests for tags-ownership feature.

Channel tags (#D<n>, #M<n>) are built from DSL declarations and written by the
renderer. The renderer owns ch.tags completely — no merge with the base template.

DSL contract:
  - AssemblyDef.channel_mute_groups: assembly-level default mute-group membership
  - AssemblyDef.channel_dcas:        assembly-level default DCA membership
  - MusicianEntry.mute_groups:       per-musician override (None → use assembly default)
  - MusicianEntry.dcas:              per-musician override (None → use assembly default)

Invariants enforced here:
  - build_tags() is a pure function of (dcas, mute_groups)
  - Assembly channels get tags from their resolved membership lists
  - Non-assembly channels always get tags = ""
  - Bus tags are not disturbed by channel-tag rendering
"""

from pathlib import Path

import pytest

from snapwright.dsl.renderer import build_tags, render_assembly

JAMES_ASSEMBLY = Path("data/dsl/teams/james/assembly.yaml")


# ---------------------------------------------------------------------------
# build_tags — pure function
# ---------------------------------------------------------------------------


class TestBuildTags:
    def test_empty_inputs_produce_empty_string(self):
        assert build_tags([], []) == ""

    def test_single_mute_group(self):
        assert build_tags([], [8]) == "#M8"

    def test_single_dca(self):
        assert build_tags([5], []) == "#D5"

    def test_multiple_dcas_and_mute_groups(self):
        assert build_tags([1, 4], [8]) == "#D1,#D4,#M8"

    def test_dca_tokens_precede_mgrp_tokens(self):
        result = build_tags([3], [7])
        assert result.index("#D3") < result.index("#M7")

    def test_order_within_dcas_preserves_input_order(self):
        assert build_tags([3, 1], []) == "#D3,#D1"

    def test_order_within_mgrps_preserves_input_order(self):
        assert build_tags([], [6, 5]) == "#M6,#M5"


# ---------------------------------------------------------------------------
# Channel tag rendering — James assembly
# ---------------------------------------------------------------------------


class TestChannelTagsJamesAssembly:
    """The rendered James assembly must match the tag pattern in
    data/reference/snapshots/james-2025-12-14.snap."""

    @pytest.fixture(scope="class")
    def snap(self):
        return render_assembly(JAMES_ASSEMBLY)

    def test_worship_channels_have_m8(self, snap):
        """Channels 1-8, 13-16, 25-28 belong to mute group 8 (Worship)."""
        worship_channels = [1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 16, 25, 26, 27, 28]
        for ch_num in worship_channels:
            tags = snap["ae_data"]["ch"][str(ch_num)].get("tags")
            assert tags == "#M8", f"ch{ch_num}: expected '#M8', got {tags!r}"

    def test_spare_channels_have_empty_tags(self, snap):
        """Handheld (ch37) and headset (ch38) are spares excluded from Worship."""
        for ch_num in [37, 38]:
            tags = snap["ae_data"]["ch"][str(ch_num)].get("tags")
            assert tags == "", f"ch{ch_num}: expected '', got {tags!r}"

    def test_non_assembly_channels_have_empty_tags(self, snap):
        """Channels not declared in the assembly keep tags = ''."""
        non_assembly = [
            9, 10, 11, 12,
            17, 18, 19, 20, 21, 22, 23, 24,
            31, 32, 33, 34, 35, 36,
        ]
        for ch_num in non_assembly:
            tags = snap["ae_data"]["ch"][str(ch_num)].get("tags")
            assert tags == "", f"ch{ch_num}: expected '', got {tags!r}"

    def test_infra_channels_have_empty_tags(self, snap):
        """Infrastructure channels ch39 and ch40 are not worship channels."""
        for ch_num in [39, 40]:
            tags = snap["ae_data"]["ch"][str(ch_num)].get("tags")
            assert tags == "", f"ch{ch_num}: expected '', got {tags!r}"


# ---------------------------------------------------------------------------
# Bus tags not disturbed
# ---------------------------------------------------------------------------


class TestBusTagsUndisturbed:
    """Channel tag rendering must not modify bus.tags — those are set by
    infrastructure.yaml and the infrastructure renderer."""

    @pytest.fixture(scope="class")
    def snap(self):
        return render_assembly(JAMES_ASSEMBLY)

    def test_mix_buses_retain_mgrp_tags(self, snap):
        expected = {
            "1": "#M5",
            "2": "#M5",
            "3": "#M5",
            "4": "#M5",
            "5": "#M6",
            "6": "#M5,#M6",
            "7": "#M5,#M6",
        }
        for bus_num, tag in expected.items():
            actual = snap["ae_data"]["bus"][bus_num].get("tags")
            assert actual == tag, f"bus{bus_num}: expected {tag!r}, got {actual!r}"

    def test_fx_return_buses_retain_dca_tags(self, snap):
        for bus_num in ["9", "10", "11", "12"]:
            actual = snap["ae_data"]["bus"][bus_num].get("tags")
            assert actual == "#D5", f"bus{bus_num}: expected '#D5', got {actual!r}"

    def test_monitor_buses_have_empty_tags(self, snap):
        for bus_num in ["13", "14", "15", "16"]:
            actual = snap["ae_data"]["bus"][bus_num].get("tags", "")
            assert actual == "", f"bus{bus_num}: expected '', got {actual!r}"

"""Snapwright CLI."""

import sys
from pathlib import Path

import click

from snapwright.dsl.renderer import render_assembly
from snapwright.evolution.diff import diff_snapshots
from snapwright.evolution.patterns import find_patterns
from snapwright.evolution.report import render_report


@click.group()
def main():
    """Snapwright — Wing snapshot DSL toolchain."""


@main.command()
@click.argument("assembly", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output .snap path. Defaults to <assembly_dir>/<team_name>.snap",
)
def render(assembly: Path, output: Path | None):
    """Render a team assembly to a Wing .snap file.

    ASSEMBLY is the path to a teams/*/assembly.yaml file.
    """
    try:
        from snapwright.dsl.loader import load_assembly
        asm_def, _ = load_assembly(assembly)
        team_slug = asm_def.team_name.lower().replace(" ", "-")

        if output is None:
            output = assembly.parent / f"{team_slug}.snap"

        snap = render_assembly(assembly, output)
        n_channels = sum(
            1 for ch in snap["ae_data"]["ch"].values()
            if ch.get("name")
        )
        click.echo(f"✓ Rendered {asm_def.team_name} → {output}")
        click.echo(f"  {len(asm_def.channels)} DSL channels, {n_channels} named channels total")

    except Exception as exc:
        click.echo(f"✗ Error: {exc}", err=True)
        sys.exit(1)

@main.command("analyze-evolution")
@click.argument("baseline", type=click.Path(exists=True, path_type=Path))
@click.argument("snapshots", nargs=-1, type=click.Path(exists=True, path_type=Path), required=True)
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output markdown report path. Defaults to evolution-report.md in current directory.",
)
@click.option(
    "--min-occurrences", "-n",
    type=int,
    default=3,
    show_default=True,
    help="Minimum occurrences to flag a pattern.",
)
def analyze_evolution(
    baseline: Path,
    snapshots: tuple[Path, ...],
    output: Path | None,
    min_occurrences: int,
):
    """Analyse how snapshots have evolved relative to a baseline.

    BASELINE is the starting Sunday Starter snapshot.
    SNAPSHOTS are one or more post-service .snap files to compare against it.

    Produces a markdown report of significant per-snapshot changes and
    recurring patterns worth promoting into the template.
    """
    if output is None:
        output = Path("evolution-report.md")

    try:
        click.echo(f"Baseline: {baseline.name}")
        click.echo(f"Analysing {len(snapshots)} snapshot(s)...")

        diffs = []
        for snap_path in sorted(snapshots):
            sd = diff_snapshots(baseline, snap_path)
            sig = len(sd.significant_channel_diffs)
            click.echo(f"  {snap_path.name}: {sig} channel(s) with significant changes")
            diffs.append(sd)

        patterns = find_patterns(diffs, min_occurrences=min_occurrences)
        click.echo(f"\nPatterns found: {len(patterns)} (threshold: {min_occurrences}+)")

        report = render_report(
            base_name=baseline.name,
            diffs=diffs,
            patterns=patterns,
            min_occurrences=min_occurrences,
        )

        output.write_text(report)
        click.echo(f"\n✓ Report written to {output}")

    except Exception as exc:
        click.echo(f"✗ Error: {exc}", err=True)
        import traceback; traceback.print_exc()
        sys.exit(1)
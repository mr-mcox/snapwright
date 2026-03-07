"""Snapwright CLI."""

import sys
from pathlib import Path

import click

from snapwright.dsl.renderer import render_assembly


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

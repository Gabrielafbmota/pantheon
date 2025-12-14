"""AtlasForge CLI - Main entry point."""

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from atlasforge import __version__
from atlasforge.application.use_cases.generate_project import GenerateProjectUseCase
from atlasforge.domain.entities.project_spec import ProjectSpec
from atlasforge.domain.exceptions.base import AtlasForgeException
from atlasforge.domain.exceptions.generation import GenerationException
from atlasforge.domain.exceptions.validation import ValidationException
from atlasforge.domain.value_objects.module_name import ModuleName
from atlasforge.domain.value_objects.project_name import ProjectName
from atlasforge.domain.value_objects.template_version import TemplateVersion
from atlasforge.infrastructure.checksum.sha256_checksum import SHA256ChecksumAdapter
from atlasforge.infrastructure.filesystem.local_filesystem_adapter import (
    LocalFileSystemAdapter,
)
from atlasforge.infrastructure.persistence.json_manifest_repository import (
    JSONManifestRepository,
)
from atlasforge.infrastructure.templating.jinja2_engine import Jinja2TemplateEngine

app = typer.Typer(
    name="atlasforge",
    help="Zero-click backend project generator for Atlas Platform",
    add_completion=False,
    rich_markup_mode=None,
)
console = Console()


def _get_templates_dir() -> Path:
    """Get templates directory path."""
    # Assume we're in src/atlasforge/presentation/cli/main.py
    # Templates are at src/atlasforge/templates
    cli_file = Path(__file__)
    atlasforge_root = cli_file.parent.parent.parent
    return atlasforge_root / "templates"


def _create_use_case() -> GenerateProjectUseCase:
    """Create GenerateProjectUseCase with all dependencies."""
    templates_dir = _get_templates_dir()
    filesystem = LocalFileSystemAdapter()
    template_engine = Jinja2TemplateEngine(templates_dir)
    checksum = SHA256ChecksumAdapter()
    manifest_repo = JSONManifestRepository(filesystem)

    return GenerateProjectUseCase(
        filesystem=filesystem,
        template_engine=template_engine,
        checksum=checksum,
        manifest_repo=manifest_repo,
    )


@app.command()
def version() -> None:
    """Show AtlasForge version."""
    console.print(f"[bold green]AtlasForge[/bold green] version {__version__}")


@app.command()
def generate(
    project_name: Annotated[str, typer.Argument(help="Name of the project to generate")],
    modules: Annotated[str, typer.Option(help="Comma-separated list of modules (mongo,otel,events)")] = "",
    output: Annotated[str, typer.Option(help="Output directory")] = ".",
    template_version: Annotated[str, typer.Option(help="Template version to use")] = "1.0.0",
) -> None:
    """Generate a new FastAPI project with Clean Architecture."""
    try:
        # Parse modules
        module_set: frozenset[ModuleName] = frozenset()
        if modules:
            module_list = [m.strip() for m in modules.split(",") if m.strip()]
            module_set = frozenset(ModuleName(m) for m in module_list)

        # Create ProjectSpec
        spec = ProjectSpec(
            project_name=ProjectName(project_name),
            template_version=TemplateVersion(template_version),
            modules=module_set,
        )

        # Display generation info
        console.print(
            Panel.fit(
                f"[bold cyan]Project:[/bold cyan] {project_name}\n"
                f"[bold cyan]Modules:[/bold cyan] {', '.join(m.value for m in module_set) or 'none'}\n"
                f"[bold cyan]Output:[/bold cyan] {output}\n"
                f"[bold cyan]Template:[/bold cyan] {template_version}",
                title="[bold green]AtlasForge Generation[/bold green]",
                border_style="green",
            )
        )

        # Create use case and execute
        use_case = _create_use_case()
        target_dir = Path(output).resolve()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating project...", total=None)
            result = use_case.execute(spec, target_dir)
            progress.update(task, completed=True)

        # Display results
        if result.success:
            console.print()
            console.print(
                Panel.fit(
                    f"[bold green]✓[/bold green] Project created successfully!\n\n"
                    f"[bold]Location:[/bold] {result.project_path}\n"
                    f"[bold]Files created:[/bold] {result.total_files}\n"
                    f"[bold]Duration:[/bold] {result.duration_seconds:.2f}s\n"
                    f"[bold]Correlation ID:[/bold] {result.correlation_id}",
                    title="[bold green]Success[/bold green]",
                    border_style="green",
                )
            )

            # Show next steps
            console.print("\n[bold cyan]Next steps:[/bold cyan]")
            console.print(f"  cd {result.project_path.name}")
            console.print("  poetry install")
            console.print("  poetry run uvicorn src.{}.presentation.api.main:app --reload".format(
                spec.project_name.to_snake_case()
            ))
        else:
            console.print()
            console.print(
                Panel.fit(
                    f"[bold red]✗[/bold red] Generation failed\n\n"
                    f"[bold]Errors:[/bold]\n" + "\n".join(f"  • {e}" for e in result.errors),
                    title="[bold red]Error[/bold red]",
                    border_style="red",
                )
            )
            sys.exit(1)

    except ValidationException as e:
        console.print(f"[bold red]Validation Error:[/bold red] {e}")
        sys.exit(1)
    except GenerationException as e:
        console.print(f"[bold red]Generation Error:[/bold red] {e}")
        sys.exit(1)
    except AtlasForgeException as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def validate(
    project_path: Annotated[str, typer.Argument(help="Path to project to validate")] = ".",
) -> None:
    """Validate a project against its manifest."""
    try:
        path = Path(project_path).resolve()
        filesystem = LocalFileSystemAdapter()
        manifest_repo = JSONManifestRepository(filesystem)
        checksum_adapter = SHA256ChecksumAdapter()

        console.print(f"[bold cyan]Validating project:[/bold cyan] {path}")

        # Load manifest
        if not manifest_repo.exists(path):
            console.print("[bold red]Error:[/bold red] No manifest found. Not an AtlasForge project?")
            sys.exit(1)

        manifest = manifest_repo.load(path)
        console.print(f"[bold green]✓[/bold green] Manifest loaded: {manifest.template_name} v{manifest.template_version}")

        # Validate files
        issues = []
        modified_files = []
        missing_files = []

        for file_path_str, managed_file in manifest.managed_files.items():
            full_path = path / file_path_str
            if not filesystem.exists(full_path):
                missing_files.append(file_path_str)
            else:
                content = filesystem.read_file(full_path)
                current_checksum = checksum_adapter.calculate(content)
                if not checksum_adapter.verify(content, managed_file.checksum):
                    modified_files.append((file_path_str, managed_file.is_user_editable))

        # Display results
        table = Table(title="Validation Results", show_header=True)
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="magenta")
        table.add_column("Status", style="green")

        table.add_row("Total managed files", str(len(manifest.managed_files)), "")
        table.add_row("Missing files", str(len(missing_files)), "❌" if missing_files else "✓")
        table.add_row("Modified files", str(len(modified_files)), "⚠️" if modified_files else "✓")

        console.print(table)

        # Show details
        if missing_files:
            console.print("\n[bold red]Missing files:[/bold red]")
            for f in missing_files:
                console.print(f"  • {f}")

        if modified_files:
            console.print("\n[bold yellow]Modified files:[/bold yellow]")
            for f, is_editable in modified_files:
                status = "[green](user-editable)[/green]" if is_editable else "[red](managed)[/red]"
                console.print(f"  • {f} {status}")

        if not missing_files and not modified_files:
            console.print("\n[bold green]✓ Project is valid and unmodified[/bold green]")
        elif missing_files:
            console.print("\n[bold red]✗ Validation failed: missing files[/bold red]")
            sys.exit(1)

    except AtlasForgeException as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def inspect(
    project_path: Annotated[str, typer.Argument(help="Path to project to inspect")] = ".",
) -> None:
    """Inspect project manifest and show details."""
    try:
        path = Path(project_path).resolve()
        filesystem = LocalFileSystemAdapter()
        manifest_repo = JSONManifestRepository(filesystem)

        console.print(f"[bold cyan]Inspecting project:[/bold cyan] {path}\n")

        # Load manifest
        if not manifest_repo.exists(path):
            console.print("[bold red]Error:[/bold red] No manifest found. Not an AtlasForge project?")
            sys.exit(1)

        manifest = manifest_repo.load(path)

        # Display manifest info
        info_panel = Panel.fit(
            f"[bold]Template:[/bold] {manifest.template_name}\n"
            f"[bold]Version:[/bold] {manifest.template_version}\n"
            f"[bold]Modules:[/bold] {', '.join(manifest.modules_enabled) or 'none'}\n"
            f"[bold]Generated:[/bold] {manifest.generated_at}\n"
            f"[bold]Correlation ID:[/bold] {manifest.correlation_id}",
            title="[bold green]Manifest Details[/bold green]",
            border_style="green",
        )
        console.print(info_panel)

        # Display managed files
        console.print("\n[bold cyan]Managed Files:[/bold cyan]")
        table = Table(show_header=True)
        table.add_column("File", style="cyan")
        table.add_column("Source", style="magenta")
        table.add_column("Checksum", style="yellow")
        table.add_column("Editable", style="green")

        for file_path_str, managed_file in sorted(manifest.managed_files.items()):
            table.add_row(
                file_path_str,
                managed_file.source,
                managed_file.checksum.short_form(),
                "✓" if managed_file.is_user_editable else "✗",
            )

        console.print(table)

        # Display upgrade history if any
        if manifest.upgrade_history:
            console.print("\n[bold cyan]Upgrade History:[/bold cyan]")
            for i, upgrade in enumerate(manifest.upgrade_history, 1):
                console.print(f"  {i}. {upgrade}")

    except AtlasForgeException as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()

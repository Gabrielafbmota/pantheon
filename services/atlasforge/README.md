# AtlasForge

**Zero-click backend project generator for the Atlas Platform**

AtlasForge generates production-ready FastAPI projects with Clean Architecture, complete with:
- Modular capabilities (MongoDB, OTEL, Events, Auth, Jobs)
- Integrated quality gates (Aegis)
- Knowledge management (Mnemosyne)
- Observability (EyeOfHorusOps)
- Safe upgrade mechanism with conflict detection

## Installation

```bash
cd services/atlasforge
poetry install
```

## Usage

```bash
# Generate a new project
atlasforge generate my-service --modules mongo,otel

# Upgrade existing project
atlasforge upgrade --dry-run

# Add module to existing project
atlasforge module add events

# Validate project structure
atlasforge validate
```

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Type checking
poetry run mypy src/

# Linting
poetry run ruff check src/

# Format code
poetry run black src/
```

## Architecture

AtlasForge follows Clean Architecture with 4 layers:
- **Domain**: Pure business logic (entities, value objects, ports)
- **Application**: Use cases and orchestration
- **Infrastructure**: External adapters (filesystem, templates, etc.)
- **Presentation**: CLI interface

## Status

**MVP0** - Initial implementation in progress

For detailed documentation, see `docs/`.

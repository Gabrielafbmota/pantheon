# AtlasForge

**Zero-click backend project generator for the Atlas Platform**

[![Tests](https://img.shields.io/badge/tests-70%20passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-54%25-yellow)]()
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)]()
[![Status](https://img.shields.io/badge/status-MVP0.9-orange)]()

AtlasForge generates production-ready FastAPI projects with Clean Architecture in seconds.

## ✨ Features

- ✅ **Zero-click generation** - Complete FastAPI projects with one command
- ✅ **Clean Architecture** - 4 layers (domain/application/infrastructure/presentation)
- ✅ **Production-ready** - Docker, tests, health checks included
- ✅ **Manifest tracking** - SHA256 checksums for all files
- ✅ **Idempotent** - Same input → same output, guaranteed
- ✅ **Modular** - MongoDB, OTEL, Events, Auth e Jobs
- 📝 **Documented** - README, tests, API docs auto-generated

## 🚀 Quick Start

### Installation (Global)

Install AtlasForge globally to use from anywhere:

```bash
# Method 1: Using the install script (recommended)
./install.sh

# Method 2: Using Make
make install-global

# Method 3: Using pipx directly
pipx install .
```

Verify installation:
```bash
atlasforge version
# Output: AtlasForge version 1.0.0
```

### Installation (Development)

For local development:

```bash
# Install with Poetry
poetry install

# Or using Make
make install-dev
```

### Generate Your First Project

```bash
# Generate a new FastAPI service
atlasforge generate my-service

# Generate in specific directory
atlasforge generate my-service --output /tmp

# With modules
atlasforge generate my-service --modules mongo,otel
# Additional modules: events, auth, jobs
```

This creates:
```
my-service/
├── src/my_service/         # Clean Architecture layers
│   ├── domain/             # Business logic
│   ├── application/        # Use cases
│   ├── infrastructure/     # Adapters
│   └── presentation/       # FastAPI API
├── tests/                  # Tests included
├── Dockerfile              # Container ready
├── pyproject.toml          # Poetry config
└── .atlasforge/
    └── manifest.json       # File tracking
```

### Run Your Project

```bash
cd my-service
poetry install
poetry run uvicorn src.my_service.presentation.api.main:app --reload
```

Visit: `http://localhost:8000`

## 📚 Documentation

- **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** - Complete usage guide and architecture
- **[FEATURE_ANALYSIS.md](./FEATURE_ANALYSIS.md)** - Feature completion status
- **[Makefile](./Makefile)** - All available commands

## 🛠️ CLI Commands

```bash
# Show version
atlasforge version

# Generate new project
atlasforge generate <name> [OPTIONS]
  --modules TEXT       Comma-separated modules (mongo,otel,events)
  --output TEXT        Output directory (default: current)
  --template-version   Template version (default: 1.0.0)

# Validate project against manifest
atlasforge validate [PATH]

# Inspect project manifest
atlasforge inspect [PATH]

# Show help
atlasforge --help
```

## 🧪 Testing

```bash
# Run all tests (70 tests)
make test

# Run with coverage
make test-cov

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration
```

**Test Results**: 70/70 passing ✅

## 🏗️ Architecture

AtlasForge follows Clean Architecture with strict layer separation:

```
src/atlasforge/
├── domain/              # Pure business logic
│   ├── entities/        # ProjectSpec, TemplateManifest, Module
│   ├── value_objects/   # ProjectName, ModuleName, Checksum, etc.
│   ├── ports/           # Interfaces (Dependency Inversion)
│   └── services/        # ConflictDetector, ModuleResolver
├── application/         # Use cases
│   └── use_cases/       # GenerateProjectUseCase
├── infrastructure/      # External adapters
│   ├── filesystem/      # LocalFileSystemAdapter
│   ├── templating/      # Jinja2TemplateEngine
│   ├── checksum/        # SHA256ChecksumAdapter
│   └── persistence/     # JSONManifestRepository
├── presentation/        # CLI interface
│   └── cli/             # Typer + Rich
└── templates/           # Jinja2 templates
    └── base/            # Base FastAPI template
```

**Principles**:
- Immutability (frozen dataclasses)
- Self-validation (value objects)
- Dependency Inversion (ports & adapters)
- Idempotency (deterministic generation)

## 📊 Status

**Current Version**: 1.0.0 (MVP0.9)
**Completeness**: 65%

### Implemented ✅
- Core project generation
- Clean Architecture structure
- CLI with 4 commands
- Manifest tracking with checksums
- Idempotent generation
- Global installation (pipx)
- 70 tests (100% passing)

### In Progress 🚧
- Module system (mongo, otel, events, auth, jobs)

### Planned 📝
- Safe upgrade mechanism with dry-run
- Platform integrations (Aegis, Mnemosyne, EyeOfHorusOps)
- API FastAPI (optional, for remote generation)

See [FEATURE_ANALYSIS.md](./FEATURE_ANALYSIS.md) for detailed status.

## 🔧 Development

### Available Make Commands

```bash
make help              # Show all commands
make install          # Install dependencies
make install-global   # Install globally with pipx
make test             # Run tests
make test-cov         # Run tests with coverage
make lint             # Run linter
make format           # Format code
make type-check       # Run type checking
make quality          # Run all quality checks
make clean            # Clean build artifacts
make demo             # Generate demo project
```

### Quality Standards

```bash
# Linting
make lint             # or: poetry run ruff check src/

# Formatting
make format           # or: poetry run black src/

# Type checking
make type-check       # or: poetry run mypy src/

# All checks
make quality
```

## 🤝 Contributing

1. Create branch: `feat/<area>/<description>`
2. Implement with tests (min 80% coverage)
3. Run quality checks: `make quality`
4. Run tests: `make test`
5. Commit: `<scope>: <action>`

Example:
```bash
git checkout -b feat/modules/add-mongo-template
# ... implement ...
make quality && make test
git commit -m "modules: add MongoDB template with connection pool"
```

## 📄 Project Structure

```
services/atlasforge/
├── src/atlasforge/          # Source code
├── tests/                   # Tests (unit + integration)
├── pyproject.toml           # Poetry config
├── Makefile                 # Development commands
├── install.sh               # Global installation script
├── README.md                # This file
├── IMPLEMENTATION.md        # Complete guide
└── FEATURE_ANALYSIS.md      # Feature status
```

## 🔗 Related Documentation

- **CLAUDE.md** - Platform instructions at repo root
- **docs/** - Architecture and planning docs
- **.claude/prompts/atlasforge.md** - Original prompt

## 📝 License

Part of the Atlas Platform - Internal development platform

---

**Generated with ❤️ by the Atlas Platform Team**

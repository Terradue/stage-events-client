# Develop and regenerate the client

Run commands from the repository root. Use Python 3.10 or newer and Hatch for
the configured quality environments. Model and OpenAPI generation additionally
use the `task` executable and remote Terradue task definitions, `uv` for model
generation, and Node.js with `npx` for OpenAPI bundling and HTML generation.

## Install and verify a checkout

For an editable installation in your own virtual environment:

```console
python -m pip install -e '.[cli]'
```

Hatch manages its own environments. Run the non-mutating checks before submitting
a change:

```console
hatch run dev:format-check
hatch run dev:lint-check
hatch run dev:typecheck
hatch run dev:security
hatch run test:test
```

The test environment has a Python 3.10–3.14 matrix. To select an installed
interpreter explicitly, use a matrix environment such as
`hatch run test.py3.10:test`. Use `hatch run test:test-cov` for coverage.
`hatch run dev:check` combines formatting verification, lint, typing, security,
and tests in the development environment. `hatch run dev:fix` changes source
files; inspect its diff before committing.

## Change an event contract

Read `AGENTS.md` and `Taskfile.yaml` before editing. Modify the authoritative
`schemas/openapi.yaml`, including descriptions and validation constraints, then
run these commands in order:

```console
task generate_openapi_doc
task generate_models
```

The first task refreshes both the bundled schema and HTML reference. The second
uses that bundle as input to `json:create_models`, writes
`src/stage_events_client/models.py`, and runs the configured Ruff fixes.
It does not first refresh the schema bundle, so do not skip the first command
after changing the source schema.

This repository does not pass a custom base class, additional imports, or custom
templates to `create_models`; the shared task supplies generation options.
The local `tool.datamodel-codegen` configuration preserves the license header.
Remote task includes and external schema references require network access and
may prompt for Task's remote-file trust on first use.

Do not edit generated classes or hand-write replacement models for the same
contract. Update application usage, relevant regression tests, and reference
documentation, then rerun the quality checks. Review the generated diff for
changes caused by shared schemas as well as your own edits.

`generate_client_archetype` is a broader scaffolding operation that regenerates
the client and removes a generated models directory. It is not the routine
command for a model-only change.

## Preview and build documentation

The documentation uses MkDocs with its built-in Read the Docs theme. Install
the same MkDocs version constraint used by the documentation workflow:

```console
python -m pip install 'mkdocs<=2.0.0'
mkdocs serve
```

Open the local URL printed by MkDocs. Build without publishing:

```console
mkdocs build --strict --site-dir /tmp/stage-events-client-docs
```

Keep pages in the appropriate Diátaxis section: guided learning in tutorials,
task instructions in how-to guides, interface facts in reference, and design
reasoning in explanation. Add new pages to `mkdocs.yaml` and link related pages.
Retain the existing `cli.md` and `python-api.md` paths for inbound links.

The docs workflow publishes on pushes to `develop`, `main`, or `master` when its
configured documentation paths change. A local build does not publish the site.

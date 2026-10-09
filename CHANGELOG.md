# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.2.0] - 2026-10-09

### Fixed

- Added missing `specversion` and `datacontenttype` [CloudEvents](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md) fields

## [1.1.0] - 2026-10-02

### Changed

- Improved type annotations and internal code quality by addressing mypy, Ruff, and Bandit findings.

## [1.0.5] - 2026-07-30

### Added

- Stronger code chekers with Ruff+McCabe & Bandit.

### Changed

- Dependencies bump
  - `eoap-problems-registry` to `1.3.0`.
  - `httpx` to `0.28.1`.
  - `typing-extensions` to `4.16.0`.

## [1.0.4] - 2026-07-26

### Changed

- Bump `eoap-problems-registry` dependency >= to `1.2.0`.

### Fixed

- New `ruff` checks

## [1.0.3] - 2026-07-23

### Changed

- Bump `eoap-problems-registry` dependency to `1.1.0`.

## [1.0.2] - 2026-07-20

### Changed

- Bump `eoap-problems-registry` dependency to `1.0.1`.

## [1.0.1] - 2026-07-20

### Fixed

- Generated models solve Pydantic/Pylance [issue](https://github.com/pydantic/pydantic/discussions/7379).

## [1.0.0] - 2026-07-17

### Added

- Initial version

[Unreleased]: https://github.com/Terradue/stage-events-client/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/Terradue/stage-events-client/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Terradue/stage-events-client/compare/v1.0.5...v1.1.0
[1.0.5]: https://github.com/Terradue/stage-events-client/compare/v1.0.4...v1.0.5
[1.0.4]: https://github.com/Terradue/stage-events-client/compare/v1.0.3...v1.0.4
[1.0.3]: https://github.com/Terradue/stage-events-client/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/Terradue/stage-events-client/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/Terradue/stage-events-client/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Terradue/stage-events-client/releases/tag/v1.0.0

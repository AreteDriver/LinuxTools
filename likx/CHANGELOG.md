# Changelog

All notable changes to LikX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CONTRIBUTING.md with contribution guidelines
- CodeQL security scanning workflow
- Issue and PR templates
- Pre-commit hooks configuration
- Dependabot for automated dependency updates

### Changed
- Refactored `_on_key_press` complexity from 75 to 30 using dispatch tables

## [3.30.0] - 2026-01-25

### Added
- Minimap panel for document navigation and overview
- Onboarding tooltips for first-time users
- Quick actions toolbar for common operations
- Undo history panel with visual timeline
- Capture queue for batch processing
- System tray integration

### Fixed
- Security: Replaced `tempfile.mktemp()` with `tempfile.mkstemp()` to prevent race condition vulnerabilities

### Changed
- Expanded test coverage (300+ new tests across 8 modules)

## [3.29.0] - 2026-01-19

### Added
- Hexagonal honeycomb color picker in toolbar
- Inline hex color input for custom colors
- Expanded test coverage for scroll_capture, overlays, tray, config, and queue modules

### Changed
- Updated dependency minimum versions

## [3.28.0] - 2026-01-18

### Added
- Quick toolbar for common actions
- Template system for annotations
- Color palettes
- Video recording support

## [3.27.0] - 2026-01-17

### Added
- GNOME HeaderBar style UI redesign
- Compact stacked layout
- Single instance lock (prevents multiple windows)
- Window opacity slider

### Changed
- MainWindow redesigned to match GNOME Screenshot style
- Reduced default window size

## [3.26.1] - 2026-01-16

### Fixed
- AppDir sync with source files
- Build script updates

## [3.26.0] - 2026-01-15

### Added
- Tabbed captures for managing multiple screenshots
- Improved window visibility controls
- 40 new tests for effects and pinned modules

### Changed
- Lazy-load numpy/opencv for 95% startup time improvement

## [3.25.0] - 2026-01-14

### Added
- AUR package support
- CLI entry point (`likx` command)
- Type safety improvements
- Enhanced hotkey system

### Changed
- Polished README with install options and comparison table

## [3.24.0] - 2026-01-13

### Added
- Italian translation
- Russian translation
- Japanese translation
- Advanced GIF quality options in settings UI

## [3.23.0] - 2026-01-12

### Added
- Internationalization (i18n) support
- Spanish translation
- French translation
- German translation
- Portuguese translation
- Multi-monitor support with quick-select (1-9 keys)
- Keyboard shortcut customization UI
- Wayland support for scroll capture

## [3.22.0] - 2026-01-11

### Added
- Editor settings tab with grid size slider
- Measure tool with angle display and axis-aligned extensions
- Expanded stamp presets with arrows and shapes
- Opacity/transparency control (Shift+[ / Shift+])
- Rotation tool (Ctrl+R / Ctrl+Shift+R)
- Element transform tools (flip, lock, grid snap, match size)
- Duplicate shortcut (Ctrl+D)
- Layer ordering (bring to front / send to back)
- Recent colors palette
- Copy/paste for annotations
- Coverage reporting with Codecov

## [3.21.0] - 2026-01-10

### Added
- Cloud upload support (Imgur, S3, Dropbox, Google Drive)
- GIF screen recording
- Scrolling screenshot capture
- Flatpak packaging support

## [3.11.0] - 2026-01-09

### Added
- Multi-select for annotations (Ctrl+click, drag selection)
- Resize handles with cursor feedback
- Keyboard nudge for selected elements

## [3.10.0] - 2026-01-08

### Added
- Resize handle tests
- Improved cursor feedback during resize operations

## [3.9.0] - 2026-01-07

### Added
- Selection tool for moving and resizing annotations
- Arrow styles (open, filled, double-headed)
- Text formatting (bold, italic, font selection)
- Snap-to-alignment guides

## [3.3.0] - 2026-01-06

### Added
- Zoom tool for detailed work
- Additional annotation tool improvements

## [3.2.0] - 2026-01-06

### Added
- Measure tool for pixel distance measurement

## [3.1.0] - 2026-01-06

### Added
- Command Palette (Ctrl+Shift+P)
- Radial menu (right-click)

## [3.0.0] - 2026-01-06

### Added
- Initial LikX release (renamed from Linux_SnipTool)
- **Capture modes**: Fullscreen, region, window
- **Display support**: X11 and Wayland (GNOME, KDE, Sway)
- **Annotation tools**: Pen, highlighter, line, arrow, rectangle, ellipse, text, blur, pixelate, number markers
- **OCR**: Text extraction via Tesseract
- **Pin to desktop**: Keep screenshots visible while working
- **Visual effects**: Shadow, border, background, rounded corners
- **Cloud upload**: Imgur integration
- **History browser**: Visual thumbnail browser
- **Distribution**: Snap Store, AppImage, Debian .deb

---

For detailed changes, see the [commit history](https://github.com/AreteDriver/LikX/commits/main).

[Unreleased]: https://github.com/AreteDriver/LikX/compare/v3.30.0...HEAD
[3.30.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.30.0
[3.29.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.29.0
[3.28.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.28.0
[3.27.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.27.0
[3.26.1]: https://github.com/AreteDriver/LikX/releases/tag/v3.26.1
[3.26.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.26.0
[3.25.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.25.0
[3.24.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.24.0
[3.23.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.23.0
[3.22.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.22.0
[3.21.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.21.0
[3.11.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.11.0
[3.10.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.10.0
[3.9.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.9.0
[3.3.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.3.0
[3.2.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.2.0
[3.1.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.1.0
[3.0.0]: https://github.com/AreteDriver/LikX/releases/tag/v3.0.0

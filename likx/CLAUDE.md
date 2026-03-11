# CLAUDE.md — LikX

## Project Overview

GTK3/Python screenshot capture and annotation tool for Linux with OCR, cloud upload, GIF recording, and scrolling screenshots. Part of the LinuxTools monorepo.

## Current State

- **Version**: 3.31.0 (3.31.1 tagged, release blocked — see Known Issues)
- **Tests**: 1,752 (pytest, all passing)
- **Coverage**: ~80%
- **CI**: GitHub Actions (lint, test, build, CodeQL)
- **Packaging**: AppImage, .deb, Snap, Flatpak, PyPI (`pip install likx`)

## Architecture

```
likx/
├── main.py                    ← Entry point + CLI (argparse)
├── src/
│   ├── __init__.py            ← Version string
│   ├── capture.py             ← Screenshot capture (X11 via Gdk, Wayland via grim/gnome-screenshot/spectacle)
│   ├── editor.py              ← Annotation editor (cairo drawing, tool dispatch)
│   ├── ui.py                  ← Main window, toolbar, dialogs
│   ├── config.py              ← User settings (~/.config/likx/config.json)
│   ├── ocr.py                 ← Tesseract OCR integration
│   ├── effects.py             ← Shadow, border, rounded corners, brightness/contrast, grayscale, invert
│   ├── uploader.py            ← Cloud upload (Imgur, S3, Dropbox, Google Drive)
│   ├── recorder.py            ← GIF/MP4/WebM recording (ffmpeg/wf-recorder)
│   ├── recording_overlay.py   ← Recording progress UI
│   ├── scroll_capture.py      ← Scrolling screenshots (OpenCV template matching)
│   ├── scroll_overlay.py      ← Scroll capture progress UI
│   ├── pinned.py              ← Pin-to-desktop floating window
│   ├── hotkeys.py             ← Global keyboard shortcuts (GNOME gsettings)
│   ├── command_palette.py     ← Ctrl+Shift+P searchable command interface
│   ├── commands.py            ← Command registry for palette
│   ├── radial_menu.py         ← Right-click radial tool selector
│   ├── clipboard.py           ← Clipboard operations
│   ├── notification.py        ← Desktop notifications
│   ├── i18n.py                ← Internationalization (gettext, 8 languages)
│   ├── history.py             ← Capture history with thumbnails
│   ├── queue.py               ← Capture queue management
│   ├── onboarding.py          ← First-run onboarding
│   ├── tray.py                ← System tray icon
│   ├── quick_actions.py       ← Quick action toolbar
│   ├── minimap.py             ← Minimap navigation widget
│   ├── undo_history.py        ← Undo/redo stack
│   ├── ui_enhanced.py         ← Enhanced UI components
│   ├── mixins/
│   │   ├── drawing_mixin.py   ← Drawing tool logic (extracted from editor)
│   │   ├── input_mixin.py     ← Mouse/input event handling
│   │   ├── keyboard_mixin.py  ← Keyboard shortcut dispatch
│   │   └── ui_setup_mixin.py  ← UI initialization
│   ├── widgets/
│   │   ├── save_handler.py    ← Save dialog and file operations
│   │   ├── color_picker.py    ← Color selection widget
│   │   └── tab_manager.py     ← Tab management
│   └── dialogs/
│       └── settings.py        ← Settings configuration dialog
├── tests/                     ← 1,752 tests
├── locale/                    ← Translations (en, es, fr, de, pt, it, ru, ja)
├── resources/icons/           ← App icons (SVG + PNG)
├── AppDir/                    ← AppImage packaging
├── debian/                    ← .deb packaging
├── snap/                      ← Snap packaging
└── scripts/                   ← Build/maintenance scripts
```

## Development Commands

```bash
# Run
python3 main.py                  # Launch GUI
python3 main.py --fullscreen     # Capture fullscreen immediately
python3 main.py --region         # Region capture mode
python3 main.py --window         # Active window capture
python3 main.py --delay 3        # 3-second delay before capture

# Test
pytest tests/ -v
pytest tests/ --cov=src/         # With coverage

# Lint (always run BOTH)
ruff check src/ tests/ main.py
ruff format src/ tests/ main.py

# Build
./build-appimage.sh              # AppImage
./build-deb.sh                   # Debian package
./build-flatpak.sh               # Flatpak
```

## Key Dependencies

### Runtime (system packages)
- `python3-gi` (PyGObject/GTK3)
- `gir1.2-gtk-3.0`
- `tesseract-ocr` (for OCR)
- `ffmpeg` (for GIF/video recording)
- `xdotool` (X11 window/scroll control)

### Runtime (pip)
- `pycairo>=1.27.0`
- `numpy>=1.26.0`
- `opencv-python-headless>=4.10.0`
- `pytesseract` (OCR bridge)

### Dev
- `pytest`, `pytest-cov`
- `ruff`

## Code Conventions

- **Python 3.9+** (per pyproject.toml `requires-python`)
- **snake_case** naming throughout
- **Type hints** encouraged on all public functions
- **GTK signal handlers**: `_on_<widget>_<signal>`
- **Settings**: always go through `src/config.py`
- **User-visible strings**: wrap with `_()` for translation (`from src.i18n import _`)
- **Logging**: use `logging` module, not `print()`
- **Paths**: use `pathlib.Path`, not `os.path`
- **Temp files**: use `tempfile.mkstemp()`, not predictable paths
- **Pixbuf from cairo surface**: always `bytes(surface.get_data())` to avoid dangling reference

## Keyboard Shortcuts

### Editor
| Key | Tool |
|-----|------|
| `V` | Select (move/resize, Shift=lock aspect) |
| `P` | Pen |
| `H` | Highlighter |
| `L` | Line |
| `A` | Arrow (open/filled/double) |
| `R` | Rectangle |
| `E` | Ellipse |
| `T` | Text (bold/italic/font from toolbar) |
| `B` | Blur |
| `X` | Pixelate |
| `M` | Measure |
| `N` | Number marker |
| `I` | Color picker (eyedropper) |
| `S` | Stamp |
| `Z` | Zoom |
| `K` | Callout/speech bubble |
| `C` | Crop (Shift for 1:1) |
| `G` | GIF recording |
| Right-click | Radial menu |

### Modifiers
| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+P` | Command Palette |
| `Ctrl+S` | Save |
| `Ctrl+Z` / `Ctrl+Y` | Undo / Redo |
| `Ctrl+C` / `Ctrl+V` | Copy / Paste annotations |
| `Ctrl+D` | Duplicate selected |
| `Ctrl+G` / `Ctrl+Shift+G` | Group / Ungroup |
| `Ctrl+]` / `Ctrl+[` | Bring to front / Send to back |
| `Ctrl+R` / `Ctrl+Shift+R` | Rotate CW / CCW 90deg |
| `Ctrl+Shift+F` / `Ctrl+Alt+F` | Flip horizontal / vertical |
| `Ctrl+L` | Lock/unlock selected |
| `Ctrl+'` | Toggle grid snap |
| `Shift+]` / `Shift+[` | Increase / Decrease opacity 10% |
| `Arrow` / `Shift+Arrow` | Nudge 1px / 10px |
| `+` / `-` / `0` | Zoom in / out / reset |
| `Delete` | Delete selected |
| `Shift+Click` | Multi-select toggle |

### Alignment (2+ elements selected)
`Ctrl+Alt+` L/R/T/B/C/M = Left/Right/Top/Bottom/Center-H/Center-V
`Ctrl+Shift+` H/J = Distribute horizontal/vertical (3+ elements)
`Ctrl+Alt+` W/E/S = Match width/height/size to first selected

### Global Hotkeys (configurable via GNOME gsettings)
| Shortcut | Action |
|----------|--------|
| `Super+Print` | Fullscreen capture |
| `Super+Shift+S` | Region capture |
| `Super+Shift+W` | Window capture |
| `Ctrl+Alt+G` | Record GIF |
| `Ctrl+Alt+S` | Scrolling screenshot |

## Internationalization

- Translation function: `from src.i18n import _`
- Template: `locale/likx.pot`
- Languages: en, es, fr, de, pt, it, ru, ja
- Extract: `./scripts/extract_strings.sh`
- Compile: `msgfmt locale/<lang>/LC_MESSAGES/likx.po -o locale/<lang>/LC_MESSAGES/likx.mo`

## Known Issues

### PyPI Trusted Publisher Mismatch (v3.31.1 release blocked)
The `publish-pypi` job fails because PyPI trusted publisher still points to the old standalone `LikX` repo. Fix: update trusted publisher on pypi.org to `AreteDriver/LinuxTools`, workflow `likx-release.yml`, environment `pypi`. Then re-tag or re-run.

### xclip Clipboard Hang (src/clipboard.py)
`_copy_x11_clipboard()` uses fire-and-forget `Popen()` with **no timeout**. xclip holds the X selection open until another app reads it — if nothing reads, the process hangs indefinitely. This caused 3 stale processes stuck since the previous day. The Wayland path (`_copy_wayland_clipboard`) correctly uses `proc.wait(timeout=5)`. The X11 path needs the same treatment.

## Known Gotchas

- `GdkPixbuf.new_from_data()` holds a reference to the data buffer — if the source (cairo surface) is GC'd, the pixbuf becomes invalid. Always copy with `bytes(surface.get_data())` first.
- GTK3 is single-threaded — all UI updates must happen on the main thread via `GLib.idle_add()`
- Wayland capture requires external tools (grim, gnome-screenshot, spectacle) since there's no direct screen grab API
- `subprocess.run()` without `timeout` can hang the UI — always set timeouts
- `_copy_x11_clipboard()` xclip Popen has no timeout — can hang indefinitely (see Known Issues)
- Scroll capture overlap detection uses OpenCV template matching — false positives possible with repetitive content
- Temp files from xclip (`/tmp/likx_clip_*.png`) may accumulate if process is killed before cleanup

## Release Process

1. Update version in `src/__init__.py`, `debian/changelog`, `snap/snapcraft.yaml`, `build-*.sh`
2. Commit and tag: `git tag v3.31.0`
3. Push tag: `git push origin v3.31.0`
4. CI builds and uploads to GitHub Releases
5. Snap auto-publishes to Snap Store

## Changelog

### v3.31.0
- **PyPI distribution**: `pip install likx` (entry point: `main:main`)
- **Clipboard image paste**: Ctrl+V with no annotation clipboard pastes system clipboard image as new tab
- **Wayland region selector**: uses `slurp` natively on Wayland, falls back to GTK overlay
- **Release pipeline**: tag push builds .deb + AppImage + Snap + publishes to PyPI

### v3.31.1 (tagged, release blocked)
- Color persistence, KDE hotkeys, root CI workflows
- Release blocked by PyPI trusted publisher mismatch (see Known Issues)

## CI/CD

- **Root monorepo workflows** (`.github/workflows/likx-ci.yml`, `likx-release.yml`) — triggered by path filter `likx/**`
- **Sub-project workflows** (`likx/.github/workflows/`) — ci.yml, tests.yml, release.yml, codeql.yml
- **CI**: ruff check + format, pytest on Python 3.10/3.11/3.12 with xvfb, Codecov upload
- **Release**: tag `v*` → build .deb + AppImage → publish PyPI (trusted publisher) → GitHub Release
- **Security**: CodeQL scanning, dependabot (all 8 alerts resolved), gitleaks pre-commit
- **Code scanning**: Not enabled at root level (consider enabling)

## Anti-Patterns (Do NOT Do)

- Do NOT use `print()` for error reporting — use `logging` module
- Do NOT use `os.path` — use `pathlib.Path`
- Do NOT create temp files with predictable paths — use `tempfile.mkstemp()`
- Do NOT pass `surface.get_data()` directly to `Pixbuf.new_from_data()` — copy first
- Do NOT call GTK methods from background threads
- Do NOT use bare `except:` — catch specific exceptions

# CLAUDE.md — LinuxTools

> Collection of native Linux desktop utilities by AreteDriver.

---

## What Is LinuxTools?

A monorepo consolidating four standalone Linux utilities that solve real desktop problems with no existing good solutions. Each tool is independent but shares a common author, packaging approach, and quality standard.

**This is a monorepo.** Each tool lives in its own directory with its own dependencies and can be built/installed independently.

---

## Repository Structure

```
LinuxTools/
├── CLAUDE.md
├── README.md                  ← Portfolio overview of all tools
├── steam-proton/              ← SteamProtonHelper
│   ├── README.md
│   ├── pyproject.toml
│   ├── setup.py
│   ├── steam_proton_helper.py ← Single-file CLI + GUI tool
│   ├── CHANGELOG.md
│   ├── CONTRIBUTING.md
│   ├── .github/workflows/     ← CI/CD + PyPI publishing
│   └── completions/           ← bash/zsh/fish shell completions
├── likx/                      ← LikX screenshot tool
│   ├── README.md
│   ├── pyproject.toml
│   ├── src/                   ← GTK-based screenshot + OCR
│   ├── resources/             ← Icons, assets
│   ├── setup.sh
│   └── build-appimage.sh      ← AppImage packaging
├── g13/                       ← Logitech G13 Linux driver
│   ├── README.md
│   ├── pyproject.toml
│   ├── src/
│   │   ├── core/
│   │   │   ├── g13_driver.py  ← Hardware abstraction (evdev + hidraw)
│   │   │   ├── profiles.py    ← JSON profile management
│   │   │   └── actions.py     ← Action execution engine
│   │   └── gui/               ← Qt6 interface (in progress)
│   ├── configs/profiles/      ← Example profiles (EVE, DevOps, OBS)
│   ├── udev/                  ← 99-g13.rules for non-root access
│   └── systemd/               ← Optional daemon service
├── razer/                     ← Razer peripheral controls
│   ├── README.md
│   ├── pyproject.toml
│   └── src/
└── shared/                    ← Any common utilities (if needed)
```

---

## Tool Summaries

### steam-proton/ — SteamProtonHelper
**Status:** Production (v1.8.0, 9 releases, PyPI published, 44+ commits)
**What:** Diagnoses and fixes Steam/Proton gaming issues on Linux. CLI + GUI modes.
**Language:** Python (single-file, stdlib only — zero dependencies)
**Packaging:** PyPI (`pip install steam-proton-helper`), shell completions, GitHub Actions CI/CD
**Distro support:** Ubuntu, Fedora, Arch, SteamOS/Steam Deck
**Key features:** Auto-detect Steam install, verify Vulkan/32-bit libs, GE-Proton management, ProtonDB lookup, multi-distro package commands
**This is the most polished tool in the collection.** It sets the quality bar for the others.

### likx/ — LikX Screenshot Tool
**Status:** Functional (27+ commits, feature-complete, needs packaging)
**What:** Screenshot capture, annotation, and OCR for Linux desktops.
**Language:** Python/GTK
**Dependencies:** PyGObject, pycairo, pytesseract, Pillow
**Key differentiator:** Built-in OCR via Tesseract — no other Linux screenshot tool has this natively.
**Display support:** X11 + Wayland (GNOME, KDE, Sway)
**Features:** Region/window/fullscreen capture, annotations, pin-to-desktop, history browser, effects (shadow, border, rounded corners)
**Packaging gap:** No AppImage, Flatpak, or distro packages yet. This is the #1 priority for adoption.

### g13/ — Logitech G13 Linux Driver
**Status:** Alpha (core working, GUI in progress)
**What:** Native Linux userspace driver for Logitech G13 Advanced Gameboard. 25 programmable keys, RGB backlight, analog stick, LCD display.
**Language:** Python
**Dependencies:** evdev, hidraw, xdotool, Qt6 (for GUI)
**Architecture:**
```
Qt6 GUI Layer (profile editor, visual mapper, live monitoring)
    ↓
Application Logic (profiles, actions, auto-switch)
    ↓
Hardware Interface (evdev for keys, hidraw for RGB/LCD, xdotool for input sim)
    ↓
G13 Hardware (/dev/input)
```
**Profile system:** JSON-based with hot-swapping. Example profiles for EVE Online, DevOps, OBS streaming.
**Why this exists:** Logitech provides zero Linux support. Existing solutions (g13d) are unmaintained since 2016.
**udev rules:** Non-root device access via plugdev group.

### razer/ — Razer Controls
**Status:** Functional
**What:** Control interface for Razer peripherals on Linux.
**Language:** Python
**PyPI target:** `pip install razer-controls`

---

## Design Principles

1. **Each tool is independently installable.** No shared runtime dependency between tools. A user can install just LikX without pulling in G13 driver code.
2. **Python-first.** All tools are Python. This keeps the stack consistent and accessible.
3. **Packaging matters.** Every tool should have: pyproject.toml, CLI entry point, at least one distribution format (PyPI, AppImage, or distro package).
4. **Solve real problems.** Every tool exists because the existing solutions are missing, broken, or abandoned on Linux.
5. **README-driven development.** Each tool's README should explain the problem, show the solution, and get someone running in under 60 seconds.

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Monorepo vs separate | Monorepo | Same author, same quality bar, shared CI patterns. Reduces GitHub noise. |
| Language | Python for all | Consistent stack, largest Linux scripting ecosystem |
| GUI framework | GTK for LikX, Qt6 for G13 | GTK integrates better with GNOME (LikX's primary target). Qt6 has better widget support for G13's visual mapper. |
| Packaging | PyPI + AppImage | PyPI for developers, AppImage for desktop users |
| Config format | JSON | Human-readable, git-diffable, schema-validatable |

---

## Naming History

This monorepo consolidates four previously separate repositories:

| Current Path | Previous Repo Name |
|-------------|-------------------|
| steam-proton/ | SteamProtonHelper |
| likx/ | LikX (or Linux_SnipTool) |
| g13/ | G13_Linux (or G13LogitechOPS) |
| razer/ | Razer_Controls |

Old repo names may appear in commit history, issues, or external references.

---

## Development Priorities

1. **LikX AppImage build** — biggest impact for adoption. OCR is the killer feature but nobody can install it easily.
2. **G13 GUI completion** — Qt6 visual mapper and profile editor. Core driver works.
3. **Razer polish** — ensure pyproject.toml and CLI entry points are clean.
4. **steam-proton maintenance** — already production-grade, just keep it current.
5. **Top-level README** — portfolio showcase page linking all four tools with screenshots/GIFs.

---

## Build & Install (per tool)

```bash
# SteamProtonHelper (from PyPI)
pip install steam-proton-helper

# SteamProtonHelper (from source)
cd steam-proton/
pip install -e .

# LikX (from source)
cd likx/
./setup.sh

# G13 (from source)
cd g13/
pip install -e .
sudo cp udev/99-g13.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules

# Razer (from source)
cd razer/
pip install -e .
```

---

## CI/CD

steam-proton/ has GitHub Actions for testing and PyPI publishing. The other tools should follow the same pattern. CI workflow template:

- Lint (ruff or flake8)
- Type check (mypy)
- Test (pytest)
- Build package
- Publish on tag (PyPI or GitHub Release with AppImage)

---

## What NOT To Build

- **A unified GUI wrapper** — these tools serve different purposes. Don't force them into one app.
- **Cross-tool dependencies** — each tool must remain independently installable.
- **Snap packages** — Flatpak/AppImage are the priority. Snap adds Canonical lock-in complexity.
- **Windows/macOS ports** — these are Linux tools. That's the point.

---

## Related Projects

| Project | Relationship |
|---------|-------------|
| Animus | Personal AI exocortex. Could eventually provide voice/AI interface to these tools. |
| EVE_Collection | G13 profiles for EVE Online live in g13/configs/profiles/. |

# LinuxTools

**Native Linux desktop utilities that solve problems nobody else bothered to fix.**

A collection of four tools built out of frustration with missing or abandoned Linux software. Each one exists because the alternative was "use Windows," "run a VM," or "it doesn't work on Wayland."

---

## The Tools

### SteamProtonHelper

Diagnoses and fixes Steam/Proton gaming issues on Linux.

```bash
pip install steam-proton-helper
steam-proton-helper --check
```

Auto-detects your Steam installation, verifies Vulkan drivers and 32-bit libraries, manages GE-Proton versions, and looks up game compatibility on ProtonDB. Works on Ubuntu, Fedora, Arch, and SteamOS/Steam Deck. CLI and GUI modes. Zero dependencies — stdlib only.

**v1.8.0** · 9 releases · PyPI published · CI/CD pipeline · Shell completions (bash/zsh/fish)

---

### LikX

Screenshot capture, annotation, and OCR for Linux.

The only Linux screenshot tool with **built-in OCR**. Capture a region, extract the text, paste it somewhere. Flameshot can't do this. Ksnip can't do this. Shutter can't do this.

Full X11 + Wayland support (GNOME, KDE, Sway). Region/window/fullscreen capture, annotation tools, pin-to-desktop, history browser, effects (shadow, border, rounded corners).

**Python/GTK** · Tesseract OCR · Feature-complete, packaging in progress

---

### G13

Native Linux driver for the Logitech G13 Advanced Gameboard.

Logitech provides zero Linux support. The community alternative (g13d) has been unmaintained since 2016. This project provides a full userspace driver with 25 programmable keys, RGB backlight control, analog stick mapping, and a profile system with hot-swapping.

```
Qt6 GUI (profile editor, visual mapper, live monitoring)
    ↓
Application Logic (profiles, actions, auto-switch)
    ↓
Hardware Interface (evdev for keys, hidraw for RGB/LCD)
    ↓
G13 Hardware
```

JSON profiles for any use case — gaming (EVE Online fleet commands), development (CI/CD shortcuts), streaming (OBS scene control). Per-application auto-switching planned.

**Python** · evdev + hidraw · Qt6 GUI · Alpha (core working, GUI in progress)

---

### Razer Controls

Control interface for Razer peripherals on Linux.

**Python** · Functional

---

## Install

Each tool is independently installable. No shared dependencies between them.

```bash
# SteamProtonHelper (from PyPI — recommended)
pip install steam-proton-helper

# SteamProtonHelper (from source)
cd steam-proton/ && pip install -e .

# LikX
cd likx/ && ./setup.sh

# G13 (requires udev rules for non-root device access)
cd g13/ && pip install -e .
sudo cp udev/99-g13.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules

# Razer
cd razer/ && pip install -e .
```

---

## Repository Structure

```
LinuxTools/
├── steam-proton/     ← Production. PyPI published. CI/CD.
├── likx/             ← Feature-complete. OCR differentiator. Needs packaging.
├── g13/              ← Alpha. Core driver works. GUI in progress.
├── razer/            ← Functional.
└── shared/           ← Common utilities (if needed)
```

---

## Why a Monorepo?

These tools were originally separate repositories. They share a common author, language (Python), and quality standard — but they kept duplicating CI configs, packaging patterns, and documentation structure. Consolidating them reduces noise and lets portfolio visitors see the full scope of Linux desktop work in one place.

Each tool remains fully independent. Installing LikX doesn't pull in the G13 driver. The monorepo is an organizational choice, not an architectural coupling.

---

## Priorities

1. **LikX AppImage** — The OCR feature is a genuine differentiator, but nobody can install it easily yet. One-click packaging is the gate to adoption.
2. **G13 GUI** — Qt6 visual mapper and profile editor. The core driver works; the interface needs to catch up.
3. **Razer polish** — Clean pyproject.toml and CLI entry points.
4. **SteamProtonHelper maintenance** — Already production-grade. Keep dependencies current.

---

## Related Projects

| Project | Connection |
|---------|-----------|
| [EVE_Collection](https://github.com/AreteDriver/EVE_Collection) | G13 has EVE Online-specific key profiles. |
| [Animus](https://github.com/AreteDriver/Animus) | Potential future integration for voice-driven tool control. |

---

## License

MIT

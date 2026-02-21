# LinuxTools

**Native Linux desktop utilities that solve problems nobody else bothered to fix.**

---

## The Tools

| Tool | Language | Status |
|------|----------|--------|
| [g13](g13/) | Python | Logitech G13 Linux driver — macros, RGB, LCD, web GUI. 1209 tests |
| [likx](likx/) | Python/GTK | Screenshot capture, annotation, OCR. 955 tests. X11/Wayland |
| [steam-proton-helper](steam-proton-helper/) | Python | Steam/Proton diagnostics and fixes. PyPI published. v1.8.0 |
| [razer-controls](razer-controls/) | Python | Razer peripheral control — button remapping, macros, RGB, DPI |
| [arete-hud](arete-hud/) | Python | Heads-up display overlay system for Linux desktop |
| [elm](elm/) | Rust | EVE Linux Manager — Proton launcher with prefix management, snapshots, rollback |

## Structure

Each tool lives in its own directory with full git history preserved via `git subtree`. Every tool is independently installable — no shared runtime dependencies.

```
LinuxTools/
├── g13/                     # Logitech G13 gameboard driver
├── likx/                    # Screenshot + OCR tool
├── steam-proton-helper/     # Steam/Proton diagnostics
├── razer-controls/          # Razer peripheral controls
├── arete-hud/               # Desktop HUD overlay
└── elm/                     # EVE Online Linux launcher (Rust)
```

### G13 Documentation

> **Getting started with the G13?** See the [Installation Guide](g13/INSTALLATION.md) for setup (udev rules, pip install, systemd service) and the [Troubleshooting Guide](g13/TROUBLESHOOTING.md) if you hit issues. Full docs: [Button Mapping Guide](g13/BUTTON_MAPPING_GUIDE.md) | [Background Image Setup](g13/BACKGROUND_IMAGE_SETUP.md)

---

## Install

```bash
# SteamProtonHelper (from PyPI)
pip install steam-proton-helper

# G13 (requires udev rules)
cd g13/ && pip install -e .
sudo cp udev/99-g13.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules

# LikX
cd likx/ && ./setup.sh

# Razer Controls
cd razer-controls/ && pip install -e .

# ELM (Rust)
cd elm/ && cargo build --release
```

## License

MIT

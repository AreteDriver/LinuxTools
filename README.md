# LinuxTools

**Native Linux desktop utilities that solve problems nobody else bothered to fix.**

Every tool here exists because the existing solutions are missing, broken, or abandoned on Linux. Each is independently installable with its own dependencies, tests, and packaging.

---

## The Tools

### [LikX](likx/) — Screenshot + OCR Tool
> GTK3 screenshot capture, annotation, and OCR for Linux desktops.

**The killer feature:** Built-in OCR via Tesseract — no other Linux screenshot tool has this natively.

- Multi-mode capture: fullscreen, region, window, scrolling, GIF recording
- Annotation: arrows, text, blur, highlights, callouts, numbered markers
- Cloud upload: Imgur, Dropbox, S3, file.io
- Display support: X11 + Wayland (GNOME, KDE, Sway)
- **v3.30.0** · 1752 tests · Python/GTK

```bash
cd likx/ && ./setup.sh
# Or AppImage: ./LikX-3.30.0-x86_64.AppImage
```

### G13 — Logitech G13 Linux Driver
> Moved out of this monorepo into its own repository: **[AreteDriver/G13_Linux](https://github.com/AreteDriver/G13_Linux)** ([PyPI](https://pypi.org/project/g13-linux/)).

### [SteamProtonHelper](steam-proton-helper/) — Steam/Proton Diagnostics
> Diagnoses and fixes Steam/Proton gaming issues on Linux. CLI + GUI modes.

**The most polished tool in the collection.** Single-file, zero dependencies, works everywhere.

- Auto-detect Steam install across all distro layouts
- Verify Vulkan drivers, 32-bit libraries, Mesa versions
- GE-Proton management (download, install, set default)
- ProtonDB lookup for game compatibility
- Multi-distro support: Ubuntu, Fedora, Arch, SteamOS/Steam Deck
- **v2.3.3** · Published on [PyPI](https://pypi.org/project/steam-proton-helper/) · Python (stdlib only)

```bash
pip install steam-proton-helper
steam-proton-helper --check
```

### [Razer Controls](razer-controls/) — Razer Peripheral Manager
> Button remapping, macro recording, RGB lighting, and DPI management for Razer devices.

- Per-button key remapping and macro assignment
- Zone-based RGB lighting control
- DPI stage configuration
- Profile save/load
- **v1.9.8** · Python

```bash
cd razer-controls/ && pip install -e .
```

### [ELM](elm/) — EVE Linux Manager
> Proton launcher for EVE Online with prefix management, snapshots, and rollback.

- Wine/Proton prefix management
- Settings snapshots and rollback
- Launch configuration profiles
- **Rust** · `cargo build --release`

### [Arete HUD](arete-hud/) — Desktop Overlay System
> Heads-up display overlay for Linux desktop. Early stage.

---

## Architecture

```
LinuxTools/
├── likx/                    # Screenshot + OCR tool
│   ├── src/                 #   GTK3 capture, editor, uploader, clipboard
│   └── resources/           #   Icons, assets
├── steam-proton-helper/     # Steam/Proton diagnostics (single file)
├── razer-controls/          # Razer peripheral controls
├── arete-hud/               # Desktop HUD overlay
└── elm/                     # EVE Online Linux launcher (Rust)
```

Each tool has its own `pyproject.toml` (or `Cargo.toml`), test suite, CI workflow, and can be packaged independently as PyPI, AppImage, .deb, Flatpak, or Snap.

---

## Design Principles

1. **Each tool is independently installable.** No shared runtime dependencies.
2. **Python-first** (Rust where performance matters). Consistent, accessible stack.
3. **Packaging matters.** PyPI, AppImage, .deb, Flatpak — meet users where they are.
4. **Solve real problems.** Every tool exists because the alternative is broken or missing.

## Community

[Discord](https://discord.gg/fdzQkrt8) — Join the community

## License

MIT

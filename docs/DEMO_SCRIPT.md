# LikX Demo Script

**Duration:** 2-3 minutes
**Target Audience:** Linux users, developers, technical hiring managers

---

## Setup (Before Recording)

```bash
# Ensure LikX is installed and running
likx &

# Have a sample webpage or document open for capturing
# Have some sensitive data visible for blur demo
```

---

## Demo Flow

### 1. Hook (10 seconds)

> "LikX is a screenshot tool for Linux that actually works on Wayland. Capture, annotate, and share - with features like GIF recording and scrolling screenshots."

**Show:** Main window

---

### 2. Capture Modes (30 seconds)

**Action:** Demonstrate each capture mode

> "Three capture modes: fullscreen, region, or window."

1. **Region capture** (`Ctrl+Shift+R`)
   - Draw selection box
   - Show snap-to-edge behavior

2. **Window capture** (`Ctrl+Shift+W`)
   - Click a window
   - Shows window decoration handling

> "Works on both X11 and Wayland - GNOME, KDE, Sway."

---

### 3. Annotation Tools (60 seconds)

**Action:** Annotate a screenshot

> "Full annotation suite. Let me highlight some key features."

1. **Arrow tool** (`A`)
   - Draw arrow pointing to something
   - Show filled vs open arrow styles in toolbar

2. **Text** (`T`)
   - Add a label
   - Show font/size options

3. **Blur** (`B`)
   - Blur sensitive data (email, name, etc.)
   > "Privacy tools for sensitive data - blur or pixelate."

4. **Number markers** (`N`)
   - Add numbered callouts: 1, 2, 3
   > "Perfect for step-by-step documentation."

5. **Selection & alignment**
   - Select multiple annotations
   - Show snap guides
   > "Smart alignment guides when positioning."

---

### 4. Special Features (45 seconds)

#### GIF Recording

> "Record any region as a GIF."

**Action:**
1. Press `G` for GIF mode
2. Select region
3. Record for 3 seconds
4. Stop and show result

> "Uses ffmpeg on X11, wf-recorder on Wayland."

#### Scrolling Screenshot

> "Capture entire web pages or documents."

**Action:** (Optional - takes time)
1. Press `Ctrl+Alt+S`
2. Show auto-scroll behavior
3. Show stitched result

#### OCR

> "Extract text from any screenshot."

**Action:**
1. Capture text-heavy region
2. Click OCR button
3. Show extracted text

---

### 5. Workflow Integration (20 seconds)

> "Save locally, copy to clipboard, or upload directly to Imgur, S3, Dropbox, or Google Drive."

**Show:** Save/upload options

> "History browser keeps all your captures organized."

**Show:** History window with thumbnails

---

### 6. Close (15 seconds)

> "LikX - screenshot capture that works everywhere Linux does. Available on Snap Store, AppImage, or build from source."

**Show:** Installation commands

```bash
sudo snap install likx
```

---

## Key Talking Points

- **Wayland-native** - works where Flameshot doesn't
- **GIF recording** - not just static screenshots
- **Scrolling capture** - full-page screenshots
- **OCR built-in** - extract text without external tools
- **Pin to desktop** - keep references visible
- **1,750+ tests** - production quality

---

## Keyboard Shortcuts to Demo

| Key | Tool | Demo Point |
|-----|------|------------|
| `V` | Select | Move/resize annotations |
| `A` | Arrow | Multiple arrow styles |
| `T` | Text | Font customization |
| `B` | Blur | Privacy protection |
| `N` | Number | Step documentation |
| `G` | GIF | Recording mode |
| `C` | Crop | Post-capture cropping |
| `Ctrl+Z` | Undo | Full undo history |
| Right-click | Radial menu | Quick tool access |

---

## Recording Tips

1. **Use a visually interesting page** for capture (colorful, with text)
2. **Pre-stage sensitive data** to blur (don't use real data)
3. **Keep annotations simple** - 3-4 max per screenshot
4. **Show the radial menu** (right-click) - it's visually distinctive
5. **End with a clean, annotated screenshot** as the hero image

---

## Backup Demos

### Command Palette
> "Ctrl+Shift+P opens the command palette - search any action by name."

### Effects Panel
> "Add shadows, borders, rounded corners - professional polish."

### Multi-monitor
> "Number keys 1-9 quick-select monitors for fullscreen capture."

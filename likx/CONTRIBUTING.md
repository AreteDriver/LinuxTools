# Contributing to LikX

Thank you for your interest in contributing to LikX! This document provides guidelines for contributing to the project.

## Ways to Contribute

- **Report Bugs**: Submit detailed bug reports via GitHub Issues
- **Suggest Features**: Propose new capture or annotation features
- **Submit Code**: Fix bugs, add features, or improve performance
- **Improve Documentation**: Help make our docs clearer
- **Test on Different DEs**: Test LikX on various desktop environments

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/LikX.git
cd LikX

# Add upstream remote
git remote add upstream https://github.com/AreteDriver/LikX.git
```

### 2. Set Up Development Environment

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
    gir1.2-gdk-3.0 gir1.2-gdkpixbuf-2.0 libcairo2-dev \
    python3-dev xdotool scrot

# Install Python dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### 3. Create a Branch

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Run `ruff check` and `ruff format` before committing
- Pre-commit hooks will check this automatically

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

### Commit Messages

Use conventional commit format:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example: `feat(editor): add circle annotation tool`

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md if applicable
5. Submit PR with clear description

## Testing on Different Environments

LikX aims to work across:

- **Display Servers**: X11 and Wayland
- **Desktop Environments**: GNOME, KDE, XFCE, etc.
- **Distributions**: Ubuntu, Fedora, Arch, etc.

Testing on different setups is very valuable!

## Need Help?

- Check existing issues for similar problems
- Open a new issue with your question
- Include your OS, DE, and Python version

Thank you for contributing!

# G13LogitechOPS

Logitech G13 Kernel Driver for Linux systems.

## CI/CD Status

![Testing Pipeline](https://github.com/AreteDriver/G13LogitechOPS/workflows/Testing%20Pipeline/badge.svg)
![Deployment Pipeline](https://github.com/AreteDriver/G13LogitechOPS/workflows/Deployment%20Pipeline/badge.svg)

## Overview

This repository contains the kernel driver for the Logitech G13 Gaming Keyboard, enabling full functionality on Linux systems.

## Development

This project uses GitHub Actions for continuous integration and deployment:

- **Testing Pipeline**: Automatically builds and tests the driver on every push and pull request
- **Deployment Pipeline**: Automatically packages and releases the driver when version tags are created

For detailed information about the CI/CD workflows, see [WORKFLOW_DOCUMENTATION.md](WORKFLOW_DOCUMENTATION.md).

## Installation

Download the latest release from the [Releases](https://github.com/AreteDriver/G13LogitechOPS/releases) page.

### Debian/Ubuntu (.deb package)

```bash
sudo dpkg -i g13-driver_*.deb
```

### Source Installation (.tar.gz)

```bash
tar -xzf g13-driver-*.tar.gz
cd g13-driver-*
sudo make install
```

## Building from Source

```bash
# Install build dependencies
sudo apt-get install build-essential linux-headers-$(uname -r) kmod libusb-1.0-0-dev pkg-config

# Build the driver
make

# Install (optional)
sudo make install
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
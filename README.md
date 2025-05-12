# Winblues 7

A bootable container built on top of [Bazzite](https://github.com/ublue-os/bazzite) and [AeroThemePlasma](https://gitgud.io/wackyideas/aerothemeplasma).

![image](https://github.com/user-attachments/assets/c7f93eee-f4a0-47e0-aff1-bc4f0de7641b)

## Project Status

This project is in alpha. Many of the components from AeroThemePlasma are installed but not configured. Some components are not installed at all. There are many rough edges.

## Installation

1. Install [Bazzite](https://bazzite.gg) using their ISO.
2. Rebase to one of the Winblues 7 images:

**For NVIDIA**
```bash
sudo bootc switch ghcr.io/winblues/blue7-nvidia:latest
``` 

**For Intel/AMD**
```bash
sudo bootc switch ghcr.io/winblues/blue7:latest
``` 

## Attribution:
- Wallpaper based on work by [KosZigler](https://www.deviantart.com/koszigler/art/Windows-7-Harmony-Style-Wallpaper-Like-Logon-700520270).
- Project logo from Reddit user [Acz___](https://www.reddit.com/r/FrutigerAero/comments/110sgm7/msn_avatars_of_all_colors/).

## Licensing

### Project Code & Configurations
All original code, workflows, configurations, and documentation in this repository are licensed under the [Apache License 2.0](LICENSE).

### Third-Party Assets
This project contains visual and audio elements that resemble Microsoft® Windows™ 7. These assets are used for nostalgic and illustrative purposes only:

Microsoft® Windows™ is a registered trademark of Microsoft Corporation. This project is not affiliated with, endorsed by, or sponsored by Microsoft. All Microsoft trademarks, service marks, trade names, and product names are the property of Microsoft Corporation.

This project does not distribute any copyrighted Microsoft binaries or code. Any similarity to Microsoft products is for interoperability, educational, and nostalgic purposes only.
# Generic Knights

[English](README.md) | [Português](README.pt-BR.md)

Mod author: **ZeroDS** · [Source and releases](https://github.com/andersongz0/GenericKnights)

**0.1.26-rc.1** updates documentation and credits. Gameplay data, Scale2x textures,
fallback sprites and all palettes are unchanged from the approved **0.1.25**.

- Holy Knight (male/female): Holy Sword; Knight level 8 + White Mage level 8.
- Rune Knight (male/female): Limit; Knight level 8 + Time Mage level 8.

## Requirements

- Windows x64 and a legal Steam installation of **FINAL FANTASY TACTICS - The Ivalice Chronicles**, Enhanced mode.
- [FFTModLoader 0.11.7-rc.1](https://github.com/andersongz0/FFTModLoader/releases/tag/v0.11.7-rc.1), installed as a complete package.
- Utility Mod Loader and loader-owned **JobExpansion**. Original GenericJobs, SigScan and SharedLib.Hooks are their compatibility dependencies.

All required runtime components are supplied by FFTModLoader; no separate dependency downloads are needed.

## Generic Knights Installation Guide

1. Install FFTModLoader following [its installation guide](https://github.com/andersongz0/FFTModLoader#fftmodloader-installation-guide).
2. Close the game and loader.
3. Download **GenericKnights-0.1.26-rc.1.zip** from [release Assets](https://github.com/andersongz0/GenericKnights/releases/tag/v0.1.26-rc.1), not **Source code**.
4. Extract outside the game directory. Open PowerShell in the extracted folder and run `./install.ps1 -GameDirectory "your game folder"`.
5. Confirm that **Mods/Generic Knights/ModConfig.json** exists in the game installation.
6. Launch **FFTModLoader.exe** in Enhanced mode. Meet the job-level requirements above to unlock the new jobs.

The installer verifies package hashes and backs up replaced files under **FFTModLoader.Backup**. Saves and unrelated mods are preserved.
To update, close the game/loader and install the new complete release. Keep only one active copy of Generic Knights.
If dependency files are missing, reinstall the complete FFTModLoader package.

## Sprite credits

The [FFHacktics catalog](https://ffhacktics.com/sprites.php) identifies these original contributors.
Rune Knight uses the catalog's **Rogue** artwork, renamed for its role in this mod.

| Mod artwork | Catalog entry | Sprite | Portrait | Palettes |
| --- | --- | --- | --- | --- |
| Holy Knight male | Male Paladin | Lijj | Lijj | Lijj |
| Holy Knight female | Female Paladin | Lijj | Twinees | Lijj |
| Rune Knight male | Male Rogue | R999 | Lijj | Lijj |
| Rune Knight female | Female Rogue | R999 | Lijj | Lijj |

ZeroDS created the mod integration and conversion; original sprite/portrait authorship is not reassigned.
[SPRITE_CREDITS.json](SPRITE_CREDITS.json) records the original file hashes and attribution evidence.
Artwork is not relicensed as original ZeroDS code.

**Nenkai**: Utility Mod Loader, FF16Tools and FaithFramework.
**Kanaruu**: FFT Ivalice Chronicles - Sprite Modding Toolkit, used for filter comparisons and selected Scale2x outputs.
**cipherxof**: original FFTGenericJobs compatibility basis; its preserved MIT notice credits trigger.

See [credits/tools](CREDITS.md), [building](BUILD.md) and [third-party notices](THIRD_PARTY_NOTICES.md).
New mods are only published after the user's explicit finalized decision.

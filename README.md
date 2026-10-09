# Generic Knights

[English](README.md) | [Português](README.pt-BR.md)

Author: **ZeroDS** · [Source and releases](https://github.com/andersongz0/GenericKnights)

Generic Knights adds **Holy Knight** and **Rune Knight** as jobs for generic male and female units, with dedicated battle sprites, menu portraits and job commands.

## Features

- Holy Knight (male/female): Holy Sword; Knight level 8 + White Mage level 8.
- Rune Knight (male/female): Limit; Knight level 8 + Time Mage level 8.

## Requirements

- Windows x64 and a legal Steam installation of **FINAL FANTASY TACTICS - The Ivalice Chronicles**, Enhanced mode.
- The complete [FFTModLoader 0.11.7-rc.2 package](https://github.com/andersongz0/FFTModLoader/releases/tag/v0.11.7-rc.2).

JobExpansion, Utility Mod Loader and their compatibility dependencies are included with FFTModLoader.

## Generic Knights Installation Guide

1. Install FFTModLoader following [its guide](https://github.com/andersongz0/FFTModLoader#fftmodloader-installation-guide).
2. Close the game. Close the loader too if it is already installed and running.
3. Download **GenericKnights-0.1.26-rc.2.zip** from [release Assets](https://github.com/andersongz0/GenericKnights/releases/tag/v0.1.26-rc.2), not **Source code**.
4. Extract the ZIP to a separate folder outside the game installation.
5. Double-click **Install.cmd** and choose your language.
6. Check the detected folder and type **YES** to confirm. If several installations are found, choose one; if none is found, enter the path to **FFT_enhanced.exe** or its folder.
7. Approve the Windows permission prompt, if shown, and wait for completion.

No terminal commands are needed. The installer verifies the package and backs up replaced files under **FFTModLoader.Backup** in the game folder. Saves and unrelated mods are preserved.
The mod is installed in **Mods/Generic Knights**.

## Using Generic Knights

Start **FFTModLoader.exe** from the game folder. Meet the job-level requirements above to unlock the new jobs for your generic units.

## Updating

Close the game and any running loader, then run **Install.cmd** from the new complete release. If dependency files are missing, reinstall the complete FFTModLoader package.

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

# Generic Knights

[English](README.md) | [Português](README.pt-BR.md)

Mod author: **ZeroDS** · [Source and releases](https://github.com/andersongz0/GenericKnights)

**0.1.26-rc.1** updates documentation and credits. Gameplay data, Scale2x textures,
fallback sprites and all palettes are unchanged from the approved **0.1.25-art-test**.

- Holy Knight (male/female): Holy Sword; Knight level 8 + White Mage level 8.
- Rune Knight (male/female): Limit; Knight level 8 + Time Mage level 8.

## Installation and dependencies

Install [FFTModLoader 0.11.7-rc.1](https://github.com/andersongz0/FFTModLoader/releases) first.
Extract **GenericKnights-0.1.26-rc.1.zip** outside the game directory and run
`install.ps1 -GameDirectory "your game folder"` with the game/loader closed.
Launch FFTModLoader.exe in Enhanced mode.

Requires Utility Mod Loader and loader-owned JobExpansion. JobExpansion's original GenericJobs,
SigScan and SharedLib.Hooks dependencies are included with FFTModLoader.
**Reworked Chemist is not required.** No saves or unrelated mods are changed.

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

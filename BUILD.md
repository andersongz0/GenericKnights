# Building Generic Knights

[English](BUILD.md) | [Português](BUILD.pt-BR.md)

The `GenericKnights` directory contains generators, the sprite converter, original credited SPR inputs,
selected Scale2x indices/portraits and final data under `art-v6/Mod`.
There is no standalone gameplay DLL: loader-owned JobExpansion supplies runtime routing.

Use Python 3 with Pillow and .NET SDK 9 for tooling.
`build_tables.py` needs original tables extracted from your own game in `analysis/base-tables.sqlite`; these are not distributed.
Use Nenkai's FF16Tools and supply `FF16TOOLS_CLI` to `rebuild_mod.py`.

`build_filtered_art.py` preserves fallback SPRs and converts selected indices into pages/atlases.
Historical comparisons also require your own legal game resources and FF16Tools.
`toolkit-filter-runner` uses Kanaruu's Sprite Modding Toolkit's `ImageProcessor.cs`/`UpscaleMethod.cs` supplied locally.
Its decompiled code is not redistributed. The selected final outputs are already included.
DDS previews require `dds-preview` and its external dependencies.

Original artwork authors are listed in README and SPRITE_CREDITS.json.
This credit is not a blanket license over third-party artwork.
The rc.1 release changes metadata/documentation only; gameplay resource hashes are checked against art-v6.

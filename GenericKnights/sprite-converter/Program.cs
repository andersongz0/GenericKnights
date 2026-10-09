if (args.Length == 5 && args[0] == "--fit-native-bounds")
{
    NativePartPacking.FitNativeBounds(args[1], args[2], args[3], args[4]);
    return 0;
}
if (args.Length == 6 && args[0] == "--pack-cleanup-points")
{
    NativePartPacking.PackCleanup(args[1], args[2], args[3], args[4], args[5]);
    return 0;
}
if (args.Length == 6 && (args[0] == "--pack-native-parts" || args[0] == "--pack-native-slots"))
{
    NativePartPacking.Pack(args[1], args[2], args[3], args[4], args[5], args[0] == "--pack-native-slots");
    return 0;
}
if (args.Length == 3 && args[0] == "--prepare-icon")
{
    SpriteSheetPreparation.PrepareIcon(args[1], args[2]);
    return 0;
}
if (args.Length is >= 4 and <= 6 && args[0] is "--prepare-holy" or "--prepare-sheet" or "--prepare-sheet-native" or "--prepare-sheet-native-pink")
{
    SpriteSheetPreparation.Prepare(args[1], args[2], args[3], args.Length >= 5 ? args[4] : null,
        args.Length == 6 ? args[5] : null, args[0].StartsWith("--prepare-sheet-native") ? 240 : 128,
        args[0] == "--prepare-sheet-native-pink" ? "pink" : null);
    return 0;
}
if (args.Length is < 2 or > 3 || (args.Length == 3 && args[2] != "--portrait-middle"))
{
    Console.Error.WriteLine("Usage: SpriteConverter <input.bmp> <output_spr.bin> [--portrait-middle]");
    return 2;
}

BattleSpriteConverter.ConvertBmpToSpr(
    Path.GetFullPath(args[0]),
    Path.GetFullPath(args[1]), args.Length == 3);
return 0;

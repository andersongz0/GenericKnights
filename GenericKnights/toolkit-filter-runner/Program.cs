using FFTSpriteToolkit;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;

if (args.Length is < 3 or > 4)
{
    Console.Error.WriteLine("Usage: ToolkitFilters <input.png> <output.png> <method> [scale=2]");
    return 2;
}
using var source = Image.Load<Rgba32>(args[0]);
var method = Enum.Parse<UpscaleMethod>(args[2], ignoreCase: true);
var scale = args.Length == 4 ? double.Parse(args[3], System.Globalization.CultureInfo.InvariantCulture) : 2;
using var output = ImageProcessor.ProcessImage(source, scale, method, false, 16);
Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(args[1]))!);
output.SaveAsPng(args[1]);
Console.WriteLine($"Toolkit {method} {scale}x: {source.Width}x{source.Height} -> {output.Width}x{output.Height}");
return 0;

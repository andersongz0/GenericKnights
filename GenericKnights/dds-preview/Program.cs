using BCnEncoder.Decoder;
using System.Drawing;
using System.Drawing.Imaging;

using var input = File.OpenRead(args[0]);
var pixels = new BcDecoder().Decode2D(input);
using var bitmap = new Bitmap(pixels.Width, pixels.Height, PixelFormat.Format32bppArgb);
for (var y = 0; y < pixels.Height; y++)
for (var x = 0; x < pixels.Width; x++)
{
    var p = pixels.Span[y, x];
    bitmap.SetPixel(x, y, Color.FromArgb(p.a, p.r, p.g, p.b));
}
bitmap.Save(args[1], ImageFormat.Png);

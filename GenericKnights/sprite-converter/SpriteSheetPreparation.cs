using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.Security.Cryptography;
using System.Text.Json;

// Deterministic format conversion, not frame generation. Original drawings
// remain untouched. Only sheets with the native layout's aspect ratio qualify.
internal static class SpriteSheetPreparation
{
    const int Width = 256, Height = 488;
    readonly record struct Sample(int Color, int Weight);

    static bool IsBackdrop(Color c, string mode) => c.A < 128 ||
        (mode == "alpha" ? false : mode == "blue"
            ? c.R < 45 && c.G < 90 && c.B > c.R + 20 && c.B > c.G + 25
            : Math.Max(c.R, Math.Max(c.G, c.B)) <= 25);
    static int Pack(Color c) => (c.R >> 3) | ((c.G >> 3) << 5) | ((c.B >> 3) << 10);
    static int Channel(int c, int axis) => (c >> (axis * 5)) & 31;
    static Color Unpack(int c) => Color.FromArgb(255, Channel(c, 0) * 255 / 31,
        Channel(c, 1) * 255 / 31, Channel(c, 2) * 255 / 31);
    static bool Portrait(int x, int y) => x >= 80 && x < 128 && y >= 456;

    static int Range(List<Sample> samples, int axis) =>
        samples.Max(s => Channel(s.Color, axis)) - samples.Min(s => Channel(s.Color, axis));

    static int[] Palette(Dictionary<int, int> histogram, int colorCount = 15)
    {
        var boxes = new List<List<Sample>> { histogram.OrderBy(p => p.Key)
            .Select(p => new Sample(p.Key, p.Value)).ToList() };
        if (histogram.Count == 0) throw new InvalidDataException("Empty sprite palette.");
        while (boxes.Count < colorCount)
        {
            var box = boxes.Where(b => b.Count > 1).OrderByDescending(b =>
                b.Sum(s => (long)s.Weight) * Enumerable.Range(0, 3).Max(a => Range(b, a)))
                .FirstOrDefault();
            if (box == null) break;
            int axis = Enumerable.Range(0, 3).OrderByDescending(a => Range(box, a)).First();
            var sorted = box.OrderBy(s => Channel(s.Color, axis)).ThenBy(s => s.Color).ToList();
            long half = (sorted.Sum(s => (long)s.Weight) + 1) / 2, accumulated = 0;
            int split = 0;
            do { accumulated += sorted[split++].Weight; }
            while (accumulated < half && split < sorted.Count - 1);
            split = Math.Clamp(split, 1, sorted.Count - 1);
            boxes.Remove(box);
            boxes.Add(sorted.GetRange(0, split));
            boxes.Add(sorted.GetRange(split, sorted.Count - split));
        }
        var colors = boxes.Select(b => {
            long weight = b.Sum(s => (long)s.Weight);
            int packed = 0;
            for (int a = 0; a < 3; a++)
                packed |= (int)((b.Sum(s => (long)Channel(s.Color, a) * s.Weight) + weight / 2) / weight) << (a * 5);
            return packed;
        }).Distinct().OrderBy(c => Channel(c, 0) * 3 + Channel(c, 1) * 6 + Channel(c, 2)).ToList();
        while (colors.Count < colorCount) colors.Add(colors[^1]);
        return new[] { 0 }.Concat(colors).ToArray();
    }

    static int[] BodyPalette(Dictionary<int,int> histogram,string? accent)
    {
        if(accent==null)return Palette(histogram);
        // Preserve uncommon costume colors during RGB555 quantization, not a
        // recolor: all palette centers are derived from artist source samples.
        bool IsPink(int c)=>Channel(c,0)>Channel(c,1)*1.1&&Channel(c,2)>=Channel(c,1)*.95&&Channel(c,0)>8;
        var pink=histogram.Where(p=>IsPink(p.Key)).ToDictionary(p=>p.Key,p=>p.Value);
        var other=histogram.Where(p=>!IsPink(p.Key)).ToDictionary(p=>p.Key,p=>p.Value);
        if(pink.Count==0||other.Count==0)throw new InvalidDataException("Required source pink accent not found.");
        return new[]{0}.Concat(Palette(other,12).Skip(1)).Concat(Palette(pink,3).Skip(1)).ToArray();
    }

    static int Closest(int packed, int[] palette)
    {
        int best = 1, distance = int.MaxValue;
        for (int i = 1; i < palette.Length; i++)
        {
            int r = Channel(packed, 0) - Channel(palette[i], 0);
            int g = Channel(packed, 1) - Channel(palette[i], 1);
            int b = Channel(packed, 2) - Channel(palette[i], 2);
            int candidate = r*r*3 + g*g*6 + b*b*2;
            if (candidate < distance) { distance = candidate; best = i; }
        }
        return best;
    }

    public static void Prepare(string input, string output, string backdrop, string? portraitInput = null,
        string? bookHandInput = null, int bodyAlphaCutoff = 128, string? bodyAccent = null)
    {
        if (backdrop is not ("black" or "blue" or "alpha")) throw new ArgumentException("Backdrop: black, blue or alpha.");
        input = Path.GetFullPath(input); output = Path.GetFullPath(output);
        if (input.Equals(output, StringComparison.OrdinalIgnoreCase)) throw new ArgumentException("Keep originals intact.");
        using var source = new Bitmap(input);
        if (Math.Abs(source.Width * (double)Height / source.Height - Width) > 1)
            throw new InvalidDataException("Sheet does not match 256x488 layout; refusing to stretch frames.");
        using var resized = new Bitmap(Width, Height, PixelFormat.Format32bppArgb);
        using (var g = Graphics.FromImage(resized))
        {
            g.InterpolationMode = InterpolationMode.NearestNeighbor;
            g.PixelOffsetMode = PixelOffsetMode.Half;
            g.CompositingMode = CompositingMode.SourceCopy;
            g.DrawImage(source, new Rectangle(0, 0, Width, Height), 0, 0, source.Width, source.Height, GraphicsUnit.Pixel);
        }
        // Optional artist-supplied upright portrait. This is format packing,
        // not an art-generation step: 32x48 -> the native clockwise 48x32 slot.
        if (portraitInput != null)
        {
            using var portraitSource = new Bitmap(portraitInput);
            if (Math.Abs(portraitSource.Width * 48.0 / portraitSource.Height - 32) > 1)
                throw new InvalidDataException("Upright portrait must have a 2:3 aspect ratio.");
            using var portrait = new Bitmap(32, 48, PixelFormat.Format32bppArgb);
            using (var g = Graphics.FromImage(portrait))
            {
                g.InterpolationMode = InterpolationMode.NearestNeighbor;
                g.PixelOffsetMode = PixelOffsetMode.Half;
                g.CompositingMode = CompositingMode.SourceCopy;
                g.DrawImage(portraitSource, new Rectangle(0, 0, 32, 48), 0, 0, portraitSource.Width, portraitSource.Height, GraphicsUnit.Pixel);
            }
            for (int y = 0; y < 48; y++) for (int x = 0; x < 32; x++)
                resized.SetPixel(80 + 47 - y, 456 + x, portrait.GetPixel(x, y));
        }
        // An independently generated artist component is packed into the
        // exact 8x8 SHP rectangle used by Book Front (frames 129 / 310).
        // No native character pixels are copied into the new artwork.
        if (bookHandInput != null)
        {
            using var handSource = new Bitmap(bookHandInput);
            int left=handSource.Width, top=handSource.Height, right=-1, bottom=-1;
            for (int y=0;y<handSource.Height;y++) for(int x=0;x<handSource.Width;x++)
                if (handSource.GetPixel(x,y).A>=128)
                { left=Math.Min(left,x);top=Math.Min(top,y);right=Math.Max(right,x);bottom=Math.Max(bottom,y); }
            if (right<left) throw new InvalidDataException("Empty generated book hand.");
            using var hand=new Bitmap(6,3,PixelFormat.Format32bppArgb);
            using(var g=Graphics.FromImage(hand))
            {
                g.InterpolationMode=InterpolationMode.NearestNeighbor;
                g.PixelOffsetMode=PixelOffsetMode.Half;
                g.CompositingMode=CompositingMode.SourceCopy;
                g.DrawImage(handSource,new Rectangle(0,0,6,3),new Rectangle(left,top,right-left+1,bottom-top+1),GraphicsUnit.Pixel);
            }
            for(int y=480;y<488;y++) for(int x=0;x<8;x++) resized.SetPixel(x,y,Color.Transparent);
            for(int y=0;y<3;y++) for(int x=0;x<6;x++) resized.SetPixel(1+x,481+y,hand.GetPixel(x,y));
        }
        var samples = new int[Width * Height];
        var body = new Dictionary<int, int>(); var face = new Dictionary<int, int>();
        int transparent = 0;
        for (int y = 0; y < Height; y++) for (int x = 0; x < Width; x++)
        {
            Color c = resized.GetPixel(x, y);
            // Native sprites have binary transparency. Strict native export
            // excludes the generated semitransparent halo, not opaque art.
            if (IsBackdrop(c, backdrop) || (!Portrait(x,y) && c.A < bodyAlphaCutoff))
            { samples[y * Width + x] = -1; transparent++; continue; }
            int packed = Pack(c); samples[y * Width + x] = packed;
            var hist = Portrait(x, y) ? face : body;
            hist[packed] = hist.GetValueOrDefault(packed) + 1;
        }
        int[] bodyPalette = BodyPalette(body,bodyAccent), facePalette = Palette(face);
        byte[] indices = new byte[samples.Length];
        var bodyMap = body.Keys.ToDictionary(c => c, c => Closest(c, bodyPalette));
        var faceMap = face.Keys.ToDictionary(c => c, c => Closest(c, facePalette));
        for (int y = 0; y < Height; y++) for (int x = 0; x < Width; x++)
        {
            int p = y * Width + x;
            if (samples[p] < 0) continue;
            indices[p] = (byte)(Portrait(x, y) ? 128 + faceMap[samples[p]] : bodyMap[samples[p]]);
        }
        Directory.CreateDirectory(Path.GetDirectoryName(output)!);
        using (var writer = new BinaryWriter(File.Create(output)))
        {
            writer.Write((ushort)0x4D42); writer.Write(1078 + indices.Length);
            writer.Write(0); writer.Write(1078); writer.Write(40);
            writer.Write(Width); writer.Write(Height); writer.Write((ushort)1); writer.Write((ushort)8);
            writer.Write(0); writer.Write(indices.Length); writer.Write(2835); writer.Write(2835);
            writer.Write(256); writer.Write(256);
            for (int i = 0; i < 256; i++)
            {
                Color c = Unpack((i < 128 ? bodyPalette : facePalette)[i % 16]);
                writer.Write(c.B); writer.Write(c.G); writer.Write(c.R); writer.Write((byte)0);
            }
            for (int y = Height - 1; y >= 0; y--) writer.Write(indices, y * Width, Width);
        }
        // Transparent enlarged QA preview; native BMP itself stays indexed.
        using var preview = new Bitmap(Width * 3, Height * 3, PixelFormat.Format32bppArgb);
        for (int y = 0; y < Height; y++) for (int x = 0; x < Width; x++)
        {
            int index = indices[y * Width + x];
            Color c = index == 0 ? Color.Transparent : Unpack((index < 128 ? bodyPalette : facePalette)[index % 16]);
            for (int dy = 0; dy < 3; dy++) for (int dx = 0; dx < 3; dx++) preview.SetPixel(x * 3 + dx, y * 3 + dy, c);
        }
        preview.Save(Path.ChangeExtension(output, ".preview.png"), ImageFormat.Png);
        var manifest = new { source = input, sourceSha256 = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(input))),
            sourceWidth = source.Width, sourceHeight = source.Height, outputWidth = Width, outputHeight = Height,
            outputSha256 = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(output))), backdrop, bodyAlphaCutoff,
            portraitY = 456, portraitSource = portraitInput, bookHandSource = bookHandInput,
            bookHandSourceSha256 = bookHandInput == null ? null : Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(bookHandInput))),
            portraitSourceSha256 = portraitInput == null ? null : Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(portraitInput))),
            transparentPixels = transparent, bodyAccent, bodyPaletteRgb555 = bodyPalette, portraitPaletteRgb555 = facePalette };
        File.WriteAllText(Path.ChangeExtension(output, ".adaptation.json"), JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }));
        Console.WriteLine($"Prepared {Path.GetFileName(output)}: 256x488, indexed 8bpp, 15+15 colors, {transparent} transparent pixels; original preserved.");
    }

    public static void PrepareIcon(string input, string output)
    {
        input=Path.GetFullPath(input); output=Path.GetFullPath(output);
        if(input.Equals(output,StringComparison.OrdinalIgnoreCase)) throw new ArgumentException("Keep source icon intact.");
        using var source=new Bitmap(input);
        if(source.Width!=source.Height) throw new InvalidDataException("Job emblem must be square.");
        using var icon=new Bitmap(60,60,PixelFormat.Format32bppArgb);
        using(var g=Graphics.FromImage(icon))
        {
            g.InterpolationMode=InterpolationMode.HighQualityBicubic;
            g.PixelOffsetMode=PixelOffsetMode.HighQuality;
            g.CompositingMode=CompositingMode.SourceCopy;
            g.DrawImage(source,new Rectangle(0,0,60,60),0,0,source.Width,source.Height,GraphicsUnit.Pixel);
        }
        Directory.CreateDirectory(Path.GetDirectoryName(output)!);
        icon.Save(output,ImageFormat.Png);
        Console.WriteLine($"Prepared native 60x60 job icon: {output}");
    }
}

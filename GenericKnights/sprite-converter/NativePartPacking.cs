using System.Buffers.Binary;
using System.Drawing;
using System.Drawing.Imaging;
using System.Security.Cryptography;
using System.Text.Json;

// Format/atlas placement only. Every inserted drawing is an imagegen output.
// Fit each isolated generated component to its native crop's occupied bounds,
// preserving source-crop coordinates, palette, portrait and all unrelated pixels.
internal static class NativePartPacking
{
    static int I32(byte[] data, int p) => BinaryPrimitives.ReadInt32LittleEndian(data.AsSpan(p,4));
    // Native atlas export: shrink-only nearest-neighbor placement into the
    // reference's occupied envelope. No native color pixels are copied.
    // Work on maximal, disjoint SHP crops, not nested head/torso sub-crops.
    public static void FitNativeBounds(string input,string referencePath,string layoutPath,string output)
    {
        if(Path.GetFullPath(input).Equals(Path.GetFullPath(output),StringComparison.OrdinalIgnoreCase))
            throw new ArgumentException("Preserve the pre-fit artwork.");
        byte[] before=File.ReadAllBytes(input),data=(byte[])before.Clone();
        int offset=I32(data,10),width=I32(data,18),height=I32(data,22),stride=(width+3)&~3;
        if(width!=256 || height!=488 || data[28]!=8 || I32(data,30)!=0)
            throw new InvalidDataException("Requires native indexed BMP.");
        int At(int x,int y)=>offset+(height-1-y)*stride+x;
        using var reference=new Bitmap(referencePath);
        using var doc=JsonDocument.Parse(File.ReadAllText(layoutPath));
        var all=doc.RootElement.GetProperty("tiles").EnumerateArray().Select(t=>{
            var v=t.GetProperty("rect");return new Rectangle(v[0].GetInt32(),v[1].GetInt32(),v[2].GetInt32(),v[3].GetInt32());
        }).Distinct().ToArray();
        var portrait=new Rectangle(80,456,48,32);
        var maximal=all.Where(r=>!r.IntersectsWith(portrait)&&!all.Any(o=>o!=r&&o.Contains(r))).ToArray();
        // Some native full-body crops intentionally share pixels with another
        // pose. Never move either of those overlapping regions independently.
        var crops=maximal.Where(r=>!maximal.Any(o=>o!=r&&r.IntersectsWith(o))).ToArray();
        var report=new List<object>(); var allowed=new HashSet<int>();
        foreach(var r in crops)
        {
            int l=r.Right,t=r.Bottom,rr=r.Left-1,b=r.Top-1;
            for(int y=r.Top;y<r.Bottom;y++)for(int x=r.Left;x<r.Right;x++)
                if(before[At(x,y)]!=0){l=Math.Min(l,x);t=Math.Min(t,y);rr=Math.Max(rr,x);b=Math.Max(b,y);}
            if(rr<l)continue;
            Rectangle oldBounds;
            try{oldBounds=Bounds(reference,r);}catch(InvalidDataException){continue;}
            var from=new Rectangle(l,t,rr-l+1,b-t+1);
            double scale=Math.Min(1.0,Math.Min(oldBounds.Width/(double)from.Width,oldBounds.Height/(double)from.Height));
            int w=Math.Max(1,(int)Math.Floor(from.Width*scale)),h=Math.Max(1,(int)Math.Floor(from.Height*scale));
            var to=new Rectangle(oldBounds.X+(oldBounds.Width-w)/2,oldBounds.Y+(oldBounds.Height-h)/2,w,h);
            // Preserve already-native geometry, even if its silhouette differs.
            if(scale>=1.0)continue;
            for(int y=r.Top;y<r.Bottom;y++)for(int x=r.Left;x<r.Right;x++)
            {int p=At(x,y);allowed.Add(p);data[p]=0;}
            for(int y=0;y<h;y++)for(int x=0;x<w;x++)
            {
                int sx=from.Left+Math.Min(from.Width-1,(int)((x+.5)*from.Width/w));
                int sy=from.Top+Math.Min(from.Height-1,(int)((y+.5)*from.Height/h));
                data[At(to.Left+x,to.Top+y)]=before[At(sx,sy)];
            }
            report.Add(new{crop=new[]{r.X,r.Y,r.Width,r.Height},from=new[]{from.X,from.Y,from.Width,from.Height},to=new[]{to.X,to.Y,to.Width,to.Height},scale});
        }
        for(int i=0;i<data.Length;i++)if(data[i]!=before[i]&&!allowed.Contains(i))throw new InvalidDataException("Changed an unselected byte.");
        File.WriteAllBytes(output,data);
        var result=new{input,referencePath,output,report,overlappingCropsPreserved=maximal.Length-crops.Length,nativePixelsCopied=false,unchangedPaletteAndPortrait=true,changedPixels=data.Where((v,i)=>v!=before[i]).Count(),sha256=Convert.ToHexString(SHA256.HashData(data))};
        File.WriteAllText(Path.ChangeExtension(output,".fit.json"),JsonSerializer.Serialize(result,new JsonSerializerOptions{WriteIndented=true}));
        Console.WriteLine($"Fitted {report.Count} oversized native atlas crops; palette and portrait preserved.");
    }
    public static void PackCleanup(string input,string atlasPath,string referencePath,string manifestPath,string output)
    {
        if(Path.GetFullPath(input).Equals(Path.GetFullPath(output),StringComparison.OrdinalIgnoreCase))
            throw new ArgumentException("Keep the pre-cleanup indexed sheet intact.");
        byte[] before=File.ReadAllBytes(input),data=(byte[])before.Clone();
        int offset=I32(data,10),width=I32(data,18),height=I32(data,22),stride=(width+3)&~3;
        if(width!=256 || height!=488 || data[28]!=8 || I32(data,30)!=0)
            throw new InvalidDataException("Requires native indexed BMP.");
        using var atlas=new Bitmap(atlasPath);using var reference=new Bitmap(referencePath);
        using var doc=JsonDocument.Parse(File.ReadAllText(manifestPath));
        int cols=doc.RootElement.GetProperty("columns").GetInt32(),rows=doc.RootElement.GetProperty("rows").GetInt32(),cell=doc.RootElement.GetProperty("cell").GetInt32();
        if(Math.Abs(atlas.Width/(double)atlas.Height-cols/(double)rows)>.01)
            throw new InvalidDataException("Cleanup atlas changed its aspect ratio.");
        var packed=new List<int[]>();var retained=new List<int[]>();var allowed=new HashSet<int>();
        foreach(var part in doc.RootElement.GetProperty("parts").EnumerateArray())
        {
            int slot=part.GetProperty("slot").GetInt32();
            int[] rect=part.GetProperty("rect").EnumerateArray().Select(v=>v.GetInt32()).ToArray();
            foreach(var point in part.GetProperty("points").EnumerateArray())
            {
                int x=point[0].GetInt32(),y=point[1].GetInt32();
                if(reference.GetPixel(x,y).A>=240) throw new InvalidDataException("Selected cleanup overlaps native art.");
                int p=offset+(height-1-y)*stride+x;allowed.Add(p);
                int sx=(int)(((slot%cols)*cell+x-rect[0]+.5)*atlas.Width/(cols*cell));
                int sy=(int)(((slot/cols)*cell+y-rect[1]+.5)*atlas.Height/(rows*cell));
                // Import only transparency actually produced by the image editor.
                // Reject new colored artwork; central component regeneration is ignored.
                if(atlas.GetPixel(sx,sy).A<240) { data[p]=0;packed.Add(new[]{x,y}); }
                else retained.Add(new[]{x,y});
            }
        }
        for(int i=0;i<data.Length;i++) if(data[i]!=before[i]&&!allowed.Contains(i))
            throw new InvalidDataException("Cleanup changed an unselected byte.");
        File.WriteAllBytes(output,data);
        var report=new {input,atlasPath,output,packed,retained,unchangedOutsideSelectedPoints=true,
            paletteAndPortraitUnchanged=true,sha256=Convert.ToHexString(SHA256.HashData(data))};
        File.WriteAllText(Path.ChangeExtension(output,".cleanup.json"),JsonSerializer.Serialize(report,new JsonSerializerOptions{WriteIndented=true}));
        Console.WriteLine(JsonSerializer.Serialize(report));
    }
    static Rectangle Bounds(Bitmap bitmap, Rectangle rect)
    {
        int l=rect.Right,t=rect.Bottom,r=rect.Left-1,b=rect.Top-1;
        for(int y=rect.Top;y<rect.Bottom;y++) for(int x=rect.Left;x<rect.Right;x++)
            if(bitmap.GetPixel(x,y).A>=240)
            { l=Math.Min(l,x);t=Math.Min(t,y);r=Math.Max(r,x);b=Math.Max(b,y); }
        if(r<l) throw new InvalidDataException("Empty component in atlas/reference.");
        return new Rectangle(l,t,r-l+1,b-t+1);
    }
    public static void Pack(string input, string atlasPath, string referencePath, string manifestPath, string output, bool exactSlots = false)
    {
        if(Path.GetFullPath(input).Equals(Path.GetFullPath(output),StringComparison.OrdinalIgnoreCase))
            throw new ArgumentException("Keep the original indexed sheet intact.");
        byte[] before=File.ReadAllBytes(input), data=(byte[])before.Clone();
        int offset=I32(data,10),width=I32(data,18),height=I32(data,22),stride=(width+3)&~3;
        if(width!=256 || height!=488 || data[28]!=8 || I32(data,30)!=0)
            throw new InvalidDataException("Requires native uncompressed 256x488 8bpp BMP.");
        int At(int x,int y) => offset+(height-1-y)*stride+x;
        using var atlas=new Bitmap(atlasPath);
        using var reference=new Bitmap(referencePath);
        using var doc=JsonDocument.Parse(File.ReadAllText(manifestPath));
        int columns=doc.RootElement.GetProperty("columns").GetInt32();
        int rows=doc.RootElement.GetProperty("rows").GetInt32();
        int cellWidth=doc.RootElement.TryGetProperty("cellWidth",out var cw) ? cw.GetInt32() : 1;
        int cellHeight=doc.RootElement.TryGetProperty("cellHeight",out var ch) ? ch.GetInt32() : 1;
        if(Math.Abs(atlas.Width/(double)atlas.Height-columns*cellWidth/(double)(rows*cellHeight))>.01)
            throw new InvalidDataException("Atlas aspect ratio does not match declared cells.");
        var changedAllowed=new HashSet<int>(); var report=new List<object>();
        var palette=Enumerable.Range(0,16).Select(i=>Color.FromArgb(255,data[54+i*4+2],data[54+i*4+1],data[54+i*4])).ToArray();
        byte Closest(Color c)
        {
            int best=1, distance=int.MaxValue;
            for(int i=1;i<16;i++)
            {
                int r=c.R-palette[i].R,g=c.G-palette[i].G,b=c.B-palette[i].B;
                int d=r*r*3+g*g*6+b*b*2;
                if(d<distance){ distance=d;best=i; }
            }
            return (byte)best;
        }
        foreach(var entry in doc.RootElement.GetProperty("parts").EnumerateArray())
        {
            int slot=entry.GetProperty("slot").GetInt32();
            int[] rect=entry.GetProperty("rect").EnumerateArray().Select(v=>v.GetInt32()).ToArray();
            var destination=new Rectangle(rect[0],rect[1],rect[2],rect[3]);
            if(destination.Right>256 || destination.Bottom>456 || destination.Left<0 || destination.Top<0)
                throw new InvalidDataException("Part would overwrite portrait or leave body area.");
            int cx=slot%columns,cy=slot/columns;
            var cell=Rectangle.FromLTRB(cx*atlas.Width/columns,cy*atlas.Height/rows,
                (cx+1)*atlas.Width/columns,(cy+1)*atlas.Height/rows);
            Rectangle from=exactSlots ? cell : Bounds(atlas,cell),to=exactSlots ? destination : Bounds(reference,destination);
            for(int y=destination.Top;y<destination.Bottom;y++) for(int x=destination.Left;x<destination.Right;x++)
            { int p=At(x,y); changedAllowed.Add(p);data[p]=0; }
            for(int y=0;y<to.Height;y++) for(int x=0;x<to.Width;x++)
            {
                // Center-sampled nearest-neighbor export; no invented pixels/poses.
                int sx=from.Left+Math.Min(from.Width-1,(int)((x+.5)*from.Width/to.Width));
                int sy=from.Top+Math.Min(from.Height-1,(int)((y+.5)*from.Height/to.Height));
                Color c=atlas.GetPixel(sx,sy);
                data[At(to.Left+x,to.Top+y)]=c.A>=240?Closest(c):(byte)0;
            }
            report.Add(new { slot, rect, generatedBounds=new[]{from.X,from.Y,from.Width,from.Height},
                nativeBounds=new[]{to.X,to.Y,to.Width,to.Height} });
        }
        for(int p=0;p<data.Length;p++)
            if(data[p]!=before[p] && !changedAllowed.Contains(p))
                throw new InvalidDataException("Unexpected pixel/header/palette mutation.");
        File.WriteAllBytes(output,data);
        using var preview=new Bitmap(768,1464,PixelFormat.Format32bppArgb);
        for(int y=0;y<height;y++) for(int x=0;x<width;x++)
        {
            int v=data[At(x,y)];
            Color c=v==0?Color.Transparent:Color.FromArgb(255,data[54+v*4+2],data[54+v*4+1],data[54+v*4]);
            for(int dy=0;dy<3;dy++) for(int dx=0;dx<3;dx++) preview.SetPixel(x*3+dx,y*3+dy,c);
        }
        preview.Save(Path.ChangeExtension(output,".preview.png"),ImageFormat.Png);
        var result=new { input, atlasPath, referencePath, output, report,
            changedPixels=data.Where((v,i)=>v!=before[i]).Count(), untouchedOutsideParts=true,
            paletteAndPortraitUnchanged=true,placement=exactSlots ? "whole-cell coordinate sampling; no bounding-box fitting" : "occupied-bounds fitting",sha256=Convert.ToHexString(SHA256.HashData(data)) };
        File.WriteAllText(Path.ChangeExtension(output,".parts.json"),JsonSerializer.Serialize(result,new JsonSerializerOptions{WriteIndented=true}));
        Console.WriteLine(JsonSerializer.Serialize(result));
    }
}

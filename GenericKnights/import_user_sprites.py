"""Import user-provided native SPR artwork without redraw or color quantization."""
from pathlib import Path
import hashlib
import json
import struct
import sys
from PIL import Image, ImageDraw
from analyze_native_art import decode, render_frame, ROOT

SOURCES = (
    ('holy', 'HolyKnight Male', 'holy_m', 'Sprite de Holy Knight/Male Paladin.spr'),
    ('holy', 'HolyKnight Female', 'holy_f', 'Sprite de Holy Knight/Female Paladin.spr'),
    ('rune', 'Rune Knight Male', 'rune_m', 'Sprite de Rune Knight/Rune Knight Male.spr'),
    ('rune', 'Rune Knight Female', 'rune_f', 'Sprite de Rune Knight/Rune Knight Female.spr'),
)

def main():
    target = Path(sys.argv[1]).resolve()
    layout = json.loads((ROOT/'art-v2/native-reference/native-layout.json').read_text())
    board = Image.new('RGB', (960, 580), (46, 49, 57))
    draw = ImageDraw.Draw(board)
    records = []
    for i, (folder, label, key, relative) in enumerate(SOURCES):
        source = ROOT.parent/'Sprite'/relative
        data = source.read_bytes()
        indices = decode(data)
        assert len(indices) == 256*488
        # Native palette 0 is body, palette 8 is portrait. Keep all 16
        # palettes in BMP/source copy, including nontransparent face background.
        palette = []
        for color in struct.unpack('<256H', data[:512]):
            palette.extend(((color&31)*255//31, ((color>>5)&31)*255//31,
                            ((color>>10)&31)*255//31))
        editor = list(indices)
        for y in range(456, 488):
            for x in range(80, 128):
                editor[y*256+x] += 128
        image = Image.new('P', (256, 488))
        image.putpalette(palette)
        image.putdata(editor)
        # Only body index zero is transparent. Portrait uses its original
        # opaque background color instead of forcing palette 8 index 0 black.
        image.info['transparency'] = 0
        out = target/folder/(label+'.BMP')
        out.parent.mkdir(parents=True, exist_ok=True)
        image.save(out)
        png = out.with_suffix('.png')
        rgba = Image.new('RGBA', image.size)
        rgba.putdata([(*palette[v*3:v*3+3], 0 if v == 0 else 255) for v in editor])
        rgba.save(png)
        source_copy = target/'sources'/(key+'.spr')
        source_copy.parent.mkdir(parents=True, exist_ok=True)
        source_copy.write_bytes(data)
        for frame in layout['frames']:
            assembled = render_frame(rgba, frame)
            assert assembled.size == (80, 80)
        draw.text((i*240+20, 12), label, fill='white')
        pose = rgba.crop((0,0,32,40)).resize((192,240), Image.Resampling.NEAREST)
        face = rgba.crop((80,456,128,488)).transpose(Image.Transpose.ROTATE_90).resize((128,192), Image.Resampling.NEAREST)
        board.paste(pose, (i*240+24,42), pose)
        board.paste(face, (i*240+56,310), face)
        records.append(dict(name=label, key=key, source=str(source),
                            sourceBytes=len(data), sourceSha256=hashlib.sha256(data).hexdigest(),
                            bmp=str(out), pixelIndicesPreserved=True, paletteSlotsPreserved=16))
    qa = target/'qa'
    qa.mkdir(parents=True, exist_ok=True)
    board.save(qa/'source-preview.png')
    (target/'source-import.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    print(json.dumps(records, indent=2))

if __name__ == '__main__':
    main()

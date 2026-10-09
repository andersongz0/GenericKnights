"""Compare the Toolkit's actual processor code with original enhanced G2D art.

This is deterministic Toolkit filtering, not AI image generation or a redraw.
All source SPRs and their palettes remain unchanged.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, struct, subprocess, sys
from PIL import Image, ImageDraw
from analyze_native_art import ROOT, decode

ART = ROOT/'art-v6'
PREVIOUS = ROOT/'art-v5'
RUNNER = ROOT/'toolkit-filter-runner/bin/Release/net9.0/ToolkitFilters.dll'
METHODS = ('NearestNeighbor', 'Scale2x', 'HQ2x', 'xBR2x')
KEYS = ('holy_m', 'holy_f', 'rune_m', 'rune_f')
LAYOUT = json.loads((ROOT/'art-v2/native-reference/native-layout.json').read_text())

def palette(data, slot=0):
    return [((v&31)*255//31, ((v>>5)&31)*255//31, ((v>>10)&31)*255//31)
            for v in struct.unpack_from('<16H', data, slot*32)]

def colored(indices, size, colors, opaque=False):
    im = Image.new('RGBA', size)
    im.putdata([(*colors[v], 255 if v or opaque else 0) for v in indices])
    return im

def render2(sheet, frame):
    out = Image.new('RGBA', (160,160))
    for tile in frame['tiles']:
        x,y,w,h=tile['rect']; crop=sheet.crop((x*2,y*2,(x+w)*2,(y+h)*2))
        if tile['flipX']: crop=crop.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if tile['flipY']: crop=crop.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        dx,dy=tile['position']; out.alpha_composite(crop,(80+dx*2,120+dy*2))
    return out

def indices_for(image, colors):
    # Enhanced G2D remains 4bpp and uses the supplied SPR palettes. Toolkit
    # HQ interpolation can create new RGB colors; map them to the original
    # 15 opaque colors, never quantize or replace the original team palettes.
    cache={}
    output=[]
    for pixel in image.convert('RGBA').get_flattened_data():
        if pixel not in cache:
            r,g,b,a=pixel
            cache[pixel]=0 if a<128 else min(range(1,16), key=lambda j:
                (r-colors[j][0])**2+(g-colors[j][1])**2+(b-colors[j][2])**2)
        output.append(cache[pixel])
    return bytes(output)

def run_filter(job):
    source, output, method, scale=job
    subprocess.run(['dotnet',str(RUNNER),str(source),str(output),method,str(scale)],
                   check=True, stdout=subprocess.DEVNULL)

def prepare():
    inputs=ART/'filter-input'; inputs.mkdir(parents=True,exist_ok=True)
    jobs=[]
    for key in KEYS:
        data=(PREVIOUS/'sources'/f'{key}.spr').read_bytes()
        indices=decode(data)
        body=colored(indices,(256,488),palette(data))
        body.save(inputs/f'{key}.png')
        # Portrait is its own image, not processed with body palette or tiles.
        face_indices=[indices[y*256+x] for y in range(456,488) for x in range(80,128)]
        face=colored(face_indices,(48,32),palette(data,8),True).transpose(Image.Transpose.ROTATE_90)
        face.save(inputs/f'{key}.portrait.png')
        for method in METHODS:
            out=ART/'filters'/method/f'{key}.png'; out.parent.mkdir(parents=True,exist_ok=True)
            jobs.append((inputs/f'{key}.png',out,method,2))
        for method in ('NearestNeighbor','Scale2x','HQ2x'):
            out=ART/'portraits'/method/f'{key}.png'; out.parent.mkdir(parents=True,exist_ok=True)
            jobs.append((inputs/f'{key}.portrait.png',out,method,4))
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(run_filter,jobs))
    reference=ART/'native-reference'; reference.mkdir(parents=True,exist_ok=True)
    rawroot=ROOT/'game-extract/.FFTSpriteToolkit/extract/SPRITETIC'
    unit=ROOT/'game-extract/.FFTSpriteToolkit/data/enhanced/extracted/fftpack/unit'
    metrics={}
    for gender,first,name in [('m',1000,'knight_m'),('f',1002,'knight_w')]:
        raw=(rawroot/f'sprite.{first}.gz').read_bytes()+(rawroot/f'sprite.{first+1}.gz').read_bytes()
        indices=[v for b in raw for v in (b&15,b>>4)]
        assert len(indices)==512*976
        native=colored(indices,(512,976),palette((unit/f'battle_{name}_spr.bin').read_bytes()))
        native.save(reference/f'{gender}.png')
        metrics[gender]=dict(nonuniform2x2Blocks=sum(len({indices[y*512+x],indices[y*512+x+1],indices[(y+1)*512+x],indices[(y+1)*512+x+1]})>1
            for y in range(0,912,2) for x in range(0,512,2)))
    qa=ART/'qa'; qa.mkdir(parents=True,exist_ok=True)
    selected=[1,6,19,24,31,54,67,85,125,170,212,310]
    for key in KEYS:
        colors=palette((PREVIOUS/'sources'/f'{key}.spr').read_bytes())
        images=[]
        for method in METHODS:
            filtered=Image.open(ART/'filters'/method/f'{key}.png').convert('RGBA')
            indices=indices_for(filtered,colors)
            quantized=colored(indices,filtered.size,colors)
            target=ART/'filters'/method/f'{key}.4bpp.png'; quantized.save(target)
            (ART/'filters'/method/f'{key}.indices').write_bytes(indices)
            images.append(quantized)
        assert images[2].tobytes()==images[3].tobytes(), 'Toolkit xBR2x changed implementation'
        # In the supplied Toolkit version XBR2x directly calls HQ2x.
        board=Image.new('RGB',(1000,1650),(46,49,57)); draw=ImageDraw.Draw(board)
        labels=('Native Knight enhanced','Previous / nearest','Toolkit Scale2x','Toolkit HQ2x','Toolkit xBR2x')
        columns=[Image.open(reference/f'{key[-1]}.png').convert('RGBA')]+images
        for col,label in enumerate(labels): draw.text((col*200+8,10),label,fill='white')
        for row,fid in enumerate(selected):
            for col,sheet in enumerate(columns):
                frame=render2(sheet,LAYOUT['frames'][fid])
                # Original physical resolution, nearest enlargement for viewing only.
                board.paste(frame,(col*200+20,row*135+30),frame)
            draw.text((2,row*135+144),f'frame {fid}',fill='white')
        board.save(qa/f'{key}.comparison.png')
    portrait_board=Image.new('RGB',(720,880),(46,49,57)); draw=ImageDraw.Draw(portrait_board)
    for row,key in enumerate(KEYS):
        for col,method in enumerate(('NearestNeighbor','Scale2x','HQ2x')):
            face=Image.open(ART/'portraits'/method/f'{key}.png').convert('RGBA')
            assert face.size==(128,192)
            draw.text((col*240+10,row*220+8),f'{key} / {method}',fill='white')
            portrait_board.paste(face,(col*240+56,row*220+25),face)
    portrait_board.save(qa/'portrait-comparison.png')
    report=dict(toolkitCode='Linked, unmodified local ImageProcessor.cs and UpscaleMethod.cs',
        xBR2xEqualsHQ2x=True, reference='Original enhanced game G2D entries 1000..1003',
        nativeReferenceMetrics=metrics, methods=list(METHODS),
        palettePolicy='Original SPR body palette; closest color for interpolated RGB; transparent alpha below 128')
    (ART/'comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__': prepare()

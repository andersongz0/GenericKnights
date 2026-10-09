"""Read-only native SPR/SHP/SEQ inspection. Outputs evidence, not replacement art."""
from pathlib import Path
import csv, hashlib, json, re, struct
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
UNIT = ROOT / 'game-extract/.FFTSpriteToolkit/data/enhanced/extracted/fftpack/unit'
OUT = ROOT / 'art-v2/native-reference'
SRC = ROOT / 'toolkit-source/FFTSpriteToolkit.Animation'
SIZES = [(8,8),(16,8),(16,16),(16,24),(24,8),(24,16),(24,24),(32,8),
         (32,16),(32,24),(32,32),(32,40),(48,16),(40,32),(48,48),(56,56)]

def decode(data):
    pixels = [v for b in data[512:37376] for v in (b & 15,b >> 4)]
    stream = [v for b in data[37376:] for v in (b >> 4,b & 15)]
    tail, pos = [], 0
    while len(tail) < 51200:
        v = stream[pos]; pos += 1
        if v: tail.append(v); continue
        n = stream[pos]; pos += 1
        if n == 0: n = stream[pos]; pos += 1
        elif n == 7: n = stream[pos] | stream[pos+1]<<4; pos += 2
        elif n == 8: n = stream[pos] | stream[pos+1]<<4 | stream[pos+2]<<8; pos += 3
        assert n > 0
        tail.extend([0]*n)
    assert len(tail) == 51200
    pixels += [v for i in range(0,len(tail),2) for v in (tail[i+1],tail[i])]
    # Convert native middle-portrait order to editor/G2D order.
    return pixels[:65536] + pixels[73728:] + pixels[65536:73728]

def sprite(name):
    data = (UNIT / f'battle_{name}_spr.bin').read_bytes()
    indices = decode(data)
    im = Image.new('RGBA',(256,488))
    def color(index, face=False):
        v = struct.unpack_from('<H',data,(128 if face else 0)*2 + index*2)[0]
        return ((v & 31)*255//31,((v>>5)&31)*255//31,((v>>10)&31)*255//31,255 if index else 0)
    im.putdata([color(v,80 <= i%256 < 128 and i//256 >=456) for i,v in enumerate(indices)])
    return im

def u32(data,off): return struct.unpack_from('<I',data,off)[0]
def shapes(kind):
    data = (UNIT / f'battle_{kind}_shp.bin').read_bytes()
    section = u32(data,0); boundary = struct.unpack_from('<H',data,4)[0]
    frames=[]
    for start,base in [(8,1034)] + ([(section+4,section+1026)] if section>8 else []):
        j=0
        while True:
            off=u32(data,start+4*j)
            if j and off==0: break
            off += base
            assert off+2 < len(data)
            tiles=[]
            for k in range((data[off]&7)+1):
                dx,dy,flags=struct.unpack_from('<bbH',data,off+2+4*k)
                x=(flags&31)*8; y=((flags>>5)&31)*8 + (256 if j>=boundary else 0)
                w,h=SIZES[(flags>>10)&15]
                assert x+w<=256 and y+h<=488, (kind,j,x,y,w,h)
                tiles.append(dict(rect=[x,y,w,h],position=[dx,dy],flipX=bool(flags&0x4000),flipY=bool(flags&0x8000)))
            frames.append(dict(frame=len(frames),tiles=list(reversed(tiles))))
            j+=1
    return frames

def sequences(kind):
    data=(UNIT / f'battle_{kind}_seq.bin').read_bytes()
    pointers=[]
    for i in range(256):
        p=u32(data,4+4*i)
        if p==0xffffffff: break
        pointers.append(p)
    code=(SRC/'SeqFileParser.cs').read_text()
    code=code.split('private static Dictionary<int, string> BuildType1Names()')[1]
    names={int(a):b for a,b in re.findall(r'\[(\d+)\] = "([^"]+)"',code.split('private static')[0])}
    ops={int(a):int(b) for a,b in re.findall(r'\{ (\d+), (\d+) \}',(SRC/'AnimationOpcode.cs').read_text())}
    result=[]
    for i,p in enumerate(pointers):
        end=1030+(pointers[i+1] if i+1<len(pointers) else len(data)-1030)
        pos=1030+p; frames=[]; offset=0
        while pos+1<min(end,len(data)):
            a,b=data[pos:pos+2]; pos+=2
            if a !=255: frames.append(dict(frame=a+offset,delay=b)); continue
            count=ops.get(b,0); args=list(data[pos:pos+count]); pos+=count
            if b==216 and args: offset=args[0] if args[0]<128 else args[0]-256
            if b==254: break
        result.append(dict(animation=i,name=names.get(i,f'Anim {i:03}'),frames=frames))
    return result

def render_frame(sheet,frame):
    im=Image.new('RGBA',(80,80))
    for tile in frame['tiles']:
        x,y,w,h=tile['rect']; crop=sheet.crop((x,y,x+w,y+h))
        if tile['flipX']: crop=crop.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if tile['flipY']: crop=crop.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        dx,dy=tile['position']; im.alpha_composite(crop,(40+dx,60+dy))
    return im

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    frames=shapes('type1'); seq=sequences('type1')
    usages={i:[] for i in range(len(frames))}
    for anim in seq:
        for part in anim['frames']:
            if part['frame'] in usages: usages[part['frame']].append(anim['name'])
    rects={}
    for frame in frames:
        frame['uses']=sorted(set(usages[frame['frame']]))
        for tile in frame['tiles']:
            key=tuple(tile['rect']); entry=rects.setdefault(key,dict(rect=list(key),frames=[],uses=[]))
            entry['frames'].append(frame['frame']); entry['uses']+=frame['uses']
    tiles=[]
    for i,entry in enumerate(sorted(rects.values(),key=lambda e:(e['rect'][1],e['rect'][0],e['rect'][2:]))):
        entry['id']=i; entry['frames']=sorted(set(entry['frames'])); entry['uses']=sorted(set(entry['uses']))
        entry['semanticStatus']='Exact native rectangle and animation uses; body-part labels require visual inspection.'
        tiles.append(entry)
    # Visual annotation of ALL 201 unique crops in the original Knight sheets.
    # A crop can contain a head/torso subset of an overlapping full-body pose.
    groups={
        'full_body': [2,4,6,8,10,12,14,21,22,24,26,28,30,32,33,35,41,60,70,73,74,82,96,101,102,111,117],
        'head_face_hair_nape': [0,1,3,5,7,9,11,13,15,16,17,20,23,25,27,29,31,34,36,40,107,120,123,163,175],
        'legs_lower_body': [18,37,38,80,86],
        'torso_shoulder_neck': [19,39,79,83,84,85,89,90,91,92,93,94,97,98,99,100,103,104,105,106,109,110,112,114,116,118,119,121,122,132,133,134,152,153,162,168,173,174,179,189,190,195,196,197,198,199],
        'fallen_or_horizontal_body': [75,76,87,88,95,113,115],
        'arm_forearm_hand': [*range(42,60),*range(61,70),71,72,77,78,81,*range(124,132),*range(135,152),*range(154,162),*range(164,168),*range(169,173),*range(176,179),*range(180,189),194,200],
        'thin_edge_or_empty_crop': [108,191,192,193],
    }
    roles={tile:role for role, ids in groups.items() for tile in ids}
    assert set(roles)==set(range(len(tiles))),set(range(len(tiles)))-set(roles)
    for entry in tiles:
        entry['bodyPart']=roles[entry['id']]
        entry['semanticStatus']='Body part visually annotated on native Knight sheets; animation names are toolkit labels, not guessed per-cell actions.'
    for name in ['knight_m','knight_w','syou_m','syou_w']:
        sheet=sprite(name); sheet.save(OUT/f'{name}.png')
        sheet.resize((768,1464),Image.Resampling.NEAREST).save(OUT/f'{name}.3x.png')
        # Every native assembled frame, not a fictitious regular pose grid.
        contact=Image.new('RGB',(800,((len(frames)+9)//10)*90),(46,49,57)); draw=ImageDraw.Draw(contact)
        for i,frame in enumerate(frames):
            crop=render_frame(sheet,frame); xx=(i%10)*80; yy=(i//10)*90
            contact.paste(crop,(xx,yy),crop); draw.text((xx+2,yy+77),str(i),fill='white')
        contact.save(OUT/f'{name}.assembled.png')
    sheet=sprite('knight_m')
    for page in range((len(tiles)+59)//60):
        contact=Image.new('RGB',(900,600),(46,49,57)); draw=ImageDraw.Draw(contact)
        for k,entry in enumerate(tiles[page*60:(page+1)*60]):
            x,y,w,h=entry['rect']; crop=sheet.crop((x,y,x+w,y+h)).resize((w*2,h*2),Image.Resampling.NEAREST)
            xx=(k%10)*90; yy=(k//10)*100
            contact.paste(crop,(xx,yy),crop); draw.text((xx+1,yy+82),f"{entry['id']} {x},{y}",fill='white')
        contact.save(OUT/f'tiles-{page:02}.png')
    evidence=dict(schema=1,templateShapes=[100,101],sheetSize=[256,488],portraitRect=[80,456,48,32],
        note='SHP crop rectangles can overlap. There is no uniform whole-body cell grid. Preserve source coordinates, destination offsets, flips and native SEQ.',
        frames=frames,sequences=seq,tiles=tiles,
        inputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [UNIT/'battle_type1_shp.bin',UNIT/'battle_type1_seq.bin',UNIT/'battle_knight_m_spr.bin',UNIT/'battle_knight_w_spr.bin']})
    (OUT/'native-layout.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
    with (OUT/'native-tiles.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.writer(f); writer.writerow(['tile','x','y','width','height','frames','animation_uses'])
        for e in tiles: writer.writerow([e['id'],*e['rect'],' '.join(map(str,e['frames'])),'; '.join(e['uses'])])
    print(f'{len(frames)} assembled SHP frames; {len(tiles)} unique source rectangles; {len(seq)} SEQ entries. Evidence: {OUT}')

if __name__=='__main__': main()

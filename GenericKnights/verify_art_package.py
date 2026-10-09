"""Independent read-only checks of candidate SPR/G2D/UI assets. No game launch."""
from pathlib import Path
import ast, hashlib, json, shutil, struct, subprocess, sys
from PIL import Image, ImageDraw
from analyze_native_art import decode, ROOT

ART=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'art-v2'
MOD=ART/'Mod'
WORKSPACE=ROOT.parent
CLI=WORKSPACE/'FF16 Tools/win-x64/FF16Tools.CLI.exe'
DDS=ROOT/'dds-preview/bin/Debug/net9.0-windows/DdsPreview.dll'
OUT=ART/'qa/package'
OUT.mkdir(parents=True,exist_ok=True)

def verify_texture(tex, expected):
    copy=OUT/tex.name
    shutil.copyfile(tex,copy)
    subprocess.run([str(CLI),'tex-conv','-i',str(copy)],check=True,stdout=subprocess.DEVNULL)
    dds=copy.with_suffix('.dds'); png=copy.with_suffix('.png')
    assert dds.exists()
    subprocess.run(['dotnet',str(DDS),str(dds),str(png)],check=True,stdout=subprocess.DEVNULL)
    actual=Image.open(png).convert('RGBA')
    # Pillow treats uncompressed BI_RGB 32-bit BMP alpha as unused. Read the
    # original BGRA bytes directly, including alpha written by System.Drawing.
    data=Path(expected).read_bytes(); offset=struct.unpack_from('<I',data,10)[0]
    width,height=struct.unpack_from('<ii',data,18)
    assert struct.unpack_from('<H',data,28)[0]==32
    rows=[data[offset+y*width*4:offset+(y+1)*width*4] for y in range(abs(height))]
    if height>0: rows.reverse()
    bgra=b''.join(rows)
    rgba=bytes(v for i in range(0,len(bgra),4) for v in (bgra[i+2],bgra[i+1],bgra[i],bgra[i+3]))
    assert actual.size==(width,abs(height)),(tex.name,actual.size,(width,abs(height)))
    assert actual.tobytes()==rgba,f'Texture round-trip differs: {tex.name}'
    return actual.size

def main():
    # Reuse the existing independent portrait-coordinate oracle, without
    # importing its unrelated executable-disassembly startup code.
    source=WORKSPACE/'FFTModLoader_Prototype_v0.10.30/tools/verify_visual_expansion.py'
    tree=ast.parse(source.read_text())
    func=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='verify_portrait')
    namespace=dict(WORKSPACE=WORKSPACE,struct=struct)
    exec(compile(ast.Module(body=[func],type_ignores=[]),str(source),'exec'),namespace)
    oracle=namespace['verify_portrait']
    entries=json.loads((MOD/'FFTModLoader.visuals.json').read_text())['Entries']
    filter_manifest_path=ART/'enhanced-filter.json'
    filter_manifest=json.loads(filter_manifest_path.read_text()) if filter_manifest_path.exists() else None
    results=[]
    for entry in entries:
        shape=entry['ShapeId']; gender='Male' if entry['Gender']=='male' else 'Female'
        folder,base=('holy',f'HolyKnight {gender}') if entry['JobId']==162 else ('rune',f'Rune Knight {gender}')
        bmp=ART/folder/(base+'.BMP'); image=Image.open(bmp)
        assert image.mode=='P' and image.size==(256,488)
        expected=bytes(v&15 for v in image.get_flattened_data())
        spr=(MOD/entry['Spr']).read_bytes()
        assert len(spr)<=45056,(base,len(spr))
        assert bytes(decode(spr))==expected,f'SPR pixel mismatch: {base}'
        palette=image.getpalette()
        native_source=ART/'sources'/Path(entry['Spr']).name
        native=native_source.read_bytes() if native_source.exists() else None
        if native is not None:
            assert bytes(decode(native))==expected, f'User source pixel mismatch: {base}'
            assert spr[:512]==native[:512], f'User source palette mismatch: {base}'
            for index in range(256):
                r,g,b=palette[index*3:index*3+3]
                assert (r>>3)|((g>>3)<<5)|((b>>3)<<10)==struct.unpack_from('<H',native,index*2)[0]&0x7fff
        for slot in range(16):
            for color in range(16):
                if native is not None:
                    continue  # All 16 original slots were verified above.
                index=(128 if slot>=8 else 0)+color
                r,g,b=palette[index*3:index*3+3]
                rgb555=(r>>3)|((g>>3)<<5)|((b>>3)<<10)
                assert struct.unpack_from('<H',spr,slot*32+color*2)[0]==rgb555
        for start,key in ((0,'TopPage'),(256,'BottomPage')):
            data=(MOD/entry[key]).read_bytes()
            assert len(data)==131072
            if filter_manifest:
                asset_key=Path(entry['Spr']).stem
                method=filter_manifest['bodyMethod']
                pixels=(ART/'filters'/method/(asset_key+'.indices')).read_bytes()
                assert len(pixels)==512*976 and max(pixels)<=15
                page=pixels[start*1024:(start+256)*1024]
                page=page+bytes(512*512-len(page))
                packed=bytes(page[i]|(page[i+1]<<4) for i in range(0,len(page),2))
                assert data==packed, f'Enhanced filter G2D mismatch: {base}/{key}'
                continue
            for y in range(256):
                indices=expected[(start+y)*256:(start+y+1)*256] if start+y<488 else bytes(256)
                row=bytes(v|(v<<4) for v in indices)
                assert data[y*512:(y+1)*512]==row+row
        face=f'wldface_{shape}_08_uitx'
        face_tex=MOD/f'FFTIVC/data/enhanced/ui/ffto/common/face/texture/{face}.tex'
        hd_expected=ART/f'ui-review/{face}.bmp'
        if hd_expected.exists():
            # These v4 costume variants must survive 15-color quantization;
            # brown/skin colors alone are not a valid female Rune export.
            def accent(index):
                r,g,b=palette[index*3:index*3+3]
                return (b>r*1.15 and b>g*1.15) if entry['Gender']=='male' else (r>g*1.1 and b>=g*.95 and r>64)
            if native is None:
                accent_pixels=sum(accent(v) for v in expected[:65536] if v)
                assert accent_pixels>=35,(base,'costume accent lost',accent_pixels)
            # HD menu art is intentionally NOT an enlarged SPR fallback face.
            # Verify actual pixels, all eight native crop coordinates and the
            # binary coordinate records independently, instead of skipping QA.
            verify_texture(face_tex,hd_expected)
            actual=Image.open(OUT/f'{face}.png').convert('RGBA')
            key=f"{folder}-{entry['Gender'][0]}"
            tile=Image.open(ART/f'ui-review/{key}.128x192.png').convert('RGBA')
            assert actual.size==(520,388) and tile.size==(128,192)
            for y in (1,195):
                for x in (1,131,261,391):
                    assert actual.crop((x,y,x+128,y+192)).tobytes()==tile.tobytes()
            for point in [(0,0),(0,200),(129,80),(259,80),(519,387)]:
                assert actual.getpixel(point)[3]==0
            template_shape={170:159,171:160,172:161,173:162}[shape]
            template=WORKSPACE/f'Nexus Mods/Generic Jobs/Mod Generic Jobs/FFTIVC/data/enhanced/ui/ffto/common/face/textureparts/wldface_{template_shape}_08_uitx.utexpt'
            expected_parts=template.read_bytes().replace(f'wldface_{template_shape}_08_uitx.tex'.encode(),f'{face}.tex'.encode())
            parts=(MOD/f'FFTIVC/data/enhanced/ui/ffto/common/face/textureparts/{face}.utexpt').read_bytes()
            assert parts==expected_parts and len(parts)==310
        else:
            oracle(MOD,shape,bmp,456)
            verify_texture(face_tex,ROOT/f'face-build/{face}.bmp')
        visual=f"jv_{22 if entry['JobId']==162 else 23}_{entry['Gender'][0]}_uitx"
        visual_expected=ART/f'ui-review/{visual}.bmp' if filter_manifest else ROOT/f'jobvisual-build/{visual}.bmp'
        verify_texture(MOD/f'FFTIVC/data/enhanced/ui/ffto/icon/job_visual/texture/{visual}.tex',visual_expected)
        results.append(dict(name=base,shape=shape,sprBytes=len(spr),sha256=hashlib.sha256(spr).hexdigest(),roundTrip=True,
                            userSourcePixelsAndAllPalettesPreserved=native is not None))
    for job in (162,163):
        icon=f'j_{job}_uitx'
        icon_expected=ART/f'ui-review/{icon}.bmp' if filter_manifest else ROOT/f'jobvisual-build/{icon}.bmp'
        size=verify_texture(MOD/f'FFTIVC/data/enhanced/ui/ffto/icon/job/texture/{icon}.tex',icon_expected)
        assert size==(60,60)
        template=WORKSPACE/'Nexus Mods/Generic Jobs/Mod Generic Jobs/FFTIVC/data/enhanced/ui/ffto/icon/job/textureparts/j_160_uitx.utexpt'
        parts=(MOD/f'FFTIVC/data/enhanced/ui/ffto/icon/job/textureparts/{icon}.utexpt').read_bytes()
        assert parts==template.read_bytes().replace(b'j_160_uitx.tex',f'{icon}.tex'.encode())
    # Gameplay data and live original art remain separate from the candidate.
    for old in (ROOT/'Mod').rglob('*'):
        if old.is_file() and old.suffix in ('.nxd','.xml'):
            assert old.read_bytes()==(MOD/old.relative_to(ROOT/'Mod')).read_bytes()
    report=dict(status='offline-format-checks-pass',assets=results,uiTextureRoundTrips=10,
        enhancedFilter=filter_manifest,
        limitation='Native packing verified, not an in-game animation/style approval. See per-crop QA and README.')
    (ART/'qa/package-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    # Read-only visual proof of the validated native pixels, not new artwork.
    board=Image.new('RGB',(960,580),(46,49,57)); draw=ImageDraw.Draw(board)
    for i,(folder,base,label) in enumerate((('holy','HolyKnight Male','Holy Knight M'),('holy','HolyKnight Female','Holy Knight F'),('rune','Rune Knight Male','Rune Knight M'),('rune','Rune Knight Female','Rune Knight F'))):
        bmp=Image.open(ART/folder/(base+'.BMP')); palette=bmp.getpalette()
        im=Image.new('RGBA',bmp.size)
        im.putdata([(*palette[v*3:v*3+3],255 if v else 0) for v in bmp.get_flattened_data()])
        pose=im.crop((0,0,32,40)).resize((192,240),Image.Resampling.NEAREST)
        if filter_manifest:
            asset_key=f"{folder}_{'m' if base.endswith('Male') else 'f'}"
            pose=Image.open(ART/'filters'/filter_manifest['bodyMethod']/(asset_key+'.4bpp.png')).convert('RGBA').crop((0,0,64,80)).resize((192,240),Image.Resampling.NEAREST)
        hd_face=ART/f"ui-review/{folder}-{'m' if base.endswith('Male') else 'f'}.128x192.png"
        face=Image.open(hd_face).convert('RGBA') if hd_face.exists() else im.crop((80,456,128,488)).transpose(Image.Transpose.ROTATE_90).resize((128,192),Image.Resampling.NEAREST)
        draw.text((i*240+20,12),label,fill='white')
        board.paste(pose,(i*240+24,42),pose); board.paste(face,(i*240+56,310),face)
        icon=Image.open(ART/'icons'/('Holy Knight.png' if folder=='holy' else 'Rune Knight.png')).convert('RGBA')
        board.paste(icon,(i*240+90,514),icon)
    board.save(ART/'qa/preview.png')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()

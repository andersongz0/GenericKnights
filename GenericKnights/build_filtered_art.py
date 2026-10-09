"""Build an isolated enhanced-texture test using actual Toolkit filter outputs."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys
from PIL import Image, ImageDraw
from compare_toolkit_filters import ART, PREVIOUS, KEYS, LAYOUT, render2, palette, colored
from analyze_native_art import ROOT

CLI=ROOT.parent/'FF16 Tools/win-x64/FF16Tools.CLI.exe'
UI='FFTIVC/data/enhanced/ui/ffto'
GENDERS={'holy_m':170,'holy_f':171,'rune_m':172,'rune_f':173}

def tex(image, name, folder):
    bmp=ART/'ui-review'/(name+'.bmp'); image.save(bmp)
    subprocess.run([str(CLI),'img-conv','-i',str(bmp)],check=True,stdout=subprocess.DEVNULL)
    shutil.copyfile(bmp.with_suffix('.tex'), ART/'Mod'/UI/folder/(name+'.tex'))

def build():
    method='Scale2x'
    for folder in ('Mod','sources','holy','rune','icons'):
        shutil.copytree(PREVIOUS/folder,ART/folder,dirs_exist_ok=True)
    shutil.copyfile(PREVIOUS/'source-import.json',ART/'source-import.json')
    (ART/'ui-review').mkdir(parents=True,exist_ok=True)
    summary=[]
    for key in KEYS:
        indices=(ART/'filters'/method/(key+'.indices')).read_bytes()
        assert len(indices)==512*976 and max(indices)<=15
        for start,suffix in ((0,'top'),(512,'bottom')):
            page=indices[start*512:(start+512)*512]
            page+=bytes(512*512-len(page))
            packed=bytes(page[i]|(page[i+1]<<4) for i in range(0,len(page),2))
            assert len(packed)==131072
            (ART/'Mod/Visuals'/f'{key}_{suffix}.bin').write_bytes(packed)
        face=Image.open(ART/'portraits'/method/(key+'.png')).convert('RGBA')
        assert face.size==(128,192)
        face.save(ART/'ui-review'/(key.replace('_','-')+'.128x192.png'))
        atlas=Image.new('RGBA',(520,388))
        for y in (1,195):
            for x in (1,131,261,391): atlas.paste(face,(x,y))
        tex(atlas,f'wldface_{GENDERS[key]}_08_uitx','common/face/texture')
        sheet=Image.open(ART/'filters'/method/(key+'.4bpp.png')).convert('RGBA')
        # Same first pose and 400x652 job card geometry, now physical 2x art.
        pose=sheet.crop((0,0,64,80)).resize((320,400),Image.Resampling.NEAREST)
        card=Image.new('RGBA',(400,652));card.paste(pose,(40,126))
        job=22 if key.startswith('holy') else 23
        tex(card,f'jv_{job}_{key[-1]}_uitx','icon/job_visual/texture')
        # All 363 source rectangles, offsets and flips are unchanged; generate
        # assembled physical-resolution contact sheets for manual inspection.
        for start in range(0,len(LAYOUT['frames']),60):
            frames=LAYOUT['frames'][start:start+60]
            contact=Image.new('RGB',(960,((len(frames)+9)//10)*120),(46,49,57));draw=ImageDraw.Draw(contact)
            for k,frame in enumerate(frames):
                im=render2(sheet,frame)
                assert im.size==(160,160)
                im=im.resize((96,96),Image.Resampling.NEAREST)
                x=k%10*96;y=k//10*120;contact.paste(im,(x,y),im)
                draw.text((x+2,y+98),str(frame['frame']),fill='white')
            contact.save(ART/'qa'/f'{key}.enhanced-frames-{start:03}.png')
        nearest=(ART/'filters/NearestNeighbor'/(key+'.indices')).read_bytes()
        differences=sum(a!=b for a,b in zip(indices,nearest))
        source=(ART/'sources'/(key+'.spr')).read_bytes()
        spr=(ART/'Mod/Visuals'/(key+'.spr')).read_bytes()
        assert spr==(PREVIOUS/'Mod/Visuals'/(key+'.spr')).read_bytes()
        assert spr[:512]==source[:512]
        summary.append(dict(key=key,changedEnhancedPixels=differences,
            fallbackSprUnchanged=True,allSixteenPalettesUnchanged=True,
            assembledFrames=363,sourceCoordinatesAndOffsetsUnchanged=True))
    # Retained icons also get local expected-BMP copies, so verification is
    # independent of the shared build directories used by previous revisions.
    for job in (162,163):
        shutil.copyfile(ROOT/'jobvisual-build'/f'j_{job}_uitx.bmp',ART/'ui-review'/f'j_{job}_uitx.bmp')
    manifest=dict(bodyMethod=method,portraitMethod=method,bodyScale=2,portraitScale=4,
        physicalSheetSize=[512,976],pageSize=[512,512],palettePolicy='Original palettes; no new body colors',
        fallback='Original user SPR preserved byte-for-byte from art-v5',assets=summary)
    (ART/'enhanced-filter.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    config=ART/'Mod/ModConfig.json'; details=json.loads(config.read_text())
    details['ModVersion']='0.1.25-art-test'
    details['ModDescription']='User Holy/Rune sprites with Toolkit Scale2x enhanced textures and separately processed portraits. Original fallback SPR and palettes preserved; in-game test pending.'
    config.write_text(json.dumps(details,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,indent=2))

if __name__=='__main__': build()

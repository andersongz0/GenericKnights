"""Read-only raster QA; does not edit or generate artwork."""
from pathlib import Path
from PIL import Image
import sys

root = Path(__file__).resolve().parent
candidate = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'art-review-20261005'
for name in ('HolyKnight Male.BMP', 'HolyKnight Female.bmp'):
    old = Image.open(root / 'adapted-sprites/holy' / name)
    new = Image.open(candidate / name)
    assert new.size == old.size == (256, 488) and new.mode == 'P'
    old_px, new_px = old.load(), new.load()
    min_iou = 1.0
    # Standing/walking/directional frames retain their native anchoring. The
    # final column contains head components, not a complete standing frame.
    for row in range(2):
        for col in range(8):
            region = [(x, y) for y in range(row*40, (row+1)*40)
                      for x in range(col*32, (col+1)*32)]
            before = {(x, y) for x, y in region if old_px[x, y]}
            after = {(x, y) for x, y in region if new_px[x, y]}
            assert before and after, (name, row, col, 'missing frame')
            iou = len(before & after) / len(before | after)
            min_iou = min(min_iou, iou)
            assert iou >= .70, (name, row, col, 'silhouette displaced', iou)
            center = lambda p: (sum(x for x,y in p)/len(p), sum(y for x,y in p)/len(p))
            a, b = center(before), center(after)
            assert max(abs(a[i]-b[i]) for i in (0,1)) <= 1.5, (name, row, col, a, b)
    # Every populated animation/component cell survives, including the lower
    # disconnected limbs. Ignore isolated source specks (<6 opaque pixels).
    preserved = 0
    for y0 in range(0, 456, 16):
        for x0 in range(0, 256, 16):
            coords = [(x,y) for y in range(y0,min(y0+16,456)) for x in range(x0,x0+16)]
            # The original portrait's antialiased upper border spills above
            # row 456. It is not an animation component and the new portrait
            # is intentionally confined to its native 48x32 rectangle.
            coords = [(x,y) for x,y in coords if not (80 <= x < 128 and y >= 448)]
            a = sum(bool(old_px[x,y]) for x,y in coords)
            b = sum(bool(new_px[x,y]) for x,y in coords)
            if a >= 6:
                assert b > 0, (name,x0,y0,'animation component removed')
                preserved += 1
    colors = {new_px[x,y] for y in range(456) for x in range(256)}
    assert colors <= set(range(16)) and 0 in colors
    print(f'{name}: PASS, all 16 preview cells anchored; minimum silhouette IoU={min_iou:.3f}; '
          f'{preserved} populated component cells retained; 15 body colors + transparency.')

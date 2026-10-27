"""像素格共用函式:AI 生的場景對齊像素格、洋紅底素材表切塊去背。只用 Pillow + NumPy。

規格(整個 skill 都照這套,改了就會出現半格):
- 一格 6px;直式畫面 1080×1920 = 180×320 格
- 場景減到 96 色(48 色會把霓虹的粉紅、藍色吃掉)
- 角色 / 道具:透明 PNG、補一圈深色外框、高度用格數定,放大只能整數倍
"""
import numpy as np
from PIL import Image

CELL = 6
GW, GH = 180, 320
OUTLINE = (28, 22, 40)
MOSAICS = [(90, 160), (45, 80), (23, 40)]      # 「從馬賽克變清楚」進場用的三張更粗版本


def keymask(a):
    """純洋紅 #FF00FF(AI 生圖會有一點偏差,所以用範圍判斷)。"""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > 170) & (b > 170) & (g < 110) & (r - g > 100) & (b - g > 100)


def _fit(w, h):
    """高度對齊 320 格,寬度照比例後裁中間 180 格。回傳 (縮放後寬度, 左邊裁掉幾格)。"""
    sw = round(w * GH / h)
    return sw, (sw - GW) // 2


def scene(src, out, colors=96, mosaics=True, key=False):
    """直式場景(約 1024×1536)→ 180×320 格、colors 色 → 1080×1920 PNG(out + '.png')。
    key=True:洋紅那塊變透明(天空畫成洋紅,後面就能放星空、K 線、會動的東西)。
    回傳最上面不透明的那一列(px),key=False 時是 0。"""
    im = Image.open(src).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    keep = (~keymask(a)).astype(np.float32) if key else np.ones(a.shape[:2], np.float32)
    sw, x0 = _fit(im.width, im.height)

    def rs(arr):
        return np.asarray(Image.fromarray(arr).resize((sw, GH), Image.BOX), dtype=np.float32)[:, x0:x0 + GW]
    k = rs(keep)
    col = np.stack([rs(a[..., c] * keep) for c in range(3)], -1) / np.maximum(k, 1e-6)[..., None]
    opaque = k >= 0.5
    rgb = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))
    q = rgb.quantize(colors=colors, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).convert('RGB')
    if key:
        img = Image.fromarray(np.dstack([np.asarray(q), (opaque * 255).astype(np.uint8)]), 'RGBA')
    else:
        img = q
    img.resize((GW * CELL, GH * CELL), Image.NEAREST).save(out + '.png')
    if mosaics and not key:
        for i, (gw, gh) in enumerate(MOSAICS, 1):
            m = q.resize((gw, gh), Image.BOX).quantize(colors=32, dither=Image.Dither.NONE).convert('RGB')
            m.resize((GW * CELL, GH * CELL), Image.NEAREST).save(f'{out}_m{i}.png')
    rows = np.where(opaque.any(1))[0]
    return int(rows.min()) * CELL if len(rows) else 0


def _dilate(m, n):
    for _ in range(n):
        m = m | np.roll(m, 1, 0) | np.roll(m, -1, 0) | np.roll(m, 1, 1) | np.roll(m, -1, 1)
    return m


def _erode(m, n):
    for _ in range(n):
        m = m & np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1)
    return m


def components(mask, step=4, grow=3):
    """縮小 step 倍後膨脹 + 連通區塊標記(把放大鏡的鏡片和握把這類分開的小塊併在一起),回傳每塊在原圖的 bbox。"""
    h, w = mask.shape
    m = mask[:h - h % step, :w - w % step].reshape(h // step, step, w // step, step).any(axis=(1, 3))
    d = _dilate(m.copy(), grow)
    lab = np.zeros(d.shape, int)
    n = 0
    for y in range(d.shape[0]):
        for x in range(d.shape[1]):
            if d[y, x] and not lab[y, x]:
                n += 1
                stack = [(y, x)]
                lab[y, x] = n
                while stack:
                    cy, cx = stack.pop()
                    for yy, xx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                        if 0 <= yy < d.shape[0] and 0 <= xx < d.shape[1] and d[yy, xx] and not lab[yy, xx]:
                            lab[yy, xx] = n
                            stack.append((yy, xx))
    boxes = []
    for i in range(1, n + 1):
        ys, xs = np.where((lab == i) & m)
        if len(ys):
            boxes.append([ys.min() * step, xs.min() * step, (ys.max() + 1) * step, (xs.max() + 1) * step, len(ys)])
    return boxes


def order(boxes, rows, cols):
    """只留最大的 rows*cols 塊(去掉雜點),照「由上到下分列、每列由左到右」排。"""
    boxes = sorted(boxes, key=lambda b: -b[4])[:rows * cols]
    boxes.sort(key=lambda b: (b[0] + b[2]) / 2)
    out = []
    for r in range(rows):
        out += sorted(boxes[r * cols:(r + 1) * cols], key=lambda b: (b[1] + b[3]) / 2)
    return out


def grid_boxes(keep, rows, cols):
    """照格子切:每一格裡非洋紅的範圍當一塊(角色上下靠太近、連通區塊會黏在一起時用)。"""
    keep = _dilate(_erode(keep, 1), 1)          # 去掉零星雜點
    h, w = keep.shape
    out = []
    for r in range(rows):
        for c in range(cols):
            y0, y1, x0, x1 = r * h // rows, (r + 1) * h // rows, c * w // cols, (c + 1) * w // cols
            ys, xs = np.where(keep[y0:y1, x0:x1])
            if not len(ys):
                raise ValueError(f'第 {r + 1} 列第 {c + 1} 格是空的')
            out.append([y0 + ys.min(), x0 + xs.min(), y0 + ys.max() + 1, x0 + xs.max() + 1, len(ys)])
    return out


def pixelize(a, keep, H, colors=40):
    """一塊素材 → 高 H 格、補一圈外框、每格放大成 6px 的透明 PNG。"""
    h, w = keep.shape
    W = max(1, round(w * H / h))

    def rs(arr):
        return np.asarray(Image.fromarray(arr.astype(np.float32)).resize((W, H), Image.BOX), dtype=np.float32)
    k = rs(keep.astype(np.float32))
    col = np.stack([rs(a[..., c] * keep) for c in range(3)], -1) / np.maximum(k, 1e-6)[..., None]
    op = k >= 0.5
    rgb = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))
    q = np.asarray(rgb.quantize(colors=colors, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).convert('RGB'))
    q = np.pad(q, ((1, 1), (1, 1), (0, 0)))
    op = np.pad(op, 1)
    edge = ~op & (np.roll(op, 1, 0) | np.roll(op, -1, 0) | np.roll(op, 1, 1) | np.roll(op, -1, 1))
    q[edge] = OUTLINE
    alpha = ((op | edge) * 255).astype(np.uint8)
    img = Image.fromarray(np.dstack([q, alpha]), 'RGBA')
    return img.resize((img.width * CELL, img.height * CELL), Image.NEAREST)


def cut_sheet(src, rows, cols, items, outdir, grid=False):
    """items:[{name, h(格), group?}];同一 group 以組內最高的那塊為 h,其他照同比例(同一角色不同動作一樣大)。
    回傳 [(name, PIL.Image)]。"""
    a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
    keep = ~keymask(a)
    boxes = grid_boxes(keep, rows, cols) if grid else order(components(keep), rows, cols)
    if len(boxes) != len(items):
        raise ValueError(f'{src}:切出 {len(boxes)} 塊,jobs.json 寫了 {len(items)} 個名字'
                         '(素材黏在一起就加 "grid": true;多出雜點就檢查洋紅背景)')
    gmax = {}
    for (y0, _, y1, _, _), it in zip(boxes, items):
        if it.get('group'):
            gmax[it['group']] = max(gmax.get(it['group'], 0), y1 - y0)
    out = []
    for (y0, x0, y1, x1, _), it in zip(boxes, items):
        g = it.get('group')
        H = round((y1 - y0) * it['h'] / gmax[g]) if g else it['h']
        img = pixelize(a[y0:y1, x0:x1], keep[y0:y1, x0:x1], max(4, H))
        img.save(f"{outdir}/{it['name']}.png")
        out.append((it['name'], img))
    return out


def preview(ims, path, bg=(11, 13, 31, 255)):
    """把切好的素材排成一張橫條,方便一眼檢查。"""
    W = sum(i.width for _, i in ims) + 20 * (len(ims) + 1)
    pv = Image.new('RGBA', (W, max(i.height for _, i in ims) + 40), bg)
    x = 20
    for _, i in ims:
        pv.alpha_composite(i, (x, 20))
        x += i.width + 20
    pv.save(path)

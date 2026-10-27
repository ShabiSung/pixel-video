"""素材處理:assets/gen/ 的 AI 原圖 → 對齊 6px 像素格的 PNG(assets/img/)。

    python tools/process.py           # 全部
    python tools/process.py hero      # 只處理這幾張

- scene → assets/img/bg_<id>.png(180×320 格、96 色)+ bg_<id>_m1..m3.png(「從馬賽克變清楚」進場用)
- sheet → 每個 item 一張透明 PNG(assets/img/<name>.png),外加 assets/img/_<id>_preview.png 一眼檢查
跑完一定要打開 _preview 看:有沒有切歪、少一塊、把兩個黏成一個。
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8')
import pxlib

GEN = os.path.join(ROOT, 'assets', 'gen')
IMG = os.path.join(ROOT, 'assets', 'img')


def main():
    args = sys.argv[1:]
    jobs = json.load(open(os.path.join(ROOT, 'jobs.json'), encoding='utf-8'))['jobs']
    os.makedirs(IMG, exist_ok=True)
    missing = []
    for job in jobs:
        if args and job['id'] not in args:
            continue
        src = os.path.join(GEN, job['id'] + '.png')
        if not os.path.exists(src):
            missing.append(job['id'])
            continue
        if job['kind'] == 'scene':
            top = pxlib.scene(src, os.path.join(IMG, 'bg_' + job['id']), colors=job.get('colors', 96), key=job.get('key', False))
            print(f'· 場景 bg_{job["id"]}.png' + (f'(透明天空到 y={top})' if job.get('key') else ''))
        else:
            ims = pxlib.cut_sheet(src, job['rows'], job['cols'], job['items'], IMG, grid=job.get('grid', False))
            pv = os.path.join(IMG, f'_{job["id"]}_preview.png')
            pxlib.preview(ims, pv)
            print(f'· 素材表 {job["id"]}:{len(ims)} 個 → ' + '、'.join(f'{n}({i.width}×{i.height})' for n, i in ims))
            print(f'  檢查 {os.path.relpath(pv, ROOT)}')
    if missing:
        print('還沒有原圖(先跑 python tools/gen.py):' + '、'.join(missing))


if __name__ == '__main__':
    main()

"""專案初始化:下載渲染要用的 GSAP 到 assets/js/(只下載一次),建好資料夾。

    python tools/setup.py

會下載 1 個檔(約 70 KB,來源 cdn.jsdelivr.net):
  assets/js/gsap.min.js   GSAP 3.14.2(動畫引擎,GreenSock 標準授權,免費)

字型已經附在 assets/fonts/(俐方體 11 號 Cubic 11、Press Start 2P,都是 SIL Open Font License),不用另外下載。
"""
import os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(HERE))
sys.stdout.reconfigure(encoding='utf-8')

FILES = [('assets/js/gsap.min.js', 'https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js')]

for path, url in FILES:
    if os.path.exists(path):
        print(f'· 已有 {path}'); continue
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with urllib.request.urlopen(url, timeout=30) as r:
        data = r.read()
    open(path, 'wb').write(data)
    print(f'· {path}  {len(data) // 1024} KB  ← {url}')
for d in ('assets/gen', 'assets/img', 'assets/audio', 'renders'):
    os.makedirs(d, exist_ok=True)
print('完成。接著 python tools/gen.py 生圖(或照它印的提示詞貼到 ChatGPT)')

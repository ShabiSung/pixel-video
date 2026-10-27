"""生圖:照 jobs.json 產提示詞。電腦上有 Codex CLI 就直接叫它生,沒有就把提示詞存成檔案,請使用者貼到 ChatGPT。

    python tools/gen.py               # 生 assets/gen/ 裡還沒有的圖
    python tools/gen.py hero props    # 只生這幾張(已經有的會蓋掉)
    python tools/gen.py --prompts     # 只寫提示詞,不叫 Codex

生出來的圖存成 assets/gen/<id>.png;提示詞一律留一份 assets/gen/_prompt_<id>.txt。
Codex 的位置:環境變數 CODEX_BIN > Windows 的 Codex App 內建版 > PATH 上的 codex。
"""
import glob, json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GEN = os.path.join(ROOT, 'assets', 'gen')
sys.stdout.reconfigure(encoding='utf-8')

SCENE_STYLE = ('16-bit retro game pixel art (SNES era), portrait orientation 1024x1536, crisp hard-edged pixels, '
               'no anti-aliasing, limited palette, rich colors on a darker background. '
               'NO characters, NO people, NO animals, NO text, NO letters, NO numbers, NO logos, NO watermark.')
KEY_SKY = ('The whole sky / background area above the scenery must be ONE perfectly flat, solid, pure magenta color (#FF00FF) '
           'with no stars, clouds or gradient; it will be removed later.')
SHEET_STYLE = ('16-bit retro game pixel art sprite sheet (SNES style), landscape orientation 1536x1024, crisp hard-edged pixels, '
               'no anti-aliasing, limited palette, each sprite has a dark 1-pixel outline. The ENTIRE background must be one '
               'perfectly flat, solid, pure magenta color (#FF00FF): no gradient, no floor, no ground shadows, no grid lines, '
               'no borders, no frames, no labels, NO text, NO letters, NO numbers, NO logos, NO watermark. '
               'Sprites must not touch each other; leave wide magenta gaps between them. The magenta will be removed later.')


def prompt(job):
    if job['kind'] == 'scene':
        body = job['prompt'] + (' ' + KEY_SKY if job.get('key') else '')
        return f'{SCENE_STYLE}\n\n{body}'
    n = len(job['items'])
    lines = [f'{SHEET_STYLE}', '',
             f'Arrange exactly {n} sprites in a grid of {job["rows"]} rows x {job["cols"]} columns, '
             'in reading order (left to right, then the next row), all evenly spaced:']
    if job.get('note'):
        lines.insert(1, '\n' + job['note'])
    lines += [f'{i}. {it["d"]}' for i, it in enumerate(job['items'], 1)]
    return '\n'.join(lines)


def find_codex():
    if os.environ.get('CODEX_BIN'):
        return os.environ['CODEX_BIN']
    la = os.environ.get('LOCALAPPDATA')
    if la:
        c = sorted(glob.glob(os.path.join(la, 'OpenAI', 'Codex', 'bin', '*', 'codex.exe')), key=os.path.getmtime)
        if c:
            return c[-1]
    return shutil.which('codex')


def run_codex(codex, job, text, out):
    ask = (f'Use your built-in image generation tool to create ONE image, then save it as a PNG file at:\n{out}\n'
           'Do not create, edit or delete any other files. Reply with the saved path.\n\n' + text)
    cmd = [codex, 'exec', '--skip-git-repo-check']
    if job.get('ref'):
        cmd += ['-i', os.path.join(ROOT, job['ref'])]
    cmd.append('-')
    t0 = time.time()
    log = open(os.path.join(GEN, f'_codex_{job["id"]}.log'), 'w', encoding='utf-8')
    subprocess.run(cmd, input=ask, text=True, encoding='utf-8', stdout=log, stderr=subprocess.STDOUT, cwd=GEN)
    log.close()
    if os.path.exists(out) and os.path.getmtime(out) >= t0:
        return True
    # 有時 Codex 只生了圖、沒複製過去:到它的輸出資料夾撿最新那張
    new = [p for p in glob.glob(os.path.join(os.path.expanduser('~'), '.codex', 'generated_images', '*', '*.png'))
           if os.path.getmtime(p) >= t0]
    if new:
        shutil.copy(max(new, key=os.path.getmtime), out)
        return True
    return False


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    only_prompts = '--prompts' in sys.argv
    jobs = json.load(open(os.path.join(ROOT, 'jobs.json'), encoding='utf-8'))['jobs']
    os.makedirs(GEN, exist_ok=True)
    todo = [j for j in jobs if (j['id'] in args if args else not os.path.exists(os.path.join(GEN, j['id'] + '.png')))]
    if not todo:
        print('assets/gen/ 都有了。要重生某張:python tools/gen.py <id>')
        return
    codex = None if only_prompts else find_codex()
    manual = []
    for job in todo:
        text = prompt(job)
        open(os.path.join(GEN, f'_prompt_{job["id"]}.txt'), 'w', encoding='utf-8').write(text + '\n')
        out = os.path.join(GEN, job['id'] + '.png')
        if codex:
            print(f'· {job["id"]}({job.get("zh", job["kind"])}):Codex 生圖中…', flush=True)
            if run_codex(codex, job, text, out):
                print(f'  ✓ {out}')
                continue
            print(f'  ✗ Codex 沒生出來,看 assets/gen/_codex_{job["id"]}.log')
        manual.append(job)
    if manual:
        print('\n這幾張請貼到 ChatGPT(或任何會生圖的 AI)生成,下載後存到指定檔名:')
        for job in manual:
            print(f'  assets/gen/_prompt_{job["id"]}.txt  →  存成 assets/gen/{job["id"]}.png'
                  f'({"直式 1024×1536" if job["kind"] == "scene" else "橫式 1536×1024、洋紅底"})')
        print('貼的時候前面加一句「請用圖片生成畫出下面這張圖:」。存好後跑 python tools/process.py')
    else:
        print('\n全部生好了,接著 python tools/process.py')


if __name__ == '__main__':
    main()

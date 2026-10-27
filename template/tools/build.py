"""排片:narration.txt + storyboard.json(+ voice.json)→ index.html、assets/audio/events.json、assets/audio/sfx.wav。

    python tools/build.py

時間:沒有配音前用 storyboard 的 cps(字/秒)估每句起訖;錄好音(assets/audio/voice.wav)後把每句 [起, 迄] 秒數
寫進 voice.json,重跑就對齊真實配音。畫面上所有動作都錨在「第 N 句開始」,改講稿、換配音都不用手調秒數。
8-bit 音效跟著動作自動登記,build 完順手合成 sfx.wav,不用另外跑。
storyboard.json 的寫法見 ../references/storyboard.md(複製出去的專案裡就是 skill 的 references/)。
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8')
import sfx8bit

CELL = 6
ACCENT = '#FFD166'
GAP, SEG_PAUSE, LEAD = 0.12, 0.35, 0.40


def snap(v, g=CELL):
    return int(round(v / g) * g)


def n_chars(t):
    t = t.replace('*', '')
    return len(re.findall(r'[一-鿿]', t)) + len(re.findall(r'[A-Za-z0-9]+', t))


def timing(lines, cps, seg_starts):
    vp = os.path.join(ROOT, 'voice.json')
    if os.path.exists(vp):
        v = json.load(open(vp, encoding='utf-8'))
        if len(v) != len(lines):
            sys.exit(f'voice.json 有 {len(v)} 句,narration.txt 有 {len(lines)} 句,要一樣多')
        return [tuple(x) for x in v], 'voice.json'
    t, out = LEAD, []
    for i, l in enumerate(lines, 1):
        if i in seg_starts and i > 1:
            t += SEG_PAUSE
        d = max(0.7, n_chars(l) / cps)
        out.append((round(t, 2), round(t + d, 2)))
        t += d + GAP
    return out, f'估算 {cps} 字/秒'


class Board:
    def __init__(self, lines, times, sizes):
        self.lines, self.times, self.sizes = lines, times, sizes
        self.sfx = []

    def at(self, a):
        """錨點:3 = 第 3 句開始;[3, 0.4] = 第 3 句開始後 0.4 秒;{"end": 3} = 第 3 句講完;{"end": 3, "dt": -0.2}。"""
        if isinstance(a, (int, float)):
            return self.times[int(a) - 1][0]
        if isinstance(a, list):
            return self.times[int(a[0]) - 1][0] + float(a[1])
        if isinstance(a, dict) and 'end' in a:
            return self.times[int(a['end']) - 1][1] + float(a.get('dt', 0))
        raise ValueError(f'看不懂的時間 {a!r}')

    def need(self, name):
        if name not in self.sizes:
            sys.exit(f'找不到素材 assets/img/{name}.png(jobs.json 有這個名字嗎?跑過 tools/process.py 了嗎?)')
        return self.sizes[name]

    def snd(self, t, name, opts, default):
        s = opts.get('sound', default)
        if s:
            self.sfx.append([round(t, 3), s])


def expand(board, S, t0, t1):
    """一個場景:素材定義 + 動作 → 給模板的資料(時間、步數、位移都算好)。"""
    things = {}
    for id_, spec in {**S.get('actors', {}), **S.get('props', {})}.items():
        board.need(spec['sprite'])
        things[id_] = {'sprite': spec['sprite'], 'x': spec['x'], 'y': spec['y'], 'k': int(spec.get('k', 1)),
                       'show': spec.get('show', True), 'frames': {spec['sprite']}, 'cx': spec['x']}
    acts = []
    for raw in S.get('do', []):
        at, verb = raw[0], raw[1]
        target = raw[2] if len(raw) > 2 and isinstance(raw[2], str) and raw[2] in things else None
        rest = raw[3:] if target else raw[2:]
        opts = next((r for r in rest if isinstance(r, dict)), {})
        arg = next((r for r in rest if not isinstance(r, dict)), None)
        acts.append((board.at(at), verb, target, arg, opts))
    acts.sort(key=lambda a: a[0])
    out = []
    for t, verb, target, arg, o in acts:
        if not (t0 - 0.3 <= t <= t1 + 0.01):
            print(f'  ! 場景 {S["id"]} 的 {verb} 在 {t:.2f}s,超出場景時間 {t0:.2f}–{t1:.2f}s')
        T = things.get(target)
        a = {'t': round(t, 3), 'verb': verb, 'target': target}
        until = o.get('until')
        a['until'] = round(board.at(until), 3) if until is not None else None
        if verb in ('show', 'hide'):
            pass
        elif verb == 'pose':
            board.need(arg); T['frames'].add(arg); a['sprite'] = arg
        elif verb == 'pop':
            board.snd(t, 'pop', o, 'pop')
        elif verb == 'drop':
            a.update(h=snap(o.get('h', 720)), dur=0.3, n=6); board.snd(t + 0.3, 'thud', o, 'thud')
        elif verb == 'slide':
            a.update(dx=snap(o.get('dx', -1080 if o.get('from', 'left') == 'left' else 1080)), dur=0.3, n=6)
            board.snd(t, 'whoosh', o, 'whoosh')
        elif verb == 'walk':
            to = o['to'] if 'to' in o else arg
            pre = T['sprite'].split('_')[0]
            frames = o.get('frames') or [f for f in (pre + '_side_a', pre + '_side_b') if f in board.sizes] or [T['sprite']]
            end = o.get('end', T['sprite'])
            for f in frames + [end]:
                board.need(f); T['frames'].add(f)
            dist = abs(to - T['cx'])
            step = float(o.get('step', 0.15))
            n = max(2, round(dist / float(o.get('speed', 360)) / step))
            px = max(CELL, snap(dist / n))
            d = 1 if to >= T['cx'] else -1
            x0 = T['cx'] - T['x']
            T['cx'] += d * px * n
            a.update(x0=x0, x1=T['cx'] - T['x'], dir=d, n=n, step=step, dur=round(n * step, 3), frames=frames, end=end)
            for i in range(n):
                board.snd(t + i * step, 'step', o, 'step')
        elif verb == 'hop':
            a['h'] = snap(o.get('h', 36)); board.snd(t, 'jump', o, 'jump')
        elif verb == 'bob':
            step = float(o.get('step', 0.12)); end = a['until'] if a['until'] is not None else t1
            a.update(h=snap(o.get('h', 12)), step=step, n=max(1, int((end - t) / step)))
        elif verb == 'loop':
            step = float(o.get('step', 0.12)); end = a['until'] if a['until'] is not None else t1
            frames = o['frames']
            for f in frames:
                board.need(f); T['frames'].add(f)
            a.update(frames=frames, step=step, n=max(1, int((end - t) / step)), end=o.get('end', T['sprite']))
            T['frames'].add(a['end'])
            for i in range(a['n'] if o.get('sound') else 0):
                board.sfx.append([round(t + i * step, 3), o['sound']])
        elif verb == 'shake':
            board.snd(t, 'hit', o, 'hit')
        elif verb == 'flash':
            board.snd(t, 'sparkle', o, 'sparkle')
        elif verb in ('big', 'clear'):
            text = 'CLEAR!' if verb == 'clear' else arg
            a.update(verb='big', text=text, y=o.get('y', 420 if verb == 'clear' else 600), size=o.get('size', 72 if verb == 'clear' else 64),
                     color=o.get('color', ACCENT))
            if a['until'] is None:
                a['until'] = round(t1, 3)
            board.snd(t, 'clear' if verb == 'clear' else 'pop', o, 'clear' if verb == 'clear' else 'pop')
            if verb == 'clear':
                out.append({'t': round(t + 0.05, 3), 'verb': 'sparkle', 'target': None, 'until': None,
                            'pts': [[160, 300], [860, 280], [780, 520], [120, 540]]})
        elif verb == 'say':
            dt = float(o.get('dt', 0.04))
            a.update(text=arg, x=o.get('x', 84), y=o.get('y', 420), w=o.get('w', 912), size=o.get('size', 44),
                     color=o.get('color', ACCENT), dt=dt)
            for i, ch in enumerate(arg):
                if ch.strip() and i % 2 == 0:
                    board.snd(t + 0.05 + i * dt, 'blip', o, 'blip')
        elif verb == 'type':
            dt = float(o.get('dt', 0.09))
            a.update(text=arg, y=o.get('y', 300), dt=dt)
            for i, ch in enumerate(arg):
                if ch.strip():
                    board.snd(t + 0.1 + i * dt, 'type', o, 'type')
        elif verb == 'count':
            n = int(o.get('steps', 8)); step = float(o.get('step', 0.08))
            lo, hi = o.get('from', 0), o.get('to', arg)
            vals = [round(lo + (hi - lo) * i / (n - 1)) for i in range(n)]
            fmt = o.get('format', '{:,}')
            a.update(values=[fmt.format(v) for v in vals], step=step, label=o.get('label', ''), y=o.get('y', 600),
                     size=o.get('size', 64), color=o.get('color', ACCENT))
            for i in range(n - 1):
                board.snd(t + i * step, 'tick', o, 'tick')
            board.snd(t + (n - 1) * step, 'coin', o, 'coin')
        elif verb == 'stamp':
            a.update(text=arg, x=o.get('x', 600), y=o.get('y', 700), color=o.get('color', '#FF5A8A'))
            board.snd(t, 'stamp', o, 'stamp')
        elif verb == 'sparkle':
            if T:
                w, h = board.sizes[T['sprite']]; w *= T['k']; h *= T['k']
                cx, by = T['cx'], T['y']
                pts = [[cx - w / 2 - 30, by - h], [cx + w / 2, by - h - 20], [cx + w / 2 + 10, by - h / 2], [cx - w / 2 - 40, by - h / 2]]
            else:
                pts = o.get('pts', [[300, 600], [740, 560], [680, 860], [360, 900]])
            a.update(pts=pts, target=None)
            board.snd(t, 'sparkle', o, 'sparkle')
        elif verb == 'sfx':
            board.snd(t, arg, {}, arg)
        else:
            sys.exit(f'看不懂的動作 {verb}(可用的見 references/storyboard.md)')
        out.append(a)
    for T in things.values():
        T['frames'] = sorted(T['frames'])
        del T['cx']
    return things, out


def main():
    lines = [l.strip() for l in open(os.path.join(ROOT, 'narration.txt'), encoding='utf-8') if l.strip()]
    sb = json.load(open(os.path.join(ROOT, 'storyboard.json'), encoding='utf-8'))
    scenes = sb['scenes']
    times, src = timing(lines, sb.get('cps', 5.4), {s['from'] for s in scenes})
    total = round(times[-1][1] + sb.get('tail', 1.5), 2)
    from PIL import Image
    img = os.path.join(ROOT, 'assets', 'img')
    sizes = {f[:-4]: list(Image.open(os.path.join(img, f)).size) for f in os.listdir(img)
             if f.endswith('.png') and not f.startswith('_')} if os.path.isdir(img) else {}
    board = Board(lines, times, sizes)
    data_scenes = []
    for i, S in enumerate(scenes):
        t0 = 0.0 if i == 0 else round(board.at(S['from']) - 0.25, 3)
        t1 = total if i + 1 == len(scenes) else round(board.at(scenes[i + 1]['from']) - 0.25, 3)
        if S.get('bg'):
            board.need('bg_' + S['bg'])
        mosaic = bool(S.get('bg')) and all(f'bg_{S["bg"]}_m{k}' in sizes for k in (1, 2, 3))
        enter = S.get('enter', 'wipe' if i else 'mosaic')
        if enter == 'wipe' and i:
            board.sfx.append([round(t0 - 0.2, 3), 'whoosh'])
        if enter == 'mosaic' and mosaic:
            for k in range(3):
                board.sfx.append([round(t0 + k * 0.09, 3), 'blip'])
        if S.get('header'):
            board.sfx.append([round(t0 + 0.1, 3), 'pop'])
        things, acts = expand(board, S, t0, t1)
        data_scenes.append({'id': S['id'], 't0': t0, 't1': t1, 'bg': S.get('bg'), 'color': S.get('color'),
                            'stars': S.get('stars', False), 'enter': enter, 'mosaic': mosaic,
                            'header': S.get('header'), 'things': things, 'do': acts})
    cap_end = [round(min(times[i + 1][0] if i + 1 < len(times) else total, times[i][0] + 4), 3) for i in range(len(times))]
    data = {'lines': lines, 'times': times, 'total': total, 'sizes': sizes, 'scenes': data_scenes, 'capEnd': cap_end,
            'noCaption': sb.get('noCaption', []), 'watermark': sb.get('watermark', '')}

    audio = []
    if os.path.exists(os.path.join(ROOT, 'assets', 'audio', 'voice.wav')):
        audio.append('<audio id="vo" src="assets/audio/voice.wav" data-start="0"></audio>')
    board.sfx.sort()
    os.makedirs(os.path.join(ROOT, 'assets', 'audio'), exist_ok=True)
    json.dump({'total': total, 'events': board.sfx}, open(os.path.join(ROOT, 'assets', 'audio', 'events.json'), 'w', encoding='utf-8'))
    if sb.get('sfx', True):
        sfx8bit.synth(board.sfx, total, os.path.join(ROOT, 'assets', 'audio', 'sfx.wav'))
        audio.append('<audio id="sfx" src="assets/audio/sfx.wav" data-start="0"></audio>')

    tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
    html = (tpl.replace('__DATA__', json.dumps(data, ensure_ascii=False)).replace('__TOTAL__', str(total))
               .replace('__TITLE__', sb.get('title', 'pixel video')).replace('__AUDIO__', '\n      '.join(audio)))
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(html)
    print(f'index.html ok · {len(lines)} 句 · {len(scenes)} 個場景 · {len(board.sfx)} 個音效 · 時間來源 {src} · 全長 {total}s')
    starts = {round(board.at(s['from']), 2): s['id'] for s in scenes}
    for i, (l, (a, b)) in enumerate(zip(lines, times), 1):
        mark = f'  ← {starts[round(a, 2)]}' if round(a, 2) in starts else ''
        print(f'{i:2d} {a:6.2f}–{b:6.2f}  {l}{mark}')


if __name__ == '__main__':
    main()

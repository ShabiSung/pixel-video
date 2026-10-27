"""8-bit 音效:用方波和雜訊直接合成,不下載任何音檔 → assets/audio/sfx.wav(44.1kHz mono)。

build.py 會自動呼叫 synth();時間點來自 storyboard 的動作(每個動作有預設音效,可用 "sound" 換或設 null 關掉)。
單獨重跑:python tools/sfx8bit.py(讀 assets/audio/events.json)
要新的聲音:在 SFX 加一行,名字就能在 storyboard 用 ["sfx", "名字"] 或 {"sound": "名字"}。
"""
import json, os, random, struct, sys, wave

SR = 44100


def synth(events, total, out, outro=True):
    buf = [0.0] * int(SR * (total + 0.5))

    def tone(t0, dur, f0, f1=None, vol=0.18, duty=0.5):
        f1 = f1 or f0
        n = int(dur * SR); s0 = int(t0 * SR); ph = 0.0
        for i in range(n):
            x = i / n
            ph += (f0 + (f1 - f0) * x) / SR
            if 0 <= s0 + i < len(buf):
                buf[s0 + i] += (1.0 if (ph % 1.0) < duty else -1.0) * vol * (1 - x) ** 1.5

    def noise(t0, dur, vol=0.12, seed=1, hold_n=6):
        rnd = random.Random(seed)
        n = int(dur * SR); s0 = int(t0 * SR); hold = 0.0
        for i in range(n):
            if i % hold_n == 0:
                hold = rnd.uniform(-1, 1)
            if 0 <= s0 + i < len(buf):
                buf[s0 + i] += hold * vol * (1 - i / n) ** 2

    def arp(t, notes, step=0.07, dur=0.08, vol=0.09):
        for i, f in enumerate(notes):
            tone(t + i * step, dur, f, f, vol)

    SFX = {
        'blip':    lambda t, k: tone(t, 0.035, 1180 + (k % 3) * 120, None, 0.06),
        'tick':    lambda t, k: tone(t, 0.025, 1800, None, 0.05),
        'type':    lambda t, k: (noise(t, 0.02, 0.06, seed=k, hold_n=3), tone(t, 0.02, 2200, None, 0.03)),
        'step':    lambda t, k: noise(t, 0.03, 0.05, seed=k),
        'pop':     lambda t, k: tone(t, 0.06, 520, 1040, 0.09),
        'jump':    lambda t, k: tone(t, 0.16, 300, 900, 0.14),
        'thud':    lambda t, k: (noise(t, 0.10, 0.18, seed=k, hold_n=12), tone(t, 0.12, 140, 70, 0.16)),
        'whoosh':  lambda t, k: (noise(t, 0.18, 0.07, seed=k, hold_n=3), tone(t, 0.18, 300, 900, 0.04)),
        'hit':     lambda t, k: (noise(t, 0.14, 0.22, seed=k, hold_n=12), tone(t, 0.14, 220, 90, 0.16)),
        'slam':    lambda t, k: (noise(t, 0.22, 0.30, seed=k, hold_n=14), tone(t, 0.25, 160, 50, 0.22)),
        'stamp':   lambda t, k: (noise(t, 0.08, 0.16, seed=k, hold_n=10), tone(t, 0.09, 260, 120, 0.12)),
        'coin':    lambda t, k: (tone(t, 0.07, 988, None, 0.13), tone(t + 0.07, 0.30, 1319, None, 0.13)),
        'sparkle': lambda t, k: arp(t, (1568, 1976, 2349, 3136), 0.05, 0.07, 0.06),
        'check':   lambda t, k: (tone(t, 0.06, 880, None, 0.10), tone(t + 0.06, 0.12, 1320, None, 0.10)),
        'alert':   lambda t, k: (tone(t, 0.08, 988, None, 0.09, 0.25), tone(t + 0.09, 0.10, 740, None, 0.09, 0.25)),
        'power':   lambda t, k: (tone(t, 0.25, 200, 1200, 0.08, 0.25), tone(t + 0.25, 0.10, 1568, None, 0.07)),
        'levelup': lambda t, k: arp(t, (659, 784, 988, 1319), 0.06, 0.09, 0.09),
        'clear':   lambda t, k: arp(t, (784, 784, 988, 1175, 1568), 0.09, 0.10, 0.10),
        'fanfare': lambda t, k: arp(t, (523, 659, 784, 1047, 784, 1047), 0.08, 0.12, 0.10),
        'gameover': lambda t, k: arp(t, (523, 494, 440, 392, 349, 262), 0.13, 0.16, 0.10),
        'boot':    lambda t, k: arp(t, (262, 330, 392, 523, 659, 784), 0.05, 0.07, 0.08),
        'coinin':  lambda t, k: (tone(t, 0.05, 1976, None, 0.10), noise(t + 0.06, 0.08, 0.10, seed=k, hold_n=10), tone(t + 0.12, 0.25, 1319, 1568, 0.08)),
        'static':  lambda t, k: noise(t, 0.30, 0.10, seed=k, hold_n=2),
        'heal':    lambda t, k: arp(t, (784, 988, 1175, 1568, 1976), 0.05, 0.08, 0.07),
        'boss':    lambda t, k: (tone(t, 0.55, 110, 70, 0.16, 0.25), arp(t + 0.05, (196, 185, 175, 147), 0.12, 0.13, 0.09)),
        'score':   lambda t, k: arp(t, (523, 659, 784, 1047, 1319, 1568, 2093), 0.06, 0.09, 0.09),
    }
    for k, (t, typ) in enumerate(events):
        if typ not in SFX:
            sys.exit(f'沒有叫 {typ} 的音效,可用:' + '、'.join(SFX))
        SFX[typ](t, k)
    if outro:
        arp(total - 1.2, (523, 659, 784, 1047), 0.08, 0.14, 0.08)   # 片尾小琶音
    peak = max(1e-6, max(abs(x) for x in buf))
    g = 0.85 / peak if peak > 0.85 else 1.0
    with wave.open(out, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b''.join(struct.pack('<h', int(max(-1, min(1, x * g)) * 32767)) for x in buf))
    return len(events)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ev = json.load(open(os.path.join(root, 'assets', 'audio', 'events.json'), encoding='utf-8'))
    n = synth(ev['events'], ev['total'], os.path.join(root, 'assets', 'audio', 'sfx.wav'))
    print('ok assets/audio/sfx.wav', n, '個音效')

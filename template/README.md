# 像素片專案模板

把這個資料夾整個複製成新專案,照順序跑:

```bash
python tools/setup.py          # 下載 GSAP(1 個檔,約 70 KB),建資料夾
python tools/gen.py            # 照 jobs.json 生圖(有 Codex 自動生;沒有就印出提示詞)
python tools/process.py        # AI 原圖 → 6px 像素素材,打開 assets/img/_*_preview.png 檢查
python tools/build.py          # narration.txt + storyboard.json → index.html + 8-bit 音效
npx --yes hyperframes@0.8.31 check
npx --yes hyperframes@0.8.31 render -q high -o renders/my-video-v1.mp4
```

| 檔案 | 換題材時要改 |
|---|---|
| `jobs.json` | 要生的場景、角色動作、道具 |
| `narration.txt` | 旁白(一行一句,`*星號*` = 上強調色) |
| `storyboard.json` | 每個場景的背景、角色、道具與動作 |
| `voice.json` | 錄好配音後每句的 [起, 迄] 秒數(沒有就用估算) |
| `tools/template.html` | 強調色 `--accent`、字幕樣式;要新動作才改 |
| `tools/sfx8bit.py` | 要新的音效才改 |
| `tools/pxlib.py`、`gen.py`、`process.py`、`build.py` | 通常不用改 |

範例片:14 秒、三個場景(街機廳 → 星空 → 街機廳)、一個主角 12 個動作、12 個道具。

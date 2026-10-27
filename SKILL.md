---
name: pixel-video
description: 用 Claude Code 做一支直式 9:16 的像素遊戲風短片(Reels / 抖音 / Shorts):AI 生場景後減到 96 色、對齊 6px 格子;一張素材表生出一整排角色動作,自動切開去背;角色一步走一格;8-bit 音效用程式直接合成、自動對上每個動作;HyperFrames 渲染 60fps 成片。不會畫畫也行。只要使用者說「做像素風影片」「像素遊戲風」「8-bit 風格短片」「復古遊戲畫面」「pixel art 影片」「把這段講稿做成像素動畫」,或想把任何題目(理財觀念、工具教學、故事)做成遊戲畫面風的短片,都要用這個 skill,即使沒有說出「像素」兩個字。Use for vertical pixel-art / retro-game style explainer videos with AI-generated scenes and sprites, chiptune SFX and HyperFrames.
---

# pixel-video:像素遊戲風短片

一支像素片就是三個關卡:**畫場景 → 角色動起來 → 配 8-bit 音效**。
場景和角色交給 AI 生圖,程式把它們修成真正的像素(96 色、對齊格子、一步一格);
畫面寫成一份 `storyboard.json`,每個動作錨在「第幾句旁白」;音效跟著動作自動合成。

`template/` 是可以直接渲染的範例專案(14 秒、三個場景、一個角色、12 個道具),做新的一支就是複製它、換掉裡面的內容。

## 需要的環境

- Claude Code、Node.js 18 以上(用 `npx` 跑 HyperFrames 0.8.31)
- Python 3.9 以上 + `pip install pillow numpy`;ffmpeg 在 PATH 上(檢查成片用)
- 生圖二選一:**Codex CLI**(有就全自動),或使用者自己貼提示詞到 **ChatGPT**(任何會生圖的 AI 都行)

開工前用 `node -v`、`python -c "import PIL, numpy"`、`ffmpeg -version` 確認一次,缺什麼先跟使用者說怎麼裝。

## 六關流程

第 1、2 關停下來給使用者確認;第 3 關生完圖給使用者看過再往下;之後自己做到成片再交。

### 第 1 關 簡報

用 AskUserQuestion 一次問完(每題給建議選項,第一個標 Recommended):

| 問什麼 | 預設 |
|---|---|
| 題材、要講的內容(有講稿就直接用) | — |
| 長度 | 40–60 秒(一句旁白 8–12 字,約 5.4 字/秒) |
| 主角 | 一個 Q 版角色(使用者有自己的吉祥物就附參考圖) |
| 世界觀 | 從題材想一個遊戲世界:街機廳、RPG 小鎮、地城、太空站…(見 `references/scene-prompts.md`) |
| 配音 | 使用者自己錄;先用估算時間做無配音預覽 |
| 生圖 | 有 Codex CLI 就自動生;沒有就給提示詞讓使用者貼到 ChatGPT |

答案寫進專案的 `SPEC.md`(之後每一關的決定都往下記)。

### 第 2 關 講稿與分鏡

1. 旁白一行一句寫進 `narration.txt`,要上強調色的詞用 `*星號*` 包起來。
2. 分鏡:**一段一個地點**,60 秒大約 6 個地點;地點裡多放會動的小東西(閃爍、上下飄、跳號),不要一直換場景。
3. 現實的東西都翻成遊戲語言:失敗 = GAME OVER、進度 = 經驗條、拿到成果 = 開寶箱 / CLEAR!、比較 = 一來一回的 Boss 戰。完整對照在 `references/storyboard.md`。
4. 給使用者看「段落 | 旁白 | 畫面(地點、角色動作、道具)」三欄表,確認了才生圖。

### 第 3 關 生素材(STAGE 1 畫場景、STAGE 2 角色)

讀 `references/generating.md`。

1. 把 `template/` 整個複製到新的專案資料夾(不要直接改 skill 裡的 template),跑 `python tools/setup.py`(會從 jsdelivr 下載 GSAP 一個檔,約 70 KB,先跟使用者說一聲)。
2. 改 `jobs.json`:每個地點一個 `scene`;角色和道具各一張 `sheet`(洋紅底素材表,3×4 最穩)。
3. `python tools/gen.py`:有 Codex 就自動生到 `assets/gen/`;沒有就把提示詞存成 `assets/gen/_prompt_<id>.txt`,請使用者貼到 ChatGPT、下載後存成 `assets/gen/<id>.png`。
4. `python tools/process.py`:場景 → 180×320 格、96 色(加三張馬賽克版給進場用);素材表 → 自動切塊、去背、補外框。
5. **打開 `assets/img/_<id>_preview.png` 逐張看**:少一塊、黏在一起、動作不對就改 jobs.json 重生那一張。給使用者看過角色長相再往下。

### 第 4 關 排畫面

讀 `references/storyboard.md`,寫 `storyboard.json`:每個場景寫背景、標題、角色和道具站哪裡、哪一句做什麼動作(走、跳、換動作、掉下來、打字、跳號、蓋章、CLEAR!)。

`python tools/build.py` → `npx --yes hyperframes@0.8.31 check`(要全部 0 errors)→ `npx --yes hyperframes@0.8.31 snapshot --at <幾個關鍵秒數> --no-end --describe false` 看定格。
build.py 會印出每句的起訖秒數,動作寫在場景時間外面時會警告。

### 第 5 關 聲音(STAGE 3 配音效)

- 每個動作都有預設的 8-bit 音效(走路腳步、落地、打字、跳號、蓋章、過關),build.py 順手合成 `assets/audio/sfx.wav`,不用下載任何音檔。要換或關掉看 `references/sound.md`。
- 配音:使用者錄好存成 `assets/audio/voice.wav`,把每句 `[起, 迄]` 秒數寫進 `voice.json`(做法見 `references/sound.md`),重跑 build.py,畫面、字幕、音效全部自動對齊。

### 第 6 關 渲染與自檢

1. `npx --yes hyperframes@0.8.31 render -q high -o renders/<名字>-v1.mp4`
2. 拼一張縮圖表逐格看:`ffmpeg -i renders/x.mp4 -vf "fps=1/0.7,scale=270:480,tile=7x4" -frames:v 1 renders/sheet.jpg`
3. 照 `references/pixel-rules.md` 最後的檢查表過一次(半格、糊掉、字被擋、場景穿幫、音效對不上),修完重渲才交。

使用者看完提意見,改 storyboard → build → render → 再看縮圖表。每一版的改動記進 SPEC.md。

## 規則

- **不能有半格**:背景一格 6px,所有位置、位移、放大倍數都是 6 的倍數 / 整數倍;動畫一律 `steps(n)`,不用平滑緩動。細節在 `references/pixel-rules.md`。
- **生圖不准有字**:AI 生的字一定是亂碼,字全部用字型疊上去。
- **不要畫真人、別人的角色和商標**:生圖提示詞不要指名現有的遊戲角色或真實人物;官方 logo 要用時去官網找原圖,縮成整數格再放大。
- **下載前先問**:GSAP、任何素材或音檔,下載前列出檔名、來源、大小。
- **不刪使用者的檔案**;要清理先問。

## 最常踩的坑

| 症狀 | 原因 | 怎麼擋 |
|---|---|---|
| 場景的霓虹粉紅、藍色被吃掉,畫面灰灰的 | 色數壓太少 | 場景用 96 色(`process.py` 預設),不要用 48 |
| 素材表切出來塊數不對 | 角色靠太近黏成一塊,或洋紅背景有漸層、地板陰影 | jobs.json 那張加 `"grid": true`;提示詞強調 flat pure magenta、wide gaps |
| 同一個角色不同動作大小不一 | 每格各自縮放 | 同角色的 item 給同一個 `group` |
| 角色走路滑過去、不像走 | 位移用平滑緩動、或只有一張腳步圖 | `walk` 用兩張側面圖交替,`steps(n)` 一步一格(build.py 已處理) |
| 角色換動作時跳一下位置 | 各動作格寬度不同 | 模板把每格貼底置中在同一個框裡,不要自己改成左上對齊 |
| 前一個場景的東西穿到下一個場景 | 用 `visibility` 藏容器,子元素被設成 visible 時擋不住 | 場景和道具容器一律用 `opacity` 藏(模板已處理) |
| 文字邊緣糊糊的 | 用了模糊陰影 | 外框用 8 個方向的實色 text-shadow(`.o6`、`.o4`) |
| Codex 說生好了但檔案不在 | 它只存在自己的資料夾 | `gen.py` 會去 `~/.codex/generated_images/` 撿最新那張 |

## 檔案地圖

```
template/                  複製這整個資料夾開新專案
  jobs.json                要生的場景與素材表(範例:街機廳、主角 12 個動作、道具 12 個)
  narration.txt            旁白,一行一句,*星號* = 上強調色
  storyboard.json          畫面:場景、角色、道具、每句的動作
  tools/setup.py           下載 GSAP(先問)、建資料夾
  tools/gen.py             產提示詞;有 Codex 就自動生圖
  tools/process.py         AI 原圖 → 6px 像素格 PNG(場景、切素材表)
  tools/pxlib.py           像素格共用函式(對齊、減色、洋紅去背、切塊、補外框)
  tools/build.py           排片 → index.html + 8-bit 音效
  tools/sfx8bit.py         方波 / 雜訊合成音效
  tools/template.html      版型與動作引擎(通常不用改)
  assets/fonts/            俐方體 11 號、Press Start 2P(OFL,附授權)
  assets/gen/              範例原圖(AI 生成)
references/
  pixel-rules.md           像素格、字、版面、檢查表
  generating.md            jobs.json 寫法、生圖提示詞、切圖疑難
  storyboard.md            storyboard.json 全部動作與參數、遊戲化對照表
  sound.md                 音效清單、換音效、配音對齊
  scene-prompts.md         加碼:做過的像素場景提示詞
```

## 出處

渲染用 [HyperFrames](https://github.com/heygen-com/hyperframes)(HeyGen);動畫用 [GSAP](https://gsap.com);
字型 [俐方體 11 號 Cubic 11](https://github.com/ACh-K/Cubic-11)、[Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P)(SIL OFL 1.1)。詳見 `NOTICE`。

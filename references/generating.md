# 生素材:jobs.json、提示詞、切圖

## 兩種圖

| kind | 尺寸 | 用途 | 處理後 |
|---|---|---|---|
| `scene` | 直式 1024×1536 | 一個地點的背景 | `assets/img/bg_<id>.png`(180×320 格、96 色、每格 6px)+ `_m1/_m2/_m3` 三張馬賽克版 |
| `sheet` | 橫式 1536×1024、洋紅底 | 角色的一整排動作、或一組道具 | 每個 item 一張透明 PNG,補一圈深色外框 |

## jobs.json

```json
{"jobs": [
  {"id": "town", "kind": "scene", "zh": "夜晚小鎮", "key": true,
   "prompt": "Side view of a small medieval town street at night ... The lower part ... must be a plain, mostly empty floor ..."},
  {"id": "hero", "kind": "sheet", "rows": 3, "cols": 4, "grid": true,
   "note": "Every sprite is the same chibi ... (長相寫死:帽子、髮色、衣服、鞋子的顏色)",
   "ref": "assets/ref/mascot.png",
   "items": [
     {"name": "hero_idle", "h": 58, "group": "hero", "zh": "站", "d": "front view, standing relaxed"},
     {"name": "hero_side_a", "h": 58, "group": "hero", "zh": "側面走 a", "d": "side view facing right, walking, left leg forward"}
   ]}
]}
```

- `prompt`(scene)只寫畫面內容;共用的風格句(16-bit SNES、硬邊、不准有字和人)`gen.py` 會自動加。
- 場景一定要寫「下方 60% 以下是空地板,讓角色站」,不然角色會踩在家具上。
- `key: true`:天空畫成純洋紅,處理時變透明 → 後面可以墊星空、會動的雲、K 線。
- `items` 由左上起逐列排;`h` = 處理後的高度(格)。主角約 58 格高(348px),道具 18–24 格,小東西 8–12 格。
- `group`:同一個角色的所有動作給同一個 group,處理時以最高的那張為準等比縮放,換動作才不會忽大忽小。
- `grid: true`:照格子切(角色舉手、跨步時會靠太近,連通區塊會黏在一起)。道具通常不用。
- `ref`:使用者有自己的角色時放參考圖,Codex 會用 `-i` 附上;用 ChatGPT 就請使用者把參考圖一起貼上。
- 角色**一定要有** `<名字>_side_a`、`<名字>_side_b` 兩張側面走路(左右腳相反),storyboard 的 `walk` 會自動用。

## 生圖

```bash
python tools/gen.py              # 生還沒有的
python tools/gen.py hero         # 重生指定的(會蓋掉)
python tools/gen.py --prompts    # 只寫提示詞
```

- **有 Codex CLI**:自動 `codex exec` 生圖並存到 `assets/gen/<id>.png`,紀錄在 `_codex_<id>.log`。Windows 會先找 Codex App 內建的新版(`%LOCALAPPDATA%\OpenAI\Codex\bin\*\codex.exe`),也可以用環境變數 `CODEX_BIN` 指定。
- **沒有 Codex**:提示詞存在 `assets/gen/_prompt_<id>.txt`。請使用者貼到 ChatGPT(前面加一句「請用圖片生成畫出下面這張圖:」),下載後存成 `assets/gen/<id>.png`。
- 生出來的圖先給使用者看,再往下做。

## 處理

```bash
python tools/process.py          # 全部
python tools/process.py hero     # 只處理 hero
```

處理完一定打開 `assets/img/_<id>_preview.png` 看一眼。

## 疑難

| 症狀 | 怎麼辦 |
|---|---|
| `切出 11 塊,jobs.json 寫了 12 個名字` | 兩個黏在一起 → 加 `"grid": true`;或 AI 少畫一個 → 重生 |
| 切出的塊數對,但順序亂掉 | 素材沒排成整齊的列 → 加 `"grid": true`,或在提示詞強調 evenly spaced grid |
| 切出來帶一圈粉紅邊 | 洋紅背景有漸層 / 陰影 → 提示詞強調 perfectly flat pure magenta, no shadows,重生 |
| 道具被切成兩塊(放大鏡的鏡片和握把) | `components()` 已經會先膨脹再分塊;還是分開就改用 `grid` |
| 場景主體太偏、被裁掉 | 場景會照高度縮放、裁掉左右兩側;重要的東西請 AI 畫在中間 70% 寬度裡 |
| 角色長得每格不一樣 | `note` 把長相寫得更死(每樣東西的顏色),或附 `ref` 參考圖 |
| 生出來有字 | 重生,提示詞已經寫 NO text;字一律之後用字型疊 |
| 想要已經存在的官方 logo 進像素畫面 | 不要叫 AI 畫;去官網拿原圖,縮成整數格(例如 22×22)再 ×6 放大 |

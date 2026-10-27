# storyboard.json:畫面怎麼寫

整支片的畫面就是一份 JSON。`tools/build.py` 把它跟 `narration.txt` 的時間合起來,算好每個動作的秒數、步數、位移和音效,塞進 `tools/template.html`。

## 最外層

```json
{
  "title": "片名(只用在 HTML 標題)",
  "watermark": "右上角小字,不要就給空字串",
  "cps": 5.4,            // 沒配音時估時間:每秒幾個字
  "tail": 1.6,           // 最後一句講完後再留幾秒
  "noCaption": [12, 13], // 這幾句不出字幕(例如畫面上已經有大字)
  "sfx": true,           // false = 不合成音效
  "scenes": [ ... ]
}
```

## 場景

```json
{
  "id": "town",
  "from": 3,                       // 從第 3 句開始(提早 0.25 秒換場);第一個場景從 0 秒開始
  "bg": "town",                    // assets/img/bg_town.png(jobs.json 的 scene id);不要背景就省略
  "color": "#0B0D1F",              // 背景色(沒有 bg、或 bg 天空透明時墊在後面)
  "stars": true,                   // 加一層會閃的星星(天空透明的場景很好用)
  "enter": "wipe",                 // 進場:wipe 方塊轉場(預設)/ mosaic 從馬賽克變清楚(第一個場景預設)/ cut 直接切
  "header": ["STAGE 1", "畫場景"], // 頂部標題:英文點陣字 + 中文;不要就省略
  "actors": { "hero": {"sprite": "hero_idle", "x": 540, "y": 1440} },
  "props":  { "chest": {"sprite": "chest", "x": 780, "y": 1440, "k": 2, "show": false} },
  "do": [ ... ]
}
```

- 場景結束 = 下一個場景開始;最後一個場景演到片尾。
- `actors` 和 `props` 寫法一樣(分開只是好讀):`sprite` 一開始顯示哪一格、`x` 腳底中心、`y` 腳底高度、`k` 放大倍數(整數)、`show: false` 先藏起來(等 pop / drop / show)。
- 版面(1080×1920):標題在 y 210 附近、主體放在 y 400–1440、字幕在 y 1500,角色腳底 1260–1440 最好看。
- 同一個 id 可以在不同場景重複用(各場景各自一份)。

## 時間錨點

每個動作的第一格是時間:

| 寫法 | 意思 |
|---|---|
| `3` | 第 3 句開始 |
| `[3, 0.4]` | 第 3 句開始後 0.4 秒(可以是負的) |
| `{"end": 3}` | 第 3 句講完 |
| `{"end": 3, "dt": -0.2}` | 第 3 句講完前 0.2 秒 |

錨在句子上,改講稿、錄好配音後重跑 build.py,全部自動對齊,不用手調秒數。

## 動作

一個動作 = `[時間, 動作, 對象?, 參數?, {選項}?]`。對象是這個場景的 actor / prop id;文字類動作沒有對象。
每個動作都可以加 `{"sound": "名字"}` 換音效、`{"sound": null}` 不要音效、`{"until": 錨點}` 指定什麼時候消失。

| 動作 | 寫法 | 做什麼 | 預設音效 |
|---|---|---|---|
| show / hide | `[2, "show", "chest"]` | 直接出現 / 消失 | — |
| pose | `[2, "pose", "hero", "hero_wave"]` | 換動作格(眨眼、揮手、驚訝…) | — |
| walk | `[2, "walk", "hero", {"to": 780}]` | 走到 x=780:自動用 `<角色>_side_a/b` 兩張交替、一步一格,往左走自動翻面,走完回到原本那格。選項 `frames`、`end`(走完換哪格)、`speed`(px/秒,預設 360)、`step`(每步秒數,預設 0.15) | step(每一步) |
| hop | `[3, "hop", "hero", {"h": 36}]` | 原地跳一下 | jump |
| pop | `[3, "pop", "chest"]` | 從小彈出來 | pop |
| drop | `[3, "drop", "chest", {"h": 720}]` | 從上面掉下來(6 格一步) | thud(落地) |
| slide | `[3, "slide", "chest", {"from": "right"}]` | 從左 / 右滑進來 | whoosh |
| bob | `[3, "bob", "coin", {"h": 12, "until": 5}]` | 上下飄(沒寫 until 就飄到場景結束) | — |
| loop | `[3, "loop", "hero", {"frames": ["hero_type_a", "hero_type_b"], "until": 5, "sound": "type", "end": "hero_idle"}]` | 幾張動作格輪播(打字、揮手、敲打) | 自己指定 |
| shake | `[4, "shake"]` / `[4, "shake", "chest"]` | 整個場景 / 一個東西抖一下 | hit |
| flash | `[4, "flash"]` | 全畫面白閃一下 | sparkle |
| sparkle | `[4, "sparkle", "chest"]` 或 `{"pts": [[x, y], …]}` | 東西四周冒十字閃光 | sparkle |
| big | `[4, "big", "LEVEL UP!", {"y": 600, "size": 64, "color": "#FFD166"}]` | 點陣大字彈出(英文數字用;中文用 say) | pop |
| clear | `[5, "clear"]` | 「CLEAR!」+ 閃光 + 過關音樂 | clear |
| say | `[2, "say", "九成的財富", {"x": 84, "y": 420, "w": 912, "size": 44}]` | 像素對話框,中文逐字打出來 | blip |
| type | `[2, "type", "畫一間街機廳", {"y": 300}]` | 指令輸入框,逐字打字 | type(每個字) |
| count | `[4, "count", {"from": 0, "to": 99999, "label": "SCORE", "format": "{:06d}"}]` | 跳號 | tick … coin |
| stamp | `[5, "stamp", "DONE", {"x": 660, "y": 760, "color": "#FF5A8A"}]` | 斜蓋一個章 | stamp |
| sfx | `[5, "sfx", "levelup"]` | 只放音效 | — |

需要模板沒有的動作:在 `tools/template.html` 的 `DO` 加一個函式,在 `tools/build.py` 的 `expand()` 加對應的時間計算與音效。動作的時間、步數一律在 build.py 算好,模板只照著播。

## 節奏

- 新畫面「進來就在動」:場景一出來,角色就在走、東西就在飄、星星在閃。
- 每 1.3–1.5 秒一個事件(換動作、掉東西、跳號、閃光),但重點畫面停 1.5–2 秒讓人看清楚。
- 一段最多兩個鏡位;段落之間留一點停頓。
- 東西要變大就連續長大(一格一格換更大的那張),不要動完突然放大。

## 現實的東西翻成遊戲語言

| 現實 | 遊戲畫面 |
|---|---|
| 失敗、被裁員、虧損 | GAME OVER + CONTINUE? |
| 進度、熟練度、適合度 | 經驗條 / 血條 |
| 拿到成果、做完 | 開寶箱、CLEAR!、CLASS CHANGE、獎盃 |
| 收集、清單 | 背包格子、圖鑑 |
| 審核、被退件 | 「!」+ REVISE 章 |
| 面試、談判、跟對手比 | 一來一回的 Boss 戰(血條、攻擊、GUARD、反擊、COMBO) |
| 選擇、步驟 | 關卡地圖、STAGE 1/2/3 |
| 錢變多 | 金幣掉下來、SCORE 跳號 |
| 時間很長 | 日夜交替(同一個場景天色變暗、燈亮起來) |

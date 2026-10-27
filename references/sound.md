# 聲音

## 8-bit 音效

`tools/sfx8bit.py` 用方波和雜訊直接合成,不下載任何音檔。build.py 每次都會依動作重算時間點、重新合成 `assets/audio/sfx.wav`,片尾自動加一段小琶音。

| 名字 | 聽起來像 | 預設給 |
|---|---|---|
| step | 輕輕的腳步 | walk 每一步 |
| jump | 往上滑的嗶 | hop |
| pop | 短促上揚 | pop、big、段落標題 |
| thud | 低沉落地 | drop 落地 |
| whoosh | 風聲 | slide、方塊轉場 |
| hit | 撞擊 | shake |
| slam | 更重的撞擊 | — |
| stamp | 蓋章 | stamp |
| type | 鍵盤 | type 每個字 |
| blip | 對話框打字 | say、馬賽克進場 |
| tick / coin | 跳號 / 最後一下金幣 | count |
| sparkle | 亮晶晶 | sparkle、flash |
| clear | 過關 | clear |
| check / alert / power / levelup / fanfare / gameover / boot / coinin / static / heal / boss / score | 打勾、警示、充能、升級、勝利、遊戲結束、開機、投幣、雜訊、回血、Boss 登場、高分 | 用 `["sfx", "名字"]` 自己放 |

- 換音效:動作加 `{"sound": "coin"}`;不要音效:`{"sound": null}`。
- 全部不要:storyboard 最外層 `"sfx": false`。
- 要新的聲音:在 `sfx8bit.py` 的 `SFX` 加一行(`tone(起點, 長度, 起始頻率, 結束頻率, 音量, 佔空比)`、`noise(...)`、`arp(起點, 音符們, ...)`)。
- 同一支片的「招牌聲音」(撞擊、過關)不要每次都一樣:同類事件可以輪流用 hit / slam、clear / fanfare / levelup。

## 配音對齊

1. 照 `narration.txt` 一句一句錄,存成 `assets/audio/voice.wav`(44.1 kHz)。
2. 量出每句的 `[起, 迄]` 秒數寫進專案根目錄的 `voice.json`,句數要跟 narration.txt 一樣:

```json
[[0.42, 2.71], [2.95, 5.60], [6.10, 8.44]]
```

   量法任選:用剪輯軟體看波形;或用語音辨識(例如 `whisper`)出每個字的時間,取每句第一個字和最後一個字。
3. 重跑 `python tools/build.py`:時間來源會顯示 `voice.json`,畫面、字幕、音效全部對上配音,`index.html` 自動加上配音軌。
4. 配音順口改了字、意思沒變:改 `narration.txt` 讓字幕照錄音走,不用重錄。

## 配樂

模板不附配樂。要配就請使用者先選曲(免費曲庫或自己有授權的),下載前先問;講話時壓低、轉場拉高。
放進 `assets/audio/` 後在 `tools/template.html` 的 `__AUDIO__` 旁邊加一條 `<audio id="bgm" src="assets/audio/bgm.mp3" data-start="0" data-volume="0.25"></audio>`。

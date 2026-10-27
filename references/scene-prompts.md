# 加碼:做過的像素場景提示詞

這些都是實際做片用過、處理後效果好的場景。直接貼進 `jobs.json` 的 `prompt`(風格句 `gen.py` 會自動加),
或整段貼到 ChatGPT(前面加「請用圖片生成畫出下面這張圖,16-bit SNES 像素風,直式 1024×1536,不要有字和人物:」)。

共通的三個要訣:

1. **下方留空地板**:"The lower part (from about 60% to 100% of the height) must be a plain, mostly empty floor so game sprites can stand on it later; keep the bottom 20% simple and slightly darker."
2. **要放東西的地方畫空的**:告示板、桌面、王座、平台都寫 EMPTY,之後再把道具疊上去。
3. **要讓後面的東西露出來就用洋紅**:天空、螢幕畫成 "ONE perfectly flat solid pure magenta color (#FF00FF)",jobs.json 加 `"key": true`。

---

**霓虹街機廳**(範例片用的)
Interior of a retro neon video game arcade at night, side view like a side-scrolling game: a long row of colorful upright arcade cabinets with glowing screens along the back wall, neon tube lights and glowing stars on the dark wall above, a claw machine on the far left edge, a prize counter on the far right edge, patterned arcade carpet. The lower part (from about 60% to 100% of the height) must be a plain, mostly empty carpet floor.

**街機特寫(螢幕挖空)**
Front view close-up of ONE big retro upright arcade cabinet that fills almost the whole image, perfectly symmetric and straight-on (no perspective tilt). From top to bottom: a glowing blank marquee panel (top 6% to 16% of the height, empty glowing light box, no writing); a large screen area from about 19% to 61% of the height and from about 9% to 91% of the width, and this screen area must be ONE perfectly flat solid pure magenta color (#FF00FF) rectangle with a thick dark bezel around it; a wide control panel from about 64% to 80% of the height with one red ball-top joystick on the left and six round arcade buttons on the right; a coin door at the bottom with two glowing coin slots.
→ 螢幕洞後面可以放影片或畫面,像在玩遊戲。

**關卡地圖**
A retro game stage-select overworld map seen from above: grassy islands in a dark blue sea, small pixel trees, a little castle at the top, and a winding dotted path that connects three empty round stone platforms (one at lower left around 20% width / 78% height, one at middle right around 72% width / 55% height, one at upper left around 28% width / 30% height). The platforms must be empty (no flags, no numbers). Keep the area above 12% height as open sea/sky so a title can be placed there.

**夜晚城市街道**
Night city street scene: deep navy-to-purple night sky with a few twinkling stars and a small crescent moon at the top; a skyline of rooftops and buildings with warm amber lit windows in the middle; a few glowing neon shop signs with NO readable text (just abstract neon shapes in pink and cyan); a clean flat street / sidewalk across the lower third with empty space in the center where a small character will stand later.

**中世紀小鎮(天空挖空)**
Side view of a small medieval town street at night, like a side-scrolling game level. The TOP 44% of the image must be a perfectly flat, solid, pure magenta color (#FF00FF) with absolutely nothing in it. From about 44% height down to about 68% height: one continuous row of small cozy medieval houses standing side by side: timber-framed walls, steep red-brown and dark slate tile roofs, a few chimneys, small warm yellow lit windows, wooden doors, one or two little shop awnings, a couple of iron street lamps with warm glow. Roofs must sit directly against the flat magenta area (clean hard edge). From about 68% height to the bottom: a wide, flat, empty cobblestone street.
→ jobs.json 加 `"key": true`,天空換成星空或 K 線。

**地下寶庫**
Inside a dark underground treasure vault / dungeon room: stone brick walls, a few wall torches with warm orange glow, faint purple mist, a big empty stone floor in the middle and lower half, slightly ominous mood, deep navy and purple tones with orange torch light.

**遊戲標題畫面**
Arcade game title screen backdrop: deep space night sky full of small twinkling stars, a glowing neon synthwave grid floor receding to the horizon in the lower third (magenta and cyan lines), a faint big retro sun on the horizon, the upper two thirds mostly dark empty sky for a logo.

**夜晚辦公室**
A modern office at night: a row of desks with dark computer monitors along the back, a big window showing city lights and a moon, a potted plant, one warm desk lamp glowing; cool blue and navy tones with a little warm lamp light; slightly lonely mood.

**小套房**
A small cozy apartment room at night: a window with the moon on the left, a bookshelf on the right, a poster-free wall, warm lamp light; the center and lower middle of the room must be EMPTY (no desk, no chair, no bed) because furniture will be added later.

**冒險者公會**
Interior of a fantasy adventurers' guild hall: a large wooden-framed cork notice board mounted on the back wall in the upper middle, completely EMPTY (no papers, no notes), wooden beams, hanging banners, a candle chandelier, a wooden counter on the far right edge, warm torch light; stone floor in the lower part left empty.
→ 告示板上之後疊任務單、職缺、清單。

**學者書房**
A scholar's study at night: tall wooden bookshelves full of books on both sides, a round window with stars, candles with warm glow, a large wooden writing desk standing in the middle of the room with an EMPTY top surface (nothing on it), warm brown and amber tones.

**王座大廳(Boss 房)**
A castle throne room boss chamber: a long red carpet leading to a large ornate EMPTY throne at the back center on a few steps, tall stone pillars, hanging purple and gold banners, torches with dramatic light, slightly intimidating "final boss" mood, deep purple, red and gold tones.

**海底世界**
Underwater world: deep blue-teal ocean with sunlight rays coming down from the top, tall swaying green kelp on the left and right edges, pink and orange coral reefs, a sunken wooden treasure chest half buried on the far right, rising air bubbles; the floor is soft pale sand.

**太空站**
Inside a retro sci-fi space station: a huge round window in the upper middle showing a big blue-green planet and many stars, metal wall panels with blinking colored lights and small control consoles on the left and right edges, pipes on the ceiling; the floor is a clean metal deck with a subtle grid.

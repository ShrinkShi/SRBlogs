## 2026-05-03 打磨轮更新：页面编辑真实绑定

- 前台工具箱继续作为游客入口：计算器为小浮窗，全局搜索和设置弹窗提高不透明度，设置中可控制字体大小、音乐音量、点击音效和鼠标点击特效。
- 鼠标点击视觉特效响应页面任意点击；点击音效只在按钮、链接、导航、表单操作等交互元素触发。
- 后台可分别关闭站点级点击音效和点击特效，关闭后游客端不可覆盖。
- 后台一级导航调整为：页面编辑、内容管理、评论管理、后台设置、日志备份。
- `/admin/pages/:page?` 页面编辑第一阶段入口已绑定真实配置和数据摘要：可编辑首页作者、头像、简介、社交链接，各页面标题/副标题，以及关于页 Markdown。
- 首页核心模块拆分为 `profileCard`、`musicPlayer`、`lyrics`、`latestPostsCarousel`、`photoCarousel`、`updatesCarousel`、`themeToggle`、`statusBar` 八个可排序/调尺寸模块。
- 首页布局保存到 `backend/data/page_config.json` 的公开 `homeLayout.components`，前台刷新时通过 `GET /api/pages/config` 读取并生效；该配置不包含 Secret。
- 后台“主题与背景 > 前台透明度设置”可以配置工具箱弹窗、首页卡片、内容卡片、留言板和顶部导航栏透明度；前台通过 `GET /api/settings/public` 的 `themeConfig.opacity` 读取。
- 作者、头像、首页简介、社交链接的主编辑入口迁移到“后台 > 页面编辑 > 首页”；设置中心只保留兼容折叠区。
- 操作暂存区默认隐藏，按需从右下角按钮打开。

# SRBlogs

## 当前前台导航与工具箱

前台顶部导航已收敛为：首页、文章、图片、音乐、项目、友链、关于。搜索、杂谈和归档不再显示在顶部导航中，但旧路由仍保留兼容。

- `文章`：进入 `/posts`，可在“正经 / 杂谈”之间切换，并支持“矩阵网格 / 中枢链路”两种显示模式。
- `图片`：进入 `/photowall`，继续使用照片墙相册数据，并支持“矩阵网格 / 中枢链路”两种显示模式。
- `搜索`：移动到左下角工具箱的“全局搜索”弹窗中，旧 `/search` 仍可直接访问。
- `游客设置`：移动到左下角工具箱，可调整昼夜模式、主题、背景、氛围、弹幕、点击音效、音乐音量和字体大小。

左下角工具箱还提供一个轻量计算器。工具箱设置写入浏览器 localStorage，不需要后台登录，也不会读取后台 Secret。

## 2026-05-03 GitHub/QQ 留言登录说明

- 前台留言板通过 `/api/settings/public` 读取 GitHub/QQ 独立 provider 状态。
- GitHub 已配置时会显示“使用 GitHub 登录后留言”；QQ 未配置只影响 QQ，不会影响 GitHub。
- 本地开发环境如未读取到 `VITE_API_BASE_URL`，前台会兜底访问 `http://127.0.0.1:8000/api`，避免登录入口落到前台 404。
- OAuth Secret 不会进入前端或后台构建产物，公开接口只返回布尔 configured 状态。

## 2026-05-03 当前收口说明

- 前台留言板支持 GitHub 与 QQ 两种访客登录入口；各平台配置状态独立判断，未配置的平台只显示中文访客提示，不影响另一个已配置平台。
- OAuth Secret 只保存在后端配置中，`/api/settings/public` 只返回 `configured` 布尔值，不返回 GitHub/QQ Secret。
- 搜索框保持轻量容器、清晰输入框、深色图标按钮；高度更紧凑，背景更不透明。
- 默认本地访问地址保持：前台 `http://127.0.0.1:5173`，后台 `http://127.0.0.1:5174/admin/`，后端 `http://127.0.0.1:8000`。

> 褰撳墠杩涘害锛歅0 100%锛孭1 绾?99%锛孭2 绾?88%銆傛湰杞ˉ淇《灞?Toast銆佸墠鍙?GitHub 璇勮鍏ュ彛銆佸悗鍙?GitHub-only 璇勮璁剧疆銆佺浉鍐岀粍缂栬緫銆佺揣鍑戦椤甸煶涔愭挱鏀惧櫒銆佹瓕璇嶉珮搴﹀拰鍚嶇墖 hover/tooltip銆?
SRBlogs 鏄竴涓熀浜?**Vue 3 + Vite + TypeScript + Tailwind CSS + FastAPI** 鐨勪釜浜哄崥瀹㈢郴缁熴€傚綋鍓嶅伐绋嬫槸瀵规爣 XinghuisamaBlogs 浜у搧鏂瑰悜鐨?Vue3/FastAPI 閲嶅埗鐗堬紝涓嶅鍒跺師椤圭洰婧愮爜銆佸浘鐗囥€佹枃妗堟垨绉佹湁绱犳潗銆?
## 鎶€鏈爤

- 鍓嶅彴锛歏ue 3銆乂ite銆乀ypeScript銆乀ailwind CSS 3.4
- 鍚庡彴锛歏ue 3銆乂ite銆乀ypeScript銆乀ailwind CSS 3.4
- 鍚庣锛欶astAPI銆丣WT銆丮arkdown Front Matter銆丣SON 鏂囦欢瀛樺偍
- 鏁版嵁锛歚backend/data` 涓殑 Markdown銆丣SON銆佽瘎璁恒€佷笂浼犳枃浠跺拰澶囦唤

## 瑙嗚涓庝氦浜?
- 鍓嶅彴閲囩敤缁熶竴姣涚幓鐠?token銆佸崱鐗?hover銆佹爣绛俱€佹寜閽拰闃呰鎺掔増鏍峰紡锛岃鍒欒 [docs/UI_STYLE_GUIDE.md](docs/UI_STYLE_GUIDE.md)銆?- 鑳屾櫙鎺у埗鍖呭惈涓婚銆佽儗鏅€佸脊骞曞拰鈥滄皼鍥粹€濆紑鍏筹紱鍏抽棴姘涘洿鍚庝細鍋滅敤妯辫姳銆佽悿鐏€丆yberCat 鍜岀偣鍑诲厜鏁堢瓑瑁呴グ鍔ㄦ晥銆?- 棣栭〉绗簩闃舵缁撴瀯鍖呭惈閾烘弧寮忛《鏍忋€佸悕鐗?+ 闊充箰鎾斁鍣ㄣ€佹瓕璇?鎾斁鐘舵€佸尯銆佹渶鏂版枃绔犮€佹渶鏂版洿鏂板唴瀹广€佹樇澶滄ā寮忓崱鐗囧拰搴曢儴鐘舵€佸尯銆?- 璁剧疆涓績鏀寔鍏紑涓婚 token銆佸瓧浣撴棌鍜屽瓧鍙锋。浣嶉厤缃紱鍓嶅彴鏄煎妯″紡閫氳繃 CSS 鍙橀噺搴旂敤銆?- 璇勮閲囩敤 GitHub 鐧诲綍鍚庤瘎璁猴紱OAuth Secret 鍙湪鍚庣閰嶇疆锛屽墠绔彧璇诲彇鐧诲綍鐘舵€佸拰 GitHub 鍏紑鐢ㄦ埛淇℃伅銆?- 闊充箰鎾斁鐘舵€佹彁鍗囧埌鍏ㄥ眬锛岄椤靛拰 `/music` 椤甸潰鍏变韩鎾斁杩涘害锛涢煶涔愮鐞嗘敮鎸佹瓕璇?URL / `.lrc` / `.txt`銆?- 鐓х墖澧欐敮鎸佺浉鍐岀粍锛屾瘡缁勬渶澶?50 寮犵収鐗囷紝鏃у崟鍥炬暟鎹粛鍏煎灞曠ず銆?- P0/P1 鍔熻兘宸叉敹鍙ｏ紝P2 瑙嗚澧炲己浠嶆寜楠屾敹娓呭崟閫愯疆鎺ㄨ繘锛屼笉寮曞叆澶у瀷鍔ㄧ敾搴撱€佷笉鍋?3D/Three.js銆?
## 椤圭洰缁撴瀯

```text
SRBlogs/
鈹溾攢鈹€ frontend/               # 璇昏€呯鍗氬 SPA
鈹溾攢鈹€ admin/                  # 鍚庡彴绠＄悊 SPA
鈹溾攢鈹€ backend/                # FastAPI 鍚庣
鈹?  鈹溾攢鈹€ app/                # API銆佹湇鍔″拰閰嶇疆
鈹?  鈹斺攢鈹€ data/               # Markdown銆丣SON銆佽瘎璁恒€佷笂浼犲拰澶囦唤
鈹溾攢鈹€ deploy/                 # Linux 閮ㄧ讲鑴氭湰銆丯ginx銆乻ystemd 鍜屽仴搴锋鏌?鈹溾攢鈹€ docs/                   # 濂戠害銆佸畨鍏ㄣ€侀獙鏀躲€侀儴缃插拰鍙戝竷鏂囨。
鈹溾攢鈹€ start-backend.cmd       # Windows 鍚庣鍚姩
鈹溾攢鈹€ start-frontend.cmd      # Windows 鍓嶅彴鍚姩
鈹溾攢鈹€ start-admin.cmd         # Windows 鍚庡彴鍚姩
鈹溾攢鈹€ start-all.cmd           # Windows 涓夌鍚姩
鈹斺攢鈹€ WINDOWS_START.md
```

## Windows 鏈湴鍚姩

鎺ㄨ崘鐩存帴杩愯锛?
```powershell
.\start-all.cmd
```

鍥哄畾璁块棶鍦板潃锛?
- 鍓嶅彴锛歚http://127.0.0.1:5173`
- 鍚庡彴锛歚http://127.0.0.1:5174/admin/`
- 鍚庣鏂囨。锛歚http://127.0.0.1:8000/docs`
- 鍋ュ悍妫€鏌ワ細`http://127.0.0.1:8000/api/health`

涔熷彲浠ュ垎鍒惎鍔細

```powershell
.\start-backend.cmd
.\start-frontend.cmd
.\start-admin.cmd
```

鍓嶅彴鍜屽悗鍙拌剼鏈浐瀹氱鍙ｅ苟浣跨敤 `--strictPort`銆傚鏋滅鍙ｈ鍗犵敤锛岃剼鏈細杈撳嚭鍗犵敤 PID 鍜?`taskkill` 澶勭悊寤鸿銆?
## 鎵嬪姩鍚姩

鍚庣锛?
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

鍓嶅彴锛?
```powershell
cd frontend
npm install
npm run dev
```

鍚庡彴锛?
```powershell
cd admin
npm install
npm run dev
```

`npm run dev` 鏄父椹诲紑鍙戞湇鍔★紝涓嶄細鑷劧閫€鍑恒€?
## 榛樿鍚庡彴璐﹀彿

```text
鐢ㄦ埛鍚嶏細admin
瀵嗙爜锛歝hange-me
```

榛樿璐﹀彿浠呯敤浜庢湰鍦板紑鍙戙€傜敓浜у墠蹇呴』鍩轰簬 `backend/.env.production.example` 閰嶇疆鏈嶅姟绔幆澧冩枃浠讹紝骞朵慨鏀?`ADMIN_PASSWORD` 鍜?`JWT_SECRET`銆?
## API 鏂囨。

鍚姩鍚庣鍚庤闂細

```text
http://127.0.0.1:8000/docs
```

璇︾粏鎺ュ彛濂戠害瑙?[docs/API_CONTRACT.md](docs/API_CONTRACT.md)銆?
鏃ュ父浣跨敤姝ラ瑙?[docs/USER_GUIDE.md](docs/USER_GUIDE.md)锛屽寘鍚櫥褰曞悗鍙般€佸啓鏂囩珷銆佽崏绋垮彂甯冦€佽瘎璁虹鐞嗐€佸獟浣撶鐞嗐€佺珯鐐硅缃€佸浠芥仮澶嶃€佸璁℃棩蹇楀拰鍓嶅彴鎼滅储/鏍囩/褰掓。浣跨敤璇存槑銆?
## 鍚庡彴涓昏璺敱

- `/admin/`锛氫华琛ㄧ洏
- `/admin/editor`锛歁arkdown 鍐欎綔
- `/admin/posts`銆乣/admin/drafts`锛氭枃绔犱笌鑽夌
- `/admin/comments`锛氭湰鍦拌瘎璁虹鐞?- `/admin/audit`锛氬悗鍙版搷浣滃璁℃棩蹇?- `/admin/backups`锛氭暟鎹浠姐€佷笅杞姐€佹仮澶嶃€佸鍏ュ鍑?- `/admin/friends`銆乣/admin/projects`銆乣/admin/music`銆乣/admin/photos`锛氱粨鏋勫寲鍐呭绠＄悊
- `/admin/settings`锛氳缃腑蹇?
## 鍓嶅彴涓昏璺敱

- `/`锛氶椤?- `/posts`銆乣/posts/:slug`锛氭枃绔犲垪琛ㄥ拰璇︽儏
- `/search`锛氬叏绔欐悳绱?- `/tags`銆乣/tags/:tag`锛氭爣绛剧储寮曞拰鏍囩鍐呭
- `/archive`锛氬唴瀹瑰綊妗?- `/moments`銆乣/moments/:slug`锛氬姩鎬?- `/chatters`銆乣/chatters/:slug`锛氭潅璋?- `/friends`銆乣/projects`銆乣/music`銆乣/photowall`锛氱粨鏋勫寲鍐呭
- `/about`銆乣/timeline`锛氬叧浜庡拰瑙嗚鏃堕棿绾?
## SEO 涓庤闃?
鍏紑鎺ュ彛锛?
- RSS锛歚http://127.0.0.1:8000/api/rss.xml`
- Sitemap锛歚http://127.0.0.1:8000/api/sitemap.xml`
- Robots锛歚http://127.0.0.1:8000/robots.txt`

鍓嶅彴鏂囩珷鍒楄〃鍜屽叧浜庨〉鎻愪緵 RSS 鍏ュ彛銆傜敓浜х幆澧冭鍦ㄥ悗绔?`.env` 璁剧疆 `PUBLIC_BASE_URL`锛岀敤浜?RSS銆丼itemap銆乺obots 鍜屼笂浼?URL銆?
## 鎬ц兘涓庡彲璁块棶鎬?
- 鍓嶅彴鍥剧墖缁熶竴閫氳繃瀹夊叏鍥剧墖缁勪欢澶勭悊鎳掑姞杞姐€乣alt` 鍜屽姞杞藉け璐ュ厹搴曘€?- 涓昏鍒楄〃銆佹悳绱€佸綊妗ｇ瓑椤甸潰鏈夊姞杞姐€佺┖鐘舵€佸拰閿欒鐘舵€侊紝API 澶辫触鏃朵笉搴旂櫧灞忋€?- Markdown 浠ｇ爜鍧楀拰琛ㄦ牸鍏佽鑷韩妯悜婊氬姩锛岄伩鍏嶆拺瀹芥暣椤点€?- 鍚庡彴渚ф爮鍦ㄧ獎灞忎笅鍙粴鍔紝鍐欎綔銆佽缃€佽瘎璁虹鐞嗙瓑椤甸潰闇€淇濇寔鍙搷浣溿€?- 褰撳墠 MarkdownRenderer 鍜?MarkdownEditor 鏋勫缓 chunk 鍋忓ぇ锛屼絾鍒嗗埆浣嶄簬鏂囩珷璇︽儏鍜岀紪杈戝櫒鎳掑姞杞借矾寰勶紱鍙戝竷鍓嶄粛闇€鍏虫敞浣撶Н鍜岄灞忎綋楠屻€?
## 鏁版嵁鐩綍

`backend/data` 鏄綋鍓嶆枃浠跺瓨鍌ㄦ牴鐩綍锛?
- `posts/*.md`锛氭枃绔?- `moments/*.md`锛氬姩鎬?- `chatters/*.md`锛氭潅璋?- `comments/*.json`锛氳瘎璁?- `friends.json`銆乣projects.json`銆乣music.json`锛氱粨鏋勫寲鍐呭
- `photos/photos.json`锛氱収鐗囧鏁版嵁
- `uploads/`锛氭湰鍦颁笂浼犳枃浠?- `.backups/`锛氳鐩栧啓鍏ユ垨鍒犻櫎鍓嶇殑澶囦唤
- `audit/audit.log`锛氬悗鍙版搷浣滃璁℃棩蹇?- `.manual_backups/*.zip`锛氬悗鍙版墜鍔ㄥ浠姐€佸鍑哄拰鎭㈠鍓嶅浠?
鎵€鏈?JSON/Markdown 鍐欏叆蹇呴』閫氳繃鍚庣瀹夊叏鍐欏叆灏佽锛岀姝笟鍔¤矾鐢辩洿鎺?`open(..., "w")` 鍐欐枃浠躲€?鎵嬪姩澶囦唤涓嶅寘鍚?`.env`銆佸墠绔簮鐮併€乣node_modules`銆乣dist` 鎴?`.manual_backups` 鏈韩锛沗settings.json` 鍐欏叆澶囦唤鍓嶄細鍓旈櫎 Secret 瀛楁銆?
浠撳簱涓殑绀轰緥鏁版嵁鐢ㄤ簬鏈湴婕旂ず鍜屽洖褰掗獙璇侊紝鍖呭惈鍏紑鏂囩珷銆佽崏绋裤€佸姩鎬併€佹潅璋堛€佸弸閾俱€侀」鐩€侀煶涔愩€佺収鐗囧拰 about 鍐呭銆傝繍琛屾椂鐢熸垚鐨勬墜鍔ㄥ浠姐€佸璁℃棩蹇椼€佷笂浼犵紦瀛樺拰 `.backups` 鏂囦欢涓嶅簲浣滀负鍙戝竷浠ｇ爜鎻愪氦銆?
## 鏋勫缓

```powershell
cd frontend
npm run build
```

```powershell
cd admin
npm run build
```

```powershell
python -m compileall backend\app
```

鏋勫缓浜х墿锛?
- `frontend/dist`
- `admin/dist`

## 閮ㄧ讲

鏈嶅姟鍣ㄩ儴缃茶鏄庤 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)锛屽寘鍚細

- FastAPI 鍚姩
- 鍓嶅彴/鍚庡彴 build
- Nginx 鍙嶅悜浠ｇ悊绀轰緥
- systemd 鏈嶅姟绀轰緥
- `backend/data` 鏉冮檺
- 鐢熶骇 `.env`
- HTTPS 鍜岀敓浜у墠妫€鏌?
鐢熶骇鍙戝竷鍊欓€夊弬鑰冩枃浠讹細

- `backend/.env.production.example`锛氱敓浜х幆澧冨彉閲忔ā鏉匡紝涓嶅寘鍚湡瀹?Secret銆?- `deploy/build-all.sh`锛氭瀯寤哄墠鍙般€佸悗鍙板苟妫€鏌ュ悗绔娉曘€?- `deploy/start-backend.sh`锛歀inux 鍚庣鍚姩鑴氭湰銆?- `deploy/srblogs-backend.service`锛歴ystemd 绀轰緥銆?- `deploy/nginx.srblogs.conf`锛歂ginx 绀轰緥銆?- `deploy/healthcheck.sh`锛氱敓浜у仴搴锋鏌ヨ剼鏈€?- [docs/PRODUCTION_CHECKLIST.md](docs/PRODUCTION_CHECKLIST.md)锛氱敓浜у彂甯冩竻鍗曘€?- [CHANGELOG.md](CHANGELOG.md) 涓?[docs/RELEASE_NOTES.md](docs/RELEASE_NOTES.md)锛氬彂甯冭鏄庛€?
## 甯歌闂

### Tailwind v3/v4 闂

鏈」鐩綋鍓嶅浐瀹氫娇鐢?Tailwind CSS `3.4.17`銆備笉瑕佺洿鎺ュ崌绾у埌 Tailwind v4锛屽惁鍒欑幇鏈夐厤缃拰鏍峰紡鍏ュ彛鍙兘涓嶅吋瀹广€?
### `pydantic_core` 瀹夎鎹熷潖

閲嶆柊鍒涘缓鍚庣铏氭嫙鐜锛?
```powershell
cd backend
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Vite 绔彛璺宠浆鍜?CORS

鍓嶅彴鍥哄畾 `5173`锛屽悗鍙板浐瀹?`5174`锛屽苟鍚敤 `--strictPort`銆傚鏋滅鍙ｈ鍗犵敤锛屽厛閲婃斁绔彛锛屼笉瑕佽 Vite 鑷姩璺崇鍙ｏ紝鍚﹀垯鍙兘瑙﹀彂 CORS 鎴栧洖璋冨湴鍧€涓嶄竴鑷淬€?
### `npm run dev` 涓€鐩翠笉閫€鍑?
杩欐槸姝ｅ父琛屼负銆俈ite dev server 鏄父椹昏繘绋嬨€傞渶瑕佸仠姝㈡椂鍦ㄥ搴旂粓绔寜 `Ctrl+C`銆?
### 8000 绔彛鍗犵敤鎴栨潈闄愰棶棰?
妫€鏌ュ崰鐢細

```powershell
netstat -ano | findstr :8000
```

纭杩涚▼鍙互鍋滄鍚庡啀鎵ц锛?
```powershell
taskkill /PID <PID> /F
```

## 褰撳墠浜や粯鐘舵€?
- 鍙嬮摼銆侀」鐩€侀煶涔愩€佺収鐗囧宸查€氳繃浜哄伐楠屾敹骞跺湪鐭╅樀涓爣璁颁负 `宸插畬鎴恅銆?- 瀹¤鏃ュ織涓庡浠芥仮澶嶅凡閫氳繃浜哄伐楠屾敹骞跺彲鍦ㄧ煩闃典腑鏍囪涓?`宸插畬鎴恅銆?- 鍚庡彴鍐欎綔銆佽崏绋裤€佸彂甯?鎾ゅ洖銆佸垹闄ゆ枃绔犲拰 pendingOperations 绗竴闃舵宸查€氳繃浜哄伐楠屾敹骞跺湪鐭╅樀涓爣璁颁负 `宸插畬鎴恅銆?- 璁剧疆涓績鍓╀綑椤瑰凡瀹屾垚楠屾敹锛氱┖ Secret 淇濈暀銆佽瘎璁哄紑鍏炽€佸浘搴?local 涓婁紶銆丄I 璁剧疆杈圭晫鍜岄儴缃叉枃妗ｆ牳楠屽潎宸查€氳繃锛涚湡瀹?OSS/Gitalk/AI 鑱旇皟浠嶄笉灞炰簬褰撳墠 P0/P1 鏀跺彛鑼冨洿銆?- 鏈€缁堟€诲洖褰掑凡瀹屾垚 API/HTTP 蹇€熼獙璇侊細瀹屾暣鍐呭鐢熶骇婕旂ず娴併€佽瘎璁哄墠鍚庡彴鍚屾銆佸璁℃棩蹇椼€佹墜鍔ㄥ浠姐€佷笅杞藉浠姐€佹仮澶嶅墠澶囦唤銆丷SS/Sitemap/robots銆丼ecret 鎵弿鍧囬€氳繃銆?- 褰撳墠杩涘害浼扮畻锛歅0 100%锛孭1 100%锛孭2 绾?74%锛汸2 宸茶繘鍏ラ椤电粨鏋勮拷骞充笌鏄煎涓婚绯荤粺闃舵锛屼粛闇€鎸変汉宸ラ獙鏀舵竻鍗曠户缁‘璁ゃ€?- 鐪熷疄鏈嶅姟鍣ㄣ€佸煙鍚嶅拰 HTTPS 閮ㄧ讲瀹炴搷浠嶆爣璁颁负 `閮ㄧ讲瀹炴搷寰呮墽琛宍锛涘綋鍓嶄粨搴撴彁渚涚殑鏄笂绾垮噯澶囪剼鏈€丯ginx/systemd 绀轰緥銆佺幆澧冨彉閲忔ā鏉垮拰閮ㄧ讲妫€鏌ユ竻鍗曘€?- 鍙戝竷鍓嶆€绘鏌ヨ [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md)銆?# SRBlogs 褰撳墠琛ュ厖

> 褰撳墠杩涘害锛歅0 100%锛孭1 绾?98%锛孭2 绾?90%銆傛湰杞ˉ淇墠鍙?GitHub 璇勮鍏ュ彛銆佹枃绔?鏉傝皥涓夊垪鍥剧墖鍒楄〃銆侀煶涔愰〉宸︽挱鏀惧櫒鍙虫瓕璇?姝屽崟甯冨眬銆侀椤垫挱鏀惧櫒绱у噾鍖栧拰闈為椤垫爣棰樺眳涓紱鐪熷疄 GitHub OAuth 鍥炶烦浠嶉渶閰嶇疆鍚庝汉宸ラ獙鏀躲€?
> 鏈€鏂拌ˉ鍏咃細鍓嶅彴璇勮鍖虹粺涓€鍛藉悕涓衡€滅暀瑷€鏉库€濓紝GitHub 鏈厤缃彁绀烘敼涓鸿瀹㈣瑙掞紱鏂囩珷椤垫柊澧炩€滅煩闃电綉鏍?/ 涓灑閾捐矾鈥濆弻妯″紡锛涢《閮ㄥ鑸Щ闄ゅ綊妗ｅ叆鍙ｄ絾 `/archive` 淇濈暀锛涙悳绱㈡爮鍜屾挱鏀惧櫒鍥炬爣鎸夐挳杩涗竴姝ヨ交閲忓寲銆?> 鏈疆淇锛氱暀瑷€鏉跨櫥褰曞叆鍙ｆ敼涓哄墠鍙?`returnTo` OAuth 娴佺▼锛屽叕寮€ `comments.githubLoginConfigured` 甯冨皵鐘舵€侊紝鏈櫥褰曞尶鍚嶇暀瑷€鍚庣杩斿洖 401锛涚収鐗囧鐩稿唽缂栬緫寮圭獥鏀寔 85vh 鍐呴儴婊氬姩锛涙枃绔犱腑鏋㈤摼璺仮澶嶅乏鍙充氦鏇垮苟璐撮潬涓績绾匡紱鎼滅储妗嗗幓鎺?`Search` 瀛楁牱骞跺鍔犳繁鑹叉悳绱㈠浘鏍囨寜閽€?
### 褰撳墠鍓嶅彴浣撻獙琛ュ厖

- 鐣欒█鏉匡細鍓嶅彴璇︽儏椤典娇鐢?GitHub 鐧诲綍鍚庣暀瑷€锛涙湭閰嶇疆鏃舵樉绀鸿瀹㈠弸濂芥彁绀猴紝涓嶆毚闇叉湇鍔＄ Secret 閰嶇疆缁嗚妭銆?- 鏂囩珷鍒楄〃锛氭敮鎸佺煩闃电綉鏍煎拰涓灑閾捐矾涓ょ鏄剧ず妯″紡锛屽崱鐗囨爣绛鹃潬杩戝簳閮ㄣ€?- 闊充箰锛氶椤垫挱鏀惧櫒鍜?`/music` 椤甸潰鍏变韩鍏ㄥ眬鎾斁銆侀煶閲忓拰闈欓煶鐘舵€併€?- 鐓х墖澧欙細鍚庡彴鐩稿唽缂栬緫寮圭獥鏀寔婊氬姩绠＄悊缁勫唴鐓х墖銆?

## 2026-05-03 Message Login Update

SRBlogs message boards support GitHub and QQ visitor login. OAuth secrets are server-side only. Public settings expose only configured booleans. Music uses a global message board target, and photowall album dialogs use per-album message targets.
## 2026-05-04 打磨补充：组件样式 DIY 与音乐喜欢

- 后台“主题与背景”支持组件级样式 DIY：主要前台组件可以分别配置日间/夜间颜色、透明度 `0..1` 和大小档位。
- `/api/settings/public` 会返回公开的 `themeConfig.componentTheme`，只包含视觉配置，不包含任何 Secret。
- 首页和音乐页播放器支持“顺序播放 / 随机播放 / 单曲循环”，状态保存在浏览器本地。
- 首页和音乐页播放器支持歌曲喜欢按钮；喜欢数写入后端 `music.json`，旧歌曲默认 `likes=0`。
- 音乐页歌单默认按喜欢数降序展示，喜欢数相同时保持原排序。
## 2026-05-04 打磨轮更新：页面编辑精细尺寸与后台平面化

- 后台“页面编辑 > 首页”已支持组件宽度/高度滑动条和精确数值输入。
- 首页布局配置继续通过 `/api/admin/pages/config` 保存，通过 `/api/pages/config` 公开读取，刷新前台后真实生效。
- 首页桌面布局使用 120 子列映射，`w` 支持 `0.1` 精度，`h` 支持 `0.1` 精度。
- 后台管理端已调整为黑白灰平面简约风，前台玻璃风格和组件级主题系统不受影响。
- 后台 UI 改造仅限 admin 应用，前台仍保持现有首页、文章、图片、音乐、项目、友链、关于、留言板和工具箱体验。
## 2026-05-04 页面编辑器调整说明

后台页面编辑器已暂时移除拖拽排序，避免与宽度/高度滑动条冲突。组件位置通过“上移 / 下移 / order 数值”调整；组件宽高通过滑动条和数值输入调整。前台首页会继续读取 `/api/pages/config`，但高度映射已改为更克制的比例，避免后台调试值把首页组件异常拉高。

## 2026-05-04 打磨更新：多页面页面编辑

后台“页面编辑”已从首页扩展到首页、文章、图片、音乐、项目、友链、关于七类页面。页面布局配置通过后端接口保存：

- 前台读取：`GET /api/pages/config`
- 后台读取：`GET /api/admin/pages/config`
- 后台保存：`PUT /api/admin/pages/config`

布局配置保存在 `backend/data/page_config.json`。每个页面使用 `pageLayouts.{page}.components` 描述组件顺序、宽度、高度和显示状态。核心组件可隐藏，自定义组件可删除；这些操作只影响页面布局，不删除真实内容数据。

后台设置中心继续保持黑白灰平面化管理风格。首页作者、头像、简介和社交链接的主编辑入口迁移到“页面编辑 > 首页”。
## 2026-05-05 打磨更新

- 页面编辑中的真实字段编辑已改为按钮弹窗，主编辑区更专注于组件布局。
- 页面编辑操作栏支持 sticky，滚动时仍可保存、添加组件和恢复默认布局。
- 组件设置弹窗支持字体族、字号、字体颜色、文本对齐、加粗和斜体，并保存到组件主题配置。
- 前台留言板不再显示开发调试 target；首页和音乐页播放器喜欢数与喜欢按钮水平显示。

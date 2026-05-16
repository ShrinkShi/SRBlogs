# Security Notes

## 2026-05-15 昼夜壁纸轮播公开字段

- `themeConfig.modes.day/night.slideshowEnabled`、`slideshowInterval` 和 `slideshowEffect` 属于公开视觉配置，可以进入 `/api/settings/public` 和主题导出 JSON。
- 白天模式前台按 `overlayOpacity=0` 使用，不应通过白色蒙层遮挡壁纸；夜间蒙层仅用于提升文字可读性。
- 壁纸轮播配置不得保存本地磁盘绝对路径、SMTP/OAuth/OSS Secret、管理员 token 或任何服务端私密字段。

## 2026-05-05 主题包与内容布局安全规则

- 主题包属于公开视觉配置，只能保存颜色、字体、透明度、背景壁纸 URL、组件样式和页面布局。
- 主题导入、导出和一键应用不得包含 GitHub/QQ Secret、AI Key、OSS Secret、JWT、管理员密码、access token 或服务端私有路径。
- `themeConfig.layout.pagePadding` 仅作为旧主题包兼容字段处理，可以出现在 `/api/settings/public` 中，但不再作为前台主内容宽度控制入口。
- 主题包导出不再包含 `pageLayouts`、页面布局或组件级低代码样式。导入旧主题包时如包含 `pageLayouts` / `componentTheme`，后台只做兼容提示并忽略这些字段，不写入前台布局。
- `/api/pages/config` 中历史布局字段只作为 legacy compatibility 保留，前台不再使用它们渲染页面结构；该配置仍不得保存脚本、Secret、access token、服务器绝对路径或任意可执行代码。
- `modes.day.bgImages` 与 `modes.night.bgImages` 只允许保存公开可访问的壁纸 URL、名称、启用状态和默认索引，不得保存本地磁盘绝对路径或私有凭据。

## 2026-05-05 主题包与页面边距安全规则

- 主题包属于公开视觉配置，只能保存颜色、字体、透明度、页面边距、背景壁纸 URL、组件样式和页面布局。
- 主题导入/导出不得包含 GitHub OAuth Secret、QQ App Secret、AI Key、OSS Secret、JWT、管理员密码、访问 token 或服务端绝对路径。
- `themeConfig.layout.pagePadding` 是公开布局字段，可以出现在 `/api/settings/public` 中。
- `modes.day.bgImages` 与 `modes.night.bgImages` 只允许保存公开可访问的壁纸 URL、名称、启用状态和默认索引，不得保存本地磁盘绝对路径或私有凭据。
- 删除主题只删除主题库中的视觉配置，不得删除文章、照片、音乐、留言、备份或上传文件。
- 当前启用主题禁止直接删除，需先切换到其他主题，避免前台读取不到 active theme。

## 2026-05-03 页面配置与首页布局安全规则

- `backend/data/page_config.json` 只保存公开页面文案、首页资料卡公开字段和首页模块布局，不得保存 Secret、管理员 Token、OAuth access token、服务端绝对路径、脚本或任意 HTML。
- `GET /api/pages/config` 是公开读取接口，只返回前台需要展示的页面配置。
- `GET /api/admin/pages/config` 和 `PUT /api/admin/pages/config` 必须需要管理员 JWT。
- 页面配置写入必须继续走 `JsonStore.write` / `safe_write_json`，覆盖前生成备份。
- 首页布局只允许固定组件 ID：`profileCard`、`musicPlayer`、`lyrics`、`latestPostsCarousel`、`photoCarousel`、`updatesCarousel`、`themeToggle`、`statusBar`；不要让前台执行任意组件名或脚本。
- 页面布局配置只允许保存固定组件 ID、顺序、宽度、高度和公开文案；不得保存脚本、HTML 注入片段、access token、Secret 或服务器绝对路径。
- `themeConfig.opacity` 属于公开视觉配置，只允许保存 0.60-1.00 的数字；它不能承载任何私密配置。
- 字体大小游客设置只能改变文字 `font-size`，不得通过 `zoom`、根字号缩放或 `transform: scale()` 放大整页、卡片、图片、播放器、弹窗或布局容器。
- 点击视觉特效只在前端生成临时 DOM，不记录用户点击内容，也不向后端发送点击轨迹。

## 2026-05-03 多平台留言登录安全规则

- GitHub OAuth Secret 与 QQ App Secret 只能保存在后端 `.env` 或服务端配置中，不能进入 `frontend/dist`、`admin/dist` 或 `/api/settings/public`。
- `/api/settings/public` 只能返回 `configured`、`clientIdConfigured`、`appIdConfigured`、`secretConfigured` 等布尔值。
- GitHub 与 QQ 的配置状态必须独立判断，不能因为 QQ 未配置而禁用 GitHub 留言。
- OAuth 登录必须由后端生成授权地址，并校验 CSRF `state` 后才创建访客登录 cookie。
- 前端留言板只能显示访客友好提示，不得出现 Secret、`.env`、后端配置路径、Client Secret 等开发者细节。
- 未登录提交留言必须返回 401，不允许恢复匿名本地留言入口。

## 2026-05-03 多平台留言登录安全补充

- GitHub OAuth Secret 和 QQ App Secret 只能保存在后端 `.env` 或服务端配置中，不得进入 `frontend/dist` 或 `admin/dist`。
- `GET /api/settings/public` 只能公开 `comments.providers.github.configured` 和 `comments.providers.qq.configured` 这类布尔状态，不得返回任何 Secret、access token 或服务端路径。
- GitHub 与 QQ 的配置状态必须独立判断，QQ 未配置不得导致 GitHub 登录入口不可用。
- GitHub / QQ OAuth 登录入口必须由后端生成授权地址，并使用 CSRF `state` 校验。
- OAuth callback URL 必须指向 FastAPI 后端 `/api/auth/{provider}/callback`，不能依赖前台 URL 拼接，避免回调落到 SPA 导致 404。
- 前台未配置提示必须面向访客，不得出现“后端”“Secret”“Client Secret”或 `.env` 等配置细节。
- 留言提交必须依赖 HttpOnly 访客登录 cookie；未登录 `POST /api/comments/{resource}/{slug}` 返回 `401`。

## Secret Storage

- JWT Secret銆佺鐞嗗憳瀵嗙爜銆丄I Key銆丱SS Key銆丟itHub OAuth Secret 鍙兘淇濆瓨鍦ㄥ悗绔?`.env` 鎴栨湇鍔＄閰嶇疆銆?- 鍓嶅彴鍙兘璇诲彇 `GET /api/settings/public` 杩斿洖鐨勫叕寮€绔欑偣閰嶇疆銆?- 鍚庡彴 settings 鎺ュ彛涔熶笉寰楄繑鍥?Secret 鏄庢枃锛屽彧鑳借繑鍥?`xxxConfigured` 甯冨皵鍊笺€?- 涓嶅緱鎶?Secret 鍐欏叆 `frontend/`銆乣admin/` 鎴栦换浣曚細杩涘叆鏋勫缓浜х墿鐨勬枃浠躲€?
## Settings Boundary

- `GET /api/settings/public` 鍙兘杩斿洖绔欑偣鏍囬銆佸壇鏍囬銆佷綔鑰呫€佸ご鍍忋€佺畝浠嬨€佺ぞ浜ら摼鎺ャ€佷富棰樸€佽儗鏅浘銆佸叕寮€闊充箰閰嶇疆鍜屽叕寮€璇勮鏄剧ず閫夐」銆?- `GET /api/admin/settings` 蹇呴』瑕佹眰绠＄悊鍛?JWT锛屼笖涓嶅緱鍥炴樉 AI Key銆丱SS Key銆丟itHub OAuth Secret 鏄庢枃銆?- 鍚庡彴閰嶇疆鍙兘閫氳繃 `aiKeyConfigured`銆乣accessKeyConfigured`銆乣secretKeyConfigured`銆乣ossKeyConfigured`銆乣githubOAuthSecretConfigured` 绛夊竷灏斿€艰〃杈?Secret 鏄惁宸查厤缃€?- `PUT /api/admin/settings` 涓?Secret 瀛楁涓虹┖瀛楃涓层€乣null` 鎴栨湭浼犳椂锛屽繀椤讳繚鎸佹棫鍊硷紱鍙湁浼犲叆鏄庣‘鏂板€兼椂鎵嶅厑璁歌鐩栥€?- GitHub OAuth Secret 浠呬綔涓烘湇鍔＄閰嶇疆鎴栧悗鍙板啓鍏ュ瓧娈靛瓨鍦紝鍓嶅彴璇勮鍖哄彧鍏佽璇诲彇鍏紑鏄剧ず閰嶇疆锛屼笉鎺ュ叆鎴栨毚闇茬湡瀹?OAuth Secret銆?- 姣忔鍙戝竷鍓嶅繀椤诲 `frontend/dist` 鍜?`admin/dist` 鍋氶潤鎬佹悳绱紝纭娌℃湁榛樿瀵嗙爜銆丣WT Secret銆丄I Key銆丱SS Key銆丟itHub OAuth Secret 鎴栫湡瀹?Secret 鍊笺€?
## Public SEO Endpoints

- `GET /api/rss.xml`銆乣GET /api/sitemap.xml` 鍜?`GET /robots.txt` 鏄叕寮€鎺ュ彛锛屼笉闇€瑕?JWT銆?- RSS 鍜?sitemap 鍙兘鍖呭惈鍏紑鍐呭锛宍draft=true` 鐨?posts/moments/chatters 涓嶅緱杩涘叆杈撳嚭銆?- RSS description 蹇呴』缁忚繃 XML/HTML 杞箟锛屼笉寰楄緭鍑烘湭缁忚浆涔夌殑 Markdown/HTML銆?- robots 蹇呴』绂佹鐖彇 `/admin`锛屼笉寰楁毚闇?`.env`銆佸浠界洰褰曘€佹湇鍔″櫒缁濆璺緞鎴?Secret銆?- OpenGraph銆乀witter Card銆丷SS銆丼itemap 浣跨敤鐨勭珯鐐?URL 鍙兘鏉ヨ嚜鍏紑 base URL 鎴栧綋鍓嶆祻瑙堝櫒 origin锛屼笉寰楀啓鍏ュ悗鍙?admin 鍦板潃鎴栫鏈夐厤缃€?
## Uploads

- 2026-05-03 璧凤紝鏈湴涓婁紶鍏ュ彛鏀寔鍥剧墖銆侀煶棰戙€佽棰戝拰姝岃瘝鏂囨湰璧勬簮锛屼絾浠嶅繀椤昏姹傜鐞嗗憳 JWT锛屽苟缁х画鎵ц鎵╁睍鍚嶃€丮IME 鍜屽ぇ灏忎笁閲嶆牎楠屻€?- 鍏佽鐨勯煶棰?瑙嗛/姝岃瘝璧勬簮鍙敤浜庢湰鍦版枃浠舵墭绠″拰 URL 鍥炲～锛屼笉浠ｈ〃鍏佽鎵ц鑴氭湰鎴栦笂浼犱换鎰忎簩杩涘埗鏂囦欢銆?- 涓婁紶杩斿洖 URL 鍙啓鍏ュご鍍忋€佽儗鏅€佺浉鍐岀収鐗囥€佸皝闈€侀煶涔?URL銆佹瓕璇?URL 鎴栧悗缁棰戝瓧娈碉紱缁撴瀯鍖?JSON 鐨勪繚瀛樹粛蹇呴』璧板悗绔?API 鍜屽畨鍏ㄥ啓鍏ュ皝瑁呫€?- 涓婁紶澶у皬鎸夌被鍨嬪垎妗ｉ檺鍒讹細鍥剧墖榛樿 10 MB锛岄煶棰戦粯璁?100 MB锛岃棰戦粯璁?200 MB锛屾瓕璇?`.lrc/.txt` 榛樿 1 MB锛涚姝㈠叧闂ぇ灏忛檺鍒舵垨鍏佽浠绘剰鏂囦欢绫诲瀷銆?
- 涓婁紶鎺ュ彛蹇呴』瑕佹眰绠＄悊鍛?JWT銆?- 鍚庣蹇呴』鍚屾椂鏍￠獙鎵╁睍鍚嶃€丮IME 鍜屽ぇ灏忋€?- 褰撳墠鍏佽锛歚.jpg`銆乣.jpeg`銆乣.png`銆乣.gif`銆乣.webp`銆乣.svg`銆乣.mp3`銆乣.wav`銆乣.ogg`銆乣.m4a`銆乣.mp4`銆乣.webm`銆乣.mov`銆乣.lrc`銆乣.txt`銆?- 褰撳墠鍏佽 MIME锛氭寜 `UPLOAD_ALLOWED_TYPES` 閰嶇疆鏍￠獙鍥剧墖/闊抽/瑙嗛锛涙瓕璇嶆枃浠跺彧鍏佽鏂囨湰绫诲瀷銆?- 褰撳墠澶у皬涓婇檺锛氬浘鐗?10 MB銆侀煶棰?100 MB銆佽棰?200 MB銆佹瓕璇?1 MB銆?
## Slug And Paths

- `slug` 蹇呴』閫氳繃 `validate_slug`銆?- 绂佹绌哄瓧绗︿覆銆乣..`銆乣/`銆乣\` 鍜岀櫧鍚嶅崟澶栧瓧绗︺€?- 鎵€鏈夋暟鎹矾寰勫繀椤婚€氳繃 `resolve_data_path`锛屾渶缁堣矾寰勫繀椤讳粛浣嶄簬 `backend/data` 鍐呫€?- 绂佹涓氬姟璺敱鎷兼帴浠绘剰鏂囦欢绯荤粺璺緞鍚庡啓鍏ャ€?
## Markdown And Comments

- 鍓嶅彴 Markdown 娓叉煋蹇呴』缁忚繃 DOMPurify 娓呮礂銆?- 璇勮鎻愪氦鍐呭蹇呴』鐢卞悗绔竻娲楀悗淇濆瓨銆?- 鏂拌瘎璁哄彧鍏佽 GitHub 鐧诲綍韬唤鎻愪氦锛涙湭鐧诲綍蹇呴』杩斿洖 401锛屼笉寰楀洖閫€鍒板尶鍚嶈瘎璁恒€?- GitHub OAuth code flow 蹇呴』鐢卞悗绔畬鎴愬苟鏍￠獙 CSRF `state`锛汷Auth Client Secret 鍙兘淇濆瓨鍦ㄥ悗绔?`.env` 鎴栨湇鍔＄閰嶇疆銆?- 鍓嶇鍙厑璁歌鍙?`/api/auth/github/me` 杩斿洖鐨?configured 鐘舵€佸拰 GitHub 鍏紑鐢ㄦ埛淇℃伅锛屼笉鑳借幏寰?OAuth access token 鎴?Secret銆?- 璇勮 JSON 涓嶅緱淇濆瓨 GitHub access token锛屽彧淇濆瓨蹇呰鐨?GitHub 鐧诲綍鍚嶃€佸ご鍍?URL銆佹樉绀哄悕鍜岃瘎璁哄唴瀹广€?- Markdown 鍐呭鍏佽鐢ㄦ埛杈撳叆锛屼絾娓叉煋鏃朵笉寰楃洿鎺ユ彃鍏ユ湭缁忔竻娲楃殑 HTML銆?- 鍚庡彴鍒犻櫎璇勮蹇呴』瑕佹眰绠＄悊鍛?JWT銆?- 鍚庡彴璇勮绱㈠紩 `GET /api/admin/comments/index` 蹇呴』瑕佹眰绠＄悊鍛?JWT锛屽彧杩斿洖 `resource`銆乣slug`銆乣count`銆乣updatedAt`銆乣title` 绛夌鐞嗙储寮曞瓧娈点€?- 鍒犻櫎璇勮鍓嶅繀椤诲浠藉搴旇瘎璁?JSON 鏂囦欢銆?- 璇勮寮€鍏冲拰鏈€澶ч暱搴﹀繀椤诲湪鍚庣 API 寮哄埗鎵ц锛屼笉鑳藉彧渚濊禆鍓嶇 UI銆?- 鏃ф湰鍦伴偖绠辫瘎璁洪厤缃笉鍐嶄綔涓哄悗鍙颁富娴佺▼灞曠ず锛涙柊璇勮鍥哄畾浣跨敤 GitHub 鐧诲綍韬唤锛屼笉鍐嶆帴鍙楀墠绔紶鍏ヤ綔鑰?閭銆?- 璇勮鍐呭鍜屾樀绉板啓鍏ュ墠蹇呴』缁х画鐢?bleach 娓呮礂锛屽墠绔睍绀轰笉寰楃洿鎺ユ覆鏌撳嵄闄?HTML銆?- 鍒犻櫎涓嶅瓨鍦ㄧ殑璇勮蹇呴』杩斿洖 404锛屼笉鍏佽闈欓粯鎴愬姛銆?- 璇勮绠＄悊涓嶈繘鍏ョ涓€闃舵鏈湴 `pendingOperations`锛屽垹闄ゆ搷浣滃綋鍓嶄负绠＄悊鍛樼‘璁ゅ悗鐩存帴鎸佷箙鍖栧啓鍥炲悗绔?JSON銆?
## JSON And Markdown Writes

- 鎵€鏈?JSON/Markdown 璇诲啓蹇呴』璧?`backend/app/services/file_store.py`銆?- 鍐欏叆蹇呴』浣跨敤涓存椂鏂囦欢 + 鍘熷瓙鏇挎崲銆?- 瑕嗙洊鎴栧垹闄ゅ凡鏈夋枃浠跺墠蹇呴』璋冪敤 `backup_file`銆?- 鍏紑鍐呭鎺ュ彛涓嶅緱杩斿洖 `draft=true` 鍐呭锛沗include_drafts=true` 鍙兘鍦ㄧ鐞嗗憳 JWT 涓嬩娇鐢ㄣ€?- 鏂囩珷鍙戝竷銆佹挙鍥炲彂甯冦€佺紪杈戝拰鍒犻櫎蹇呴』鍐欏璁℃棩蹇楋紱鍒犻櫎 Markdown 鍓嶅繀椤诲浠藉師鏂囦欢銆?- 绂佹涓氬姟璺敱鎴栦笟鍔?service 鐩存帴 `open(..., "w")` 鍐?JSON/Markdown銆?- friends/projects/music/photos 鐨勮〃鍗曞寲绠＄悊鍜岄珮绾?JSON 缂栬緫閮藉繀椤婚€氳繃 `JsonStore.write` 鍐欏叆锛屼笉鍏佽鍓嶇缁曡繃 API 鐩存帴鏀规枃浠躲€?- 楂樼骇 JSON 缂栬緫鍙綔涓哄厹搴曞叆鍙ｏ紝淇濆瓨鍓嶅繀椤绘牎楠?JSON 鏍煎紡涓旀牴鑺傜偣蹇呴』涓烘暟缁勩€?- 鍥剧墖涓婁紶鍙啓鍏ヤ笂浼犳枃浠跺苟杩斿洖 URL锛涚収鐗囪褰曚粛闇€閫氳繃 `/api/photos` 鍐欏叆 JSON锛屼笖涓嶈繘鍏ユ湰鍦?`pendingOperations`銆?
## Audit Logs And Backups

- 鍚庡彴瀹¤鏃ュ織鍐欏叆 `backend/data/audit/audit.log`锛屼娇鐢?JSON Lines锛屾瘡鏉℃棩蹇楀繀椤诲寘鍚椂闂淬€佹搷浣滆€呫€佸姩浣溿€佽祫婧愩€佺洰鏍囥€佺粨鏋滃拰璇存槑銆?- 瀹¤鏃ュ織鍐欏叆澶辫触涓嶅緱闃绘柇涓讳笟鍔℃搷浣滐紝浣嗗垹闄ゃ€佹仮澶嶃€佸鍏ャ€佸鍑恒€佷笂浼犮€乻ettings 淇敼鍜屽唴瀹瑰啓鍏ョ瓑楂橀闄╁姩浣滃簲灏介噺璁板綍銆?- 瀹¤鏃ュ織 `detail` 蹇呴』娓呮礂 `secret`銆乣password`銆乣token`銆乣key`銆乣authorization` 绛夊瓧娈碉紝涓嶅緱璁板綍 Secret 鏄庢枃銆?- 鎵€鏈夋墜鍔ㄥ浠姐€佷笅杞藉浠姐€佹仮澶嶅浠姐€佸鍏ュ拰瀵煎嚭鎺ュ彛蹇呴』瑕佹眰绠＄悊鍛?JWT銆?- 鎵嬪姩澶囦唤鍙兘鍐欏叆 `backend/data/.manual_backups/{timestamp}.zip`锛屾枃浠跺悕蹇呴』浣跨敤鏃堕棿鎴抽伩鍏嶈鐩栥€?- 澶囦唤涓嶅緱鍖呭惈 `.env`銆乣.venv`銆乣node_modules`銆乣dist`銆佸墠绔簮鐮佹垨 `.manual_backups` 鏈韩銆?- 澶囦唤涓殑 `settings.json` 蹇呴』鍓旈櫎 Secret 瀛楁鍚庡啀鍐欏叆 zip锛涚敓浜?Secret 搴斾繚瀛樺湪鍚庣 `.env` 鎴栨湇鍔＄閰嶇疆銆?- 涓嬭浇鍜屾仮澶嶅浠芥椂蹇呴』鏍￠獙 zip 鏂囦欢鍚嶏紝绂佹 `..`銆乣/`銆乣\` 鍜岄潪 `.zip` 鍚嶇О銆?- 鎭㈠鍜屽鍏?zip 鏃跺繀椤绘鏌?zip 鍐呮瘡涓矾寰勶紝绂佹缁濆璺緞銆乣..`銆佷笉鍦ㄥ厑璁稿浠借寖鍥村唴鐨勮矾寰勫拰鎺掗櫎鐩綍銆?- 鎭㈠鎴栧鍏ュ墠蹇呴』鑷姩鍒涘缓鎭㈠鍓嶅浠斤紝閬垮厤璇搷浣滄棤娉曞洖婊氥€?- 鍚庡彴鎭㈠椤甸潰蹇呴』鏄剧ず鏄庣‘椋庨櫓鎻愮ず锛氭仮澶嶄細瑕嗙洊褰撳墠 `backend/data` 鍐呭锛岀郴缁熶細鍏堝垱寤烘仮澶嶅墠澶囦唤銆?
## 鐢熶骇閮ㄧ讲瀹夊叏

- 鐢熶骇閰嶇疆搴斾粠 `backend/.env.production.example` 澶嶅埗鍒版湇鍔＄鐜鏂囦欢锛屼緥濡?`/etc/srblogs/backend.env`锛屼笉寰楁彁浜ょ湡瀹?Secret銆?- 鐢熶骇蹇呴』淇敼 `ADMIN_PASSWORD` 鍜?`JWT_SECRET`锛屼笉寰椾娇鐢ㄦ湰鍦板紑鍙戦粯璁ゅ€笺€?- `CORS_ORIGINS` 鐢熶骇鐜涓嶅緱浣跨敤 `*`锛屽彧鑳藉寘鍚彲淇″墠鍙板拰鍚庡彴鍩熷悕銆?- `PUBLIC_BASE_URL` 鍙兘閰嶇疆鍏紑绔欑偣 origin锛岀敤浜?RSS銆丼itemap銆乺obots銆丱penGraph 鍜屼笂浼?URL锛涗笉寰楅厤缃悗鍙扮鐞嗗湴鍧€銆?- Nginx 涓嶅緱鐩存帴鏆撮湶 `.env`銆乣.manual_backups`銆乣audit`銆佸墠绔簮鐮併€乣node_modules` 鎴栨瀯寤哄唴閮ㄧ洰褰曘€?- `GET /api/admin/system/status` 蹇呴』瑕佹眰绠＄悊鍛?JWT锛屽彧鑳借繑鍥炵洰褰曞瓨鍦ㄦ€у拰璇诲啓鐘舵€侊紝涓嶅緱杩斿洖鐜鍙橀噺鍐呭鎴?Secret銆?- systemd 鏃ュ織閫氳繃 `journalctl` 鏌ョ湅锛汵ginx access/error log 搴斾繚瀛樺湪绯荤粺鏃ュ織鐩綍锛屾帓鏌ユ椂涓嶅緱绮樿创 Secret銆?
## Pending Queue Scope

鐘舵€佹満鍥哄畾涓猴細

- `editing`锛氭鍦ㄧ紪杈戯紝灏氭湭杩涘叆鏆傚瓨闃熷垪銆?- `pending`锛氬凡鍔犲叆鏆傚瓨闃熷垪锛岀瓑寰呭簲鐢ㄣ€?- `applied`锛氬凡鎴愬姛鍐欏叆鍚庣鏁版嵁銆?- `failed`锛氬簲鐢ㄥけ璐ワ紝淇濈暀閿欒淇℃伅锛屽厑璁搁噸璇曟垨绉婚櫎銆?
绗竴闃舵鏈湴 `pendingOperations` 鍙鐩栵細

- settings 淇敼
- 鏂囩珷鏂板缓
- 鏂囩珷缂栬緫
- 鏂囩珷鍒犻櫎
- 鑽夌鍙戝竷

鍥剧墖涓婁紶銆丼ecret 淇敼銆佽瘎璁虹鐞嗘殏涓嶈繘鍏ユ湰鍦?`pendingOperations`銆傜涓€闃舵闃熷垪鍦ㄥ埛鏂伴〉闈㈠悗浼氫涪澶憋紱绗簩闃舵鍐嶅仛鏈嶅姟绔寔涔呭寲銆?# 2026-05-03 瀹夊叏琛ュ厖锛欸itHub 璇勮涓庡墠鍙板叆鍙?
- GitHub OAuth 鐧诲綍鍏ュ彛鍙兘鏀惧湪鍓嶅彴鏂囩珷璇︽儏璇勮鍖猴紱鍚庡彴璁剧疆椤靛彧璐熻矗閰嶇疆 Client ID 鍜?Secret configured 鐘舵€侊紝涓嶆壙鎷呰瀹㈢櫥褰曘€?- 鏈櫥褰曠敤鎴锋彁浜よ瘎璁哄繀椤昏繑鍥?`401`锛屼笉鑳藉洖閫€鍒板尶鍚嶈瘎璁恒€侀偖绠辫瘎璁烘垨鍓嶇浼€犱綔鑰呫€?- 鍓嶅彴鍙兘璇诲彇 `/api/auth/github/me` 鐨?configured 鐘舵€佸拰 GitHub 鍏紑鐢ㄦ埛淇℃伅锛汷Auth Secret銆乤ccess token銆佺鐞嗗憳 JWT 涓嶅緱杩涘叆鍓嶇鏋勫缓浜х墿銆?- 鐣欒█鏉垮彧鏄墠鍙板睍绀哄悕绉帮紝鍚庣浠嶄娇鐢ㄦ棦鏈?comments 瀛樺偍锛涗笉寰椾负浜嗘枃妗堝彉鍖栨柊澧炲尶鍚嶆彁浜ゆ梺璺€?- 闊充箰椤靛拰棣栭〉鍏变韩鍏ㄥ眬鎾斁鐘舵€佷笉搴斾繚瀛樹换浣?Secret锛涙瓕璇嶆枃浠朵笂浼犱粛鎸夋枃鏈被瀹夊叏闄愬埗澶勭悊銆?
## 2026-05-03 GitHub 鐣欒█涓庡墠鍙版枃妗堣竟鐣?
- 鍓嶅彴鏈厤缃?GitHub 鐣欒█鏃讹紝鍙兘鎻愮ず璁垮鈥滅珯鐐规殏鏈紑鍚?GitHub 鐣欒█锛岃绋嶅悗鍐嶈瘯鎴栬仈绯荤珯鐐圭鐞嗗憳銆傗€?- 鍓嶅彴涓嶅緱鍑虹幇 `Secret`銆乣Client Secret`銆乣.env`銆佸悗绔厤缃矾寰勭瓑寮€鍙戣€呮枃妗堛€?- GitHub OAuth Client Secret 浠嶅彧鑳戒繚瀛樺湪鍚庣 `.env` 鎴栨湇鍔＄閰嶇疆涓紝鏋勫缓浜х墿涓嶅緱鍖呭惈璇ュ€笺€?- `GET /api/auth/github/login` 浣跨敤 `returnTo` 浣滀负鍓嶅彴鍥炶烦鍙傛暟锛涘悗绔繀椤婚檺鍒剁粷瀵?URL 鍥炶烦鏉ユ簮锛岄伩鍏嶅紑鏀鹃噸瀹氬悜銆?- 鏈櫥褰曠洿鎺ヨ皟鐢?`POST /api/comments/{resource}/{slug}` 蹇呴』杩斿洖 401锛屼笉鑳戒繚鐣欏尶鍚嶆彁浜ゆ梺璺€?- `/api/settings/public` 鍙兘鍏紑 `comments.githubLoginConfigured` 杩欑被甯冨皵鍊硷紱GitHub OAuth Secret銆乤ccess token銆乣.env` 璺緞鍜屾湇鍔＄閰嶇疆缁嗚妭涓嶅緱杩涘叆鍓嶅彴鍝嶅簲銆?- 鎾斁鍣ㄩ煶閲忚缃粎淇濆瓨鍦ㄦ祻瑙堝櫒 localStorage锛屼笉灞炰簬鏁忔劅閰嶇疆銆?

## 2026-05-03 Visitor OAuth Security Notes

- GitHub OAuth Client Secret and QQ OAuth App Secret must stay in backend `.env` or server-side settings only.
- Frontend and admin builds may only receive configured booleans such as `githubLoginConfigured` and `qqLoginConfigured`.
- OAuth access tokens are never returned to frontend code.
- GitHub and QQ login flows must validate CSRF `state` before creating the visitor session cookie.
- `POST /api/comments/{resource}/{slug}` must reject anonymous requests with `401`; anonymous local message submission must not be restored.
- Visitor-facing unavailable-provider text must not mention `.env`, Secret, Client Secret, backend configuration, or internal deployment details.

## 2026-05-04 Component Theme And Music Likes Security

- `themeConfig.componentTheme` is public presentation data only. It may include colors, opacity, size, labels, borders, and accent values, but must not include OAuth secrets, AI keys, OSS secrets, admin JWTs, access tokens, server paths, or executable HTML/JS.
- Component opacity is allowed to be `0..1`; `0` may visually hide a component but must not remove authorization checks or backend validation.
- Component size settings are presentation hints only. They must not change API permissions, write paths, or upload validation.
- Music likes are public visitor interactions. The first stage uses browser `localStorage` to avoid duplicate likes from the same browser; this is not a strong identity guarantee.
- Music likes writes must keep counts nonnegative and use the existing safe JSON write/backup path for `music.json`.
- The music likes endpoint must not return private visitor identifiers or authentication tokens.
## 2026-05-03 Interaction And Page Layout Security

- `/api/settings/public` 可以公开 `interaction.clickEffectEnabled`，但只能作为布尔站点开关，不得携带 Secret、管理员配置或调试信息。
- 点击音效 URL 属于公开前台资源地址；如果使用上传资源，仍必须经过上传类型、MIME 和大小限制。
- 页面编辑第一阶段保存的 `pageLayouts` 只能保存页面标题、副标题、说明和预览布局坐标，不得保存脚本、HTML 片段、Secret 或服务端路径。
- 页面编辑公开配置 `pageText` / `pageLayouts` 会进入 `/api/settings/public`，只能包含前台可展示的文字、公开链接和布局坐标；不得写入管理员 Token、OAuth Secret、服务器绝对路径、HTML 脚本或任意可执行代码。
- “页面编辑 > 首页”保存的作者、头像、简介和社交链接属于公开资料卡内容，任何私人联系方式应由站点管理员自行判断是否适合公开展示。
- 页面布局配置通过后台 settings 写入，仍需管理员 JWT；前台游客只能读取公开效果，不能写入布局配置。
- 鼠标点击视觉特效只在前端渲染临时节点，不应记录用户点击内容，也不应向后端发送点击轨迹。
## 2026-05-05 Theme Package Security

- Theme packages are presentation data only. They may include colors, opacity, font names, radius, blur, component style tokens, and optional public page layout data.
- Theme packages must not include GitHub OAuth Secret, QQ App Secret, AI API Key, OSS AccessKey Secret, admin JWT, password, access token, server absolute path, executable HTML, or JavaScript.
- `GET /api/settings/public` may expose active theme id, public theme packages, component theme tokens, and opacity values only.
- Admin theme import must validate that the uploaded JSON has a usable `modes.day` and `modes.night` structure before applying it.
- Theme import must not overwrite backend secret settings. Empty secret preservation rules remain unchanged.
- If an imported theme contains `pageLayouts`, the admin UI must give the operator a choice before applying layouts.
- Component opacity may be `0..1`. Opacity `0` can visually hide a component, but it must not bypass authorization, upload checks, comment login rules, or backend validation.
## About Contact Form SMTP Secrets

- `/api/contact/send` sends mail only from the backend. Frontend code never receives SMTP host credentials, usernames, passwords, authorization codes, or provider internals.
- Configure SMTP only through server-side environment variables: `CONTACT_MAIL_ENABLED`, `CONTACT_MAIL_TO`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_SSL`, and `SMTP_FROM`.
- `SMTP_PASSWORD` must not be a personal login password when the provider requires an app authorization code. QQ Mail usually requires an SMTP authorization code.
- Contact form errors returned to visitors must be user-readable and must not expose SMTP usernames, passwords, server paths, stack traces, or provider debug output.
- About page structured content is public presentation data. It may contain public email, QQ, WeChat, GitHub, website links, page text, and local GitHub-style statistics, but must not contain private tokens or credentials.
## 2026-05-10 Code Review Security Fixes

- About page highlight words are rendered as text segments, not `v-html`; editable About content must not be treated as trusted HTML.
- Contact-form SMTP delivery remains server-side only and now runs in a threadpool so mail network I/O does not block the FastAPI event loop.
- Contact-form audit records must avoid visitor message content and full personal identifiers; current logs store name length and masked email only.
- `/api/settings/public` may expose `defaultPostCover` as a public image URL, but must not expose secret keys, OAuth secrets, SMTP credentials, access tokens, or admin credentials.
- Album batch upload validation must reject over-capacity selections instead of silently truncating user-selected files.

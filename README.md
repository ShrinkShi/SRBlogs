# SRBlogs

![Vue](https://img.shields.io/badge/Vue-3.5-42b883)
![Vite](https://img.shields.io/badge/Vite-TypeScript-646cff)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38bdf8)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776ab)
![Nginx](https://img.shields.io/badge/Nginx-reverse_proxy-009639)

SRBlogs 是一个基于 Vue 3 + FastAPI 的个人博客系统，包含访客前台、后台管理端和文件型内容后端。

## 在线体验 / 项目状态

- 在线演示：暂无在线演示。
- 当前版本：`v1.2.0`。
- 当前状态：可本地运行；Linux 服务器支持一键安装、一键更新和一键诊断；真实域名、HTTPS 与第三方服务仍需按环境验收。
- 默认本地地址：前台 `http://127.0.0.1:5173`，后台 `http://127.0.0.1:5174/admin/`，后端 `http://127.0.0.1:8000`。

## 截图

README 当前未内置截图，避免继续展示旧版后台 UI。建议发布前补充以下截图：

- 前台首页：展示当前主题、内容卡片和运行时间。
- 后台文章编辑：展示 v1.2.0 双栏编辑器、Markdown 工具栏和预览。
- 后台内容管理：展示文章、图片、音乐的嵌入式评论管理入口。
- Linux 安装向导：展示 `/install` 首次初始化流程。

## 项目概述

SRBlogs 面向个人站长、内容创作者和需要轻量自托管博客的开发者。它用 Markdown 与 JSON 文件保存内容，避免引入独立数据库，适合小型个人站、作品集、日志站和带后台维护能力的静态风格博客。

项目解决的核心问题是：用一套可本地开发、可服务器部署的工程，统一管理文章、杂谈、图片、音乐、友链、项目、关于页、留言评论、主题配置和基础运维。

## 核心功能

- 文章管理：支持正经文章、杂谈和动态内容的 Markdown 读写、草稿、发布、撤回、删除和搜索。
- Markdown 编辑器：后台文章页采用双栏编辑布局，内置 Markdown 工具栏、编辑/预览切换、图片插入和全屏 Markdown 编辑器。
- 评论系统：文章、图片、音乐条目内嵌评论管理，可查看评论内容、用户信息、回复关系并在后台删除。
- 媒体管理：支持图片相册、音乐列表、封面、歌词、音频文件和后台鉴权上传，通过 `/uploads` 访问。
- 结构化内容：支持项目展示、友情链接、关于页面、站点信息和社交链接等 JSON/结构化数据维护。
- 设置中心：支持站点信息、作者信息、主题外观、评论/OAuth 状态、联系表单和安全相关配置。
- 前台能力：提供首页、文章、杂谈、图片、音乐、项目、友链、关于、搜索、标签、归档和评论交互。
- SEO 输出：提供 RSS、Sitemap、Robots、OpenGraph/Twitter Card 等公开输出。
- 操作反馈：后台使用项目内 Toast 和确认弹窗，不再依赖浏览器原生 `alert` / `confirm`。
- 运维能力：提供审计日志 API、备份/导入导出接口、生产环境模板、Nginx/systemd 示例和健康检查脚本。
- 版本更新：后台读取本地版本常量并检测 GitHub Releases，提供错误分类和调试日志；Linux 服务器可由后端触发 `deploy/update.sh` 安全更新，Windows 本地开发环境仅支持检测并明确显示不支持一键更新。

## 后台管理体验

v1.2.0 的后台主流程围绕内容维护收敛：

- 左侧导航只保留“内容”和“设置”，评论不再是独立入口，而是嵌入文章、图片、音乐条目。
- 文章新增/编辑页为左侧正文、右侧元信息的双栏布局，Slug 收进高级设置。
- Markdown 正文区域支持中文“编写 / 预览”切换、快捷工具栏、`.md` 导入、图片插入和全屏编辑器。
- 全屏 Markdown 编辑器支持 `Ctrl+S` / `Cmd+S` 快捷保存，未修改关闭不弹确认，保存反馈走 Toast。
- 设置页、关于页和内容页移除旧版大 Hero 区块，保存类按钮统一使用绿色并下沉到操作区。
- 版本弹窗显示当前版本、最新 Release、发布时间、更新摘要、检测状态和调试日志。

## 技术栈

| 组件 | 技术 |
|---|---|
| 前台 | Vue 3、Vite、TypeScript、Vue Router、Pinia、Tailwind CSS |
| 管理端 | Vue 3、Vite、TypeScript、CodeMirror、Axios、Tailwind CSS |
| 后端 | FastAPI、Uvicorn、Pydantic、python-jose、passlib |
| 数据存储 | `backend/data` 中的 Markdown、JSON、评论文件、上传文件和审计日志 |
| 内容渲染 | marked、DOMPurify、highlight.js |
| 编辑器 | CodeMirror、Markdown 工具栏、DOMPurify 预览净化 |
| 构建工具 | npm、vue-tsc、Vite、ESLint、Prettier |
| 部署 | Nginx、systemd、Shell 脚本、Windows CMD 启动脚本 |

## 快速开始

### 环境要求

- Windows 10/11 或 Linux
- Node.js 与 npm
- Python 3.11+
- PowerShell / CMD；Linux 部署需要 bash、nginx、systemd

### 克隆项目

```powershell
git clone <your-repo-url> SRBlogs
cd SRBlogs
```

### 后端启动

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Linux/macOS 可将虚拟环境命令替换为：

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

也可以在仓库根目录安装后端依赖：

```powershell
python -m pip install -r requirements.txt
```

本项目不需要初始化数据库；内容数据来自 `backend/data`。

### 前端启动

```powershell
cd frontend
npm install
npm run dev
```

### 管理端启动

```powershell
cd admin
npm install
npm run dev
```

### 访问地址

- 前台：`http://127.0.0.1:5173`
- 后台：`http://127.0.0.1:5174/admin/`
- 后端 Swagger：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/api/health`
- 管理员账号：首次部署通过 `/install` 创建；忘记密码可用 `backend/scripts/reset_admin.py` 重置。

## 一键启动脚本

Windows 推荐从仓库根目录运行：

```powershell
.\start-all.cmd
```

该脚本会分别启动：

- `start-backend.cmd`：检查 8000 端口，创建后端虚拟环境并安装依赖。
- `start-frontend.cmd`：检查 5173 端口，安装前台依赖并运行 Vite。
- `start-admin.cmd`：检查 5174 端口，安装管理端依赖并运行 Vite。

单独启动：

```powershell
.\start-backend.cmd
.\start-frontend.cmd
.\start-admin.cmd
```

如需释放本地后端端口，可使用：

```powershell
.\kill-8000.bat
```

## 配置说明

后端读取 `backend/.env` 或生产环境文件 `/etc/srblogs/backend.env`。前台与后台开发环境读取各自的 `.env.development`。

| 配置项 | 默认值 | 是否必填 | 说明 |
|---|---:|---|---|
| `APP_NAME` | `SRBlogs API` | 否 | FastAPI 应用名称 |
| `APP_ENV` | `development` | 否 | 运行环境标识 |
| `DATA_DIR` | `backend/data` | 是 | Markdown、JSON、上传、备份和日志目录 |
| `PUBLIC_BASE_URL` | `http://127.0.0.1:8000` | 生产必填 | RSS、Sitemap、Robots、OpenGraph 和上传 URL 的公开地址 |
| `SITE_START_TIME` | 空 | 否 | 站点运行时间起点；首次安装向导未填写时由后端自动生成 |
| `ADMIN_USERNAME` | `admin` | 安装后必填 | 后台管理员用户名；推荐由 `/install` 或 `reset_admin.py` 写入 |
| `ADMIN_PASSWORD_HASH` | 空 | 安装后必填 | 后台管理员密码哈希；新安装和重置脚本写入该字段 |
| `ADMIN_PASSWORD` | 空 | 否 | 旧部署兼容字段，不建议继续使用；`doctor.sh` 会提示 WARN |
| `JWT_SECRET` | `please-change-this-secret` | 生产必填 | JWT 签名密钥；安装向导自动生成，手动配置必须改为长随机值 |
| `JWT_EXPIRE_MINUTES` | `1440` | 否 | 管理端登录有效期 |
| `CORS_ORIGINS` | 本地前后台地址 | 是 | 允许访问 API 的前端来源，生产不要使用 `*` |
| `UPLOAD_DRIVER` | `local` | 否 | 当前实现为本地上传 |
| `UPLOAD_MAX_SIZE` | `5242880` | 否 | 上传大小上限，需与 Nginx `client_max_body_size` 协调 |
| `UPLOAD_ALLOWED_TYPES` | 图片/音视频 MIME 列表 | 否 | 上传 MIME 白名单 |
| `GITHUB_OAUTH_CLIENT_ID` / `GITHUB_OAUTH_CLIENT_SECRET` | 空 | 否 | GitHub 访客登录配置 |
| `QQ_OAUTH_APP_ID` / `QQ_OAUTH_APP_SECRET` | 空 | 否 | QQ 访客登录配置 |
| `OSS_*` | 空 | 否 | OSS 占位配置，Secret 只能保存在服务端 |
| `AI_A_*` / `AI_B_*` | 空 | 否 | AI 服务占位配置，Key 不进入前端构建 |
| `CONTACT_MAIL_ENABLED` | `false` | 否 | 联系表单 SMTP 开关 |
| `SMTP_*` | 空 | 否 | 联系表单邮件发送配置 |
| `SRBLOGS_UPDATE_REPO` | `ShrinkShi/SRBlogs` | 否 | GitHub Release 检测仓库 |
| `SRBLOGS_UPDATE_ENABLED` | `true` | 否 | 是否允许 Linux 服务器端一键更新；Windows 本地只检测版本 |
| `SRBLOGS_UPDATE_COMMAND` | 空 | 否 | 历史兼容字段；当前更新流程优先使用 `deploy/update.sh` |
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000/api` | 开发建议 | 前台/管理端 API 地址 |

生产配置可从 `backend/.env.production.example` 复制，不要提交真实密钥。

忘记后台密码时，在服务器上运行：

```bash
cd /opt/srblogs/backend
sudo .venv/bin/python scripts/reset_admin.py --username admin --env-file /etc/srblogs/backend.env
sudo systemctl restart srblogs-backend
```

## 部署方式

### 方式一：本地开发

前置条件：本机安装 Node.js、npm、Python 3.11+。

操作步骤：

```powershell
.\start-all.cmd
```

查看日志：三个启动窗口分别输出后端、前台和管理端日志。访问地址见“访问地址”章节。

### 方式二：Linux 一键部署

主要支持 Alibaba Cloud Linux / CentOS / RHEL 系服务器，使用 `dnf` 或 `yum`。推荐通过本地上传 zip 包部署，避免服务器直接 `git clone GitHub` 不稳定。

zip 包可以直接包含 `admin/ backend/ frontend/`，也可以多一层目录，例如 `SRBlogs-main/admin`。

#### 全新安装

先预览将执行的系统修改：

```bash
sudo bash deploy/install.sh --dry-run --zip /opt/SRBlogs-main.zip
```

执行安装：

```bash
sudo bash deploy/install.sh --zip /opt/SRBlogs-main.zip
```

可选参数：

```bash
sudo bash deploy/install.sh --source /tmp/SRBlogs-main
sudo bash deploy/install.sh --app-dir /opt/srblogs --domain example.com
sudo bash deploy/install.sh --zip /opt/SRBlogs-main.zip --compile-python
sudo bash deploy/install.sh --force-nginx-main
```

脚本完成后访问：

```text
http://服务器IP/install
```

安装向导会写入 `/etc/srblogs/backend.env`、初始化 `backend/data/settings.json`、创建 `backend/data/.install.lock`，并由后端生成 `JWT_SECRET`。完成后建议重启：

```bash
sudo systemctl restart srblogs-backend
sudo bash /opt/srblogs/deploy/doctor.sh
```

`deploy/setup.sh` 仍保留为兼容入口，内部转调 `deploy/install.sh`。

#### 一键更新

```bash
sudo bash /opt/srblogs/deploy/update.sh --dry-run --zip /opt/SRBlogs-main.zip
sudo bash /opt/srblogs/deploy/update.sh --zip /opt/SRBlogs-main.zip
sudo bash /opt/srblogs/deploy/doctor.sh
```

`update.sh` 会先备份当前 `/opt/srblogs`、`/etc/srblogs/backend.env`、Nginx 配置和 systemd unit 到 `/opt/srblogs.backup.TIMESTAMP/`，再在 staging 中安装依赖和构建。依赖安装、构建、`nginx -t`、systemd restart 或 API healthcheck 失败都会触发回滚；回滚后还会检查旧版本 `/api/health`。

默认只清理旧的 `/opt/srblogs.backup.*`，保留最近 3 个。`/opt/srblogs.previous.*` 和 `/opt/srblogs.failed.*` 只有传入 `--cleanup` 才会清理。

#### 一键诊断

```bash
sudo bash /opt/srblogs/deploy/doctor.sh
```

诊断项包括 Python 3.11、Node/npm、nginx、systemd、8000 端口、安装状态接口、公开设置接口、目录权限、构建产物、默认 Nginx 冲突、swap 和默认弱密钥。存在 FAIL 时退出码为 `1`；只有 WARN 或全 PASS 时退出码为 `0`。

#### 保守安全策略

- 默认不源码编译 Python；只有 `--compile-python` 才允许 `make altinstall`。
- 默认不覆盖 `/etc/nginx/nginx.conf`；只有 `--force-nginx-main` 才允许备份后重写。
- 只会把明确默认站点 `default.conf`、`welcome.conf` 改名为 `.disabled.TIMESTAMP`，不会删除未知 Nginx 配置。
- 无 swap 且根分区可用空间大于 4G 时才尝试创建 `/swapfile-srblogs`；失败只警告不中断。
- 日志会隐藏 `ADMIN_PASSWORD`、`JWT_SECRET`、OAuth Secret、Token 和 API Key。
- 安装期允许 `srblogs` 写 `/etc/srblogs/backend.env`；安装完成后建议收紧为 `root:srblogs 640` 或 `root:root 600`。

#### 手动流程：逐步部署

```bash
sudo mkdir -p /opt/srblogs /etc/srblogs
sudo rsync -a --delete ./ /opt/srblogs/
sudo cp /opt/srblogs/backend/.env.production.example /etc/srblogs/backend.env
sudo editor /etc/srblogs/backend.env

cd /opt/srblogs/backend
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r /opt/srblogs/requirements.txt
mkdir -p data/uploads data/audit data/.manual_backups

cd /opt/srblogs
bash deploy/build-all.sh
sudo cp deploy/srblogs-backend.service /etc/systemd/system/srblogs-backend.service
sudo systemctl daemon-reload
sudo systemctl enable --now srblogs-backend
```

后端服务允许 `/etc/srblogs/backend.env` 缺失时启动进入未安装状态；未安装时仅开放 `/install`、`/api/install/status`、`POST /api/install` 和 `/api/health`。

#### 后台一键更新入口

后台左侧底部版本入口会请求：

- `GET /api/admin/update/status`：读取 `backend/app/version.py` 当前版本，检测 GitHub Latest Release，并返回 `errorCode`、`errorMessage`、`platform` 和 `debugLogs`。
- `POST /api/admin/update/run`：仅管理员可调用。Linux 服务器会下载 Release zip 并调用 `deploy/update.sh`；Windows 本地开发环境直接返回 `unsupported_platform`，不会尝试执行 shell 更新。

如果 GitHub 没有创建 Release，弹窗会显示“未找到 GitHub Release”；如果网络不可达、超时或 API 限流，会显示对应错误并可展开“查看日志”。

确认服务状态和日志：

```bash
systemctl status srblogs-backend --no-pager
sudo journalctl -u srblogs-backend -n 100 --no-pager
```

数据目录默认位于 `/opt/srblogs/backend/data`。生产环境应确保运行用户可读写：

```bash
sudo chown -R srblogs:srblogs /opt/srblogs/backend/data
```

部署后可以运行健康检查：

```bash
PUBLIC_BASE_URL=https://example.com API_BASE_URL=http://127.0.0.1:8000 bash deploy/healthcheck.sh
```

### 方式三：Nginx 反向代理

参考配置：`deploy/nginx.srblogs.conf` 或 `deploy/nginx/srblogs.conf`。

安装配置：

```bash
sudo cp /opt/srblogs/deploy/nginx.srblogs.conf /etc/nginx/conf.d/srblogs.conf
sudo nginx -t
sudo systemctl reload nginx
```

示例配置会：

- 从 `/opt/srblogs/frontend/dist` 提供前台静态文件。
- 从 `/opt/srblogs/admin/dist` 提供 `/admin/` 管理端。
- 将 `/api/`、`/uploads/` 和 `/robots.txt` 代理到 `127.0.0.1:8000`。
- 为 Vue history mode 配置 `try_files` 回退。
- 设置 `client_max_body_size 5m`。

上线前请将配置中的 `server_name example.com` 替换为真实域名，并接入 HTTPS。Nginx 日志通常位于 `/var/log/nginx/access.log` 和 `/var/log/nginx/error.log`，后端日志使用 `sudo journalctl -u srblogs-backend -n 100 --no-pager` 查看。

当前仓库未提供 Dockerfile 或 Docker Compose，不把 Docker 作为推荐部署方式。

## 常用命令

| 场景 | 命令 |
|---|---|
| 启动后端 | `cd backend; .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000` |
| 启动前台 | `cd frontend; npm run dev` |
| 启动管理端 | `cd admin; npm run dev` |
| 构建前台 | `cd frontend; npm run build` |
| 构建管理端 | `cd admin; npm run build` |
| 代码检查/修复 | `cd frontend; npm run lint` 或 `cd admin; npm run lint` |
| 格式化 | `cd frontend; npm run format` 或 `cd admin; npm run format` |
| 后端语法检查 | `python -m compileall backend/app` |
| 安装后端依赖 | `python -m pip install -r requirements.txt` |
| 重置管理员密码 | `cd backend; python scripts/reset_admin.py --username admin --env-file /etc/srblogs/backend.env` |
| 重置安装状态 | `cd backend; python scripts/reset_install.py` |
| 生产构建 | `bash deploy/build-all.sh` |
| Linux 一键安装预览 | `sudo bash deploy/install.sh --dry-run --zip /opt/SRBlogs-main.zip` |
| Linux 一键安装 | `sudo bash deploy/install.sh --zip /opt/SRBlogs-main.zip` |
| Linux 一键更新预览 | `sudo bash /opt/srblogs/deploy/update.sh --dry-run --zip /opt/SRBlogs-main.zip` |
| Linux 一键更新 | `sudo bash /opt/srblogs/deploy/update.sh --zip /opt/SRBlogs-main.zip` |
| Linux 部署诊断 | `sudo bash /opt/srblogs/deploy/doctor.sh` |
| 部署脚本语法检查 | `bash -n deploy/install.sh deploy/update.sh deploy/doctor.sh` |
| 健康检查 | `PUBLIC_BASE_URL=https://example.com API_BASE_URL=http://127.0.0.1:8000 bash deploy/healthcheck.sh` |
| 查看 systemd 服务 | `systemctl status srblogs-backend --no-pager` |
| 查看 systemd 日志 | `sudo journalctl -u srblogs-backend -n 100 --no-pager` |
| 停止本地开发服务 | 在对应终端按 `Ctrl+C` |
| 释放 8000 端口 | `.\kill-8000.bat` |

仓库当前没有独立测试命令和数据库迁移命令。

## 项目结构

```text
SRBlogs/
├── frontend/                 # 访客前台 Vue SPA
│   ├── src/views/            # 前台页面
│   ├── src/components/       # 前台组件
│   ├── src/api/              # 前台 API 客户端
│   └── package.json          # 前台脚本与依赖
├── admin/                    # 后台管理 Vue SPA
│   ├── src/views/            # 后台页面
│   ├── src/components/       # 后台组件
│   ├── src/api/              # 后台 API 客户端
│   └── package.json          # 后台脚本与依赖
├── backend/                  # FastAPI 后端
│   ├── app/api/              # API 路由
│   ├── app/services/         # 内容、上传、备份、审计等服务
│   ├── app/models/           # Pydantic 模型
│   ├── app/version.py        # v1.2.0 统一版本与 GitHub 仓库常量
│   ├── scripts/              # 管理员密码与安装状态维护工具
│   ├── data/                 # Markdown、JSON、评论、上传和日志数据
│   └── requirements.txt      # 后端依赖
├── docs/                     # API、部署、安全、QA、发布文档
├── deploy/                   # Linux 一键部署/更新/诊断、Nginx、systemd、健康检查脚本
├── requirements.txt          # 根目录 Python 依赖入口，转发到 backend/requirements.txt
├── start-all.cmd             # Windows 一键启动
├── start-backend.cmd         # Windows 后端启动
├── start-frontend.cmd        # Windows 前台启动
├── start-admin.cmd           # Windows 后台启动
├── WINDOWS_START.md          # Windows 启动说明
├── HISTORY.md                # 历史开发记录
└── CHANGELOG.md              # 发布变更摘要
```

## 接口文档

启动后端后访问：

- Swagger UI：`http://127.0.0.1:8000/docs`
- OpenAPI JSON：`http://127.0.0.1:8000/openapi.json`
- 健康检查：`GET http://127.0.0.1:8000/api/health`
- RSS：`GET http://127.0.0.1:8000/api/rss.xml`
- Sitemap：`GET http://127.0.0.1:8000/api/sitemap.xml`
- Robots：`GET http://127.0.0.1:8000/robots.txt`
- 安装状态：`GET http://127.0.0.1:8000/api/install/status`
- 版本检测：`GET http://127.0.0.1:8000/api/admin/update/status`

## 相关文档

- [Windows 启动说明](WINDOWS_START.md)
- [API 契约](docs/API_CONTRACT.md)
- [用户指南](docs/USER_GUIDE.md)
- [部署指南](docs/DEPLOYMENT.md)
- [生产检查清单](docs/PRODUCTION_CHECKLIST.md)
- [发布检查清单](docs/RELEASE_CHECKLIST.md)
- [手动 QA 清单](docs/MANUAL_QA_CHECKLIST.md)
- [安全说明](docs/SECURITY_NOTES.md)
- [UI 风格指南](docs/UI_STYLE_GUIDE.md)
- [历史记录](HISTORY.md)
- [发布变更](CHANGELOG.md)

## 部署注意事项

- 前台开发环境可使用 `VITE_API_BASE_URL=http://127.0.0.1:8000/api`；生产环境推荐通过同域 `/api` 反向代理。
- 管理端使用 `/admin/` history base，Nginx 必须将 `/admin/` 回退到 `/admin/index.html`。
- 前台 history mode 需要将未知路径回退到 `/index.html`。
- 后端生产建议监听内网地址，由 Nginx 对外暴露；如果跨主机部署，需要调整 `HOST`、`PORT` 和 `CORS_ORIGINS`。
- `backend/data/uploads`、`backend/data/audit`、`backend/data/.manual_backups` 需要后端服务用户可读写。
- Nginx 的 `client_max_body_size` 应与 `UPLOAD_MAX_SIZE` 保持一致或更大。
- 不要直接暴露 `.env`、`.manual_backups`、`audit`、源代码目录、`node_modules` 或构建内部文件。
- 首次部署后访问 `/install` 完成初始化；安装完成会创建 `backend/data/.install.lock`，重复访问安装 API 会被拒绝。
- 生产推荐先上传 zip，再执行 `deploy/install.sh --zip`；更新时使用 `deploy/update.sh --zip`，不要直接覆盖 `/opt/srblogs`。
- 如更新失败且出现 `rollback attempted but healthcheck failed`，优先查看 `/var/log/srblogs/update.TIMESTAMP.log` 和 `sudo journalctl -u srblogs-backend -n 100 --no-pager`。

## 安全说明

- 生产环境必须通过 `/install` 或 `/etc/srblogs/backend.env` 设置管理员账号；`JWT_SECRET` 由安装向导自动生成，手动配置时必须改为长随机值。
- 管理员账号密码、JWT、OAuth Secret、SMTP 密码、AI Key、OSS Key 不得提交到 Git。
- 上传接口需要管理员 JWT；后端会校验文件类型和大小。
- 公开设置接口只应返回非敏感状态，例如 provider 是否已配置，不返回 Secret 明文。
- 留言、登录、上传、备份、恢复、系统状态和更新触发等能力都应通过后端鉴权边界访问。
- 一键更新由后端在 Linux 服务器上调用 `deploy/update.sh`；Windows 本地开发环境会显示不支持，不会伪造更新成功。

## 已知问题

- README 暂未包含 v1.2.0 截图，发布 GitHub Release 前建议补充前台、后台编辑器、评论弹窗和安装向导截图。
- 真实服务器、域名和 HTTPS 部署实操仍需按目标环境执行验收。
- GitHub/QQ OAuth、SMTP、OSS、AI Provider 需要配置真实服务后再进行联调。
- 仓库当前没有自动化单元测试套件，主要依赖构建、后端语法检查、健康检查和手动 QA。
- `backend/data` 是文件型存储，适合个人站和轻量内容维护，不适合作为高并发多作者 CMS。

## 开发计划

- 补充更系统的自动化测试。
- 完善真实生产部署记录与 HTTPS 验收流程。
- 根据实际使用继续收敛 OAuth、SMTP、OSS 和 AI Provider 的配置体验。
- 持续维护前台可读性、移动端表现和管理端内容工作流。

## 许可证

暂未声明开源许可证。使用、分发或二次开发前请先确认项目授权。

## 致谢

项目使用 Vue、Vite、FastAPI、Tailwind CSS、Pinia、marked、DOMPurify、highlight.js、CodeMirror 等开源项目构建。若这个项目对你有帮助，欢迎 Star。

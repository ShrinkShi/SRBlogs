# SRBlogs 部署指南

SRBlogs 前台和后台使用 Vue 3 + Vite + TypeScript，后端使用 FastAPI。本指南推荐使用在线安装器部署到 Ubuntu 22.04，并兼容 Alibaba Cloud Linux / CentOS / RHEL 系服务器。

默认生产路径：

- 应用目录：`/opt/srblogs`
- 环境文件：`/etc/srblogs/backend.env`
- 后端服务：`srblogs-backend`
- 后端监听：`127.0.0.1:8000`

## 1. 在线安装（推荐）

推荐生产流程：

```bash
# 1. 进入中文 TUI 并完成安装
curl -fsSL -o /tmp/srblogs-install.sh https://raw.githubusercontent.com/ShrinkShi/SRBlogs/main/deploy/install-online.sh && sudo bash /tmp/srblogs-install.sh

# 2. 执行诊断
sudo bash /opt/srblogs/deploy/doctor.sh
```

在线安装器优先使用 GitHub Releases latest，不会静默拉取 `main` 分支。TUI 会要求设置安装目录、配置目录、对外访问端口、后端内部端口、站点域名、管理员账号密码、是否安装受限 updater，以及是否尝试配置 UFW 放行端口。

安装完成后会输出公网/内网前台地址、后台地址、API 地址、管理员账号密码、服务状态命令和日志命令。若使用云服务器，请同步在安全组中放行 TUI 中配置的 TCP 端口。

安装日志位于 `/var/log/srblogs/install.TIMESTAMP.log`。日志会脱敏 `ADMIN_PASSWORD`、`JWT_SECRET`、Token、Secret 和 API Key。

如已存在 `/opt/srblogs`，安装器会询问覆盖安装（自动备份）、备份后覆盖或退出；如已存在 `/etc/srblogs/backend.env`，会询问保留、备份重建或退出。覆盖前会自动备份到 `/opt/srblogs.backup.TIMESTAMP`。

`deploy/setup.sh` 仅作为兼容入口保留，内部转调 `deploy/install.sh`。

## 2. 手动安装（高级）

手动安装适用于离线服务器、内网镜像或需要显式传入 zip/source 的场景。zip 包可以直接包含 `admin/ backend/ frontend/`，也可以多一层根目录，例如 `SRBlogs-main/admin`。

```bash
# 1. 上传 zip 到服务器，例如 /opt/SRBlogs-main.zip
sudo bash deploy/install.sh --dry-run --zip /opt/SRBlogs-main.zip
sudo bash deploy/install.sh --zip /opt/SRBlogs-main.zip

# 2. 浏览器打开安装向导
# http://<your-server-ip>/install

# 3. 安装向导完成后重启后端
sudo systemctl restart srblogs-backend

# 4. 执行诊断
sudo bash /opt/srblogs/deploy/doctor.sh
```

## 2.1 install.sh 行为

`install.sh` 会执行：

- 检查 root 权限，`--dry-run` 除外。
- 通过 `dnf` 或 `yum` 安装系统依赖。
- 检测 `python3.11`，再尝试通过包管理器安装。
- 未传入 `--compile-python` 时拒绝源码编译 Python。
- 检测 Node.js >= 20，必要时安装 NodeSource Node 20。
- 创建 `srblogs` 服务用户。
- 准备 `/opt/srblogs`、`/etc/srblogs/backend.env` 和 `backend/data`。
- 在 `/opt/srblogs/backend/.venv` 创建后端虚拟环境。
- 从 `backend/requirements.txt` 安装 Python 依赖。
- 有 `package-lock.json` 时使用 `npm ci`，否则使用 `npm install`。
- 使用 `NODE_OPTIONS=--max-old-space-size=1024` 构建前台和后台。
- 安装 systemd 和 Nginx 配置。
- 启动 nginx 和 `srblogs-backend`，并按 `/api/health`、`/api/system/health` 顺序重试健康检查。

可选参数：

```bash
sudo bash deploy/install.sh --zip /opt/SRBlogs-main.zip --compile-python
sudo bash deploy/install.sh --force-nginx-main
sudo bash deploy/install.sh --app-dir /opt/srblogs --domain example.com
```

默认不会重写 `/etc/nginx/nginx.conf`。脚本只会把 `/etc/nginx/conf.d/default.conf`、`/etc/nginx/conf.d/welcome.conf` 等明确默认站点改名为 `.disabled.TIMESTAMP`，不会处理未知 Nginx 配置。

swap 创建是保守策略：仅当当前无 swap 且 `/` 可用空间大于 4G 时，尝试创建 `/swapfile-srblogs`。swap 创建失败只输出 WARN，不中断安装。

## 3. 手动安装后的 Web 初始化

使用 `deploy/install.sh` 手动安装、或旧部署缺少 `.install.lock` 时，访问：

```text
http://<your-server-ip>/install
```

安装向导会创建 `backend/data/.install.lock`，写入公开站点设置，写入 `/etc/srblogs/backend.env`，保存 `ADMIN_PASSWORD_HASH`，并在后端生成 `JWT_SECRET`。完成后执行：

```bash
sudo systemctl restart srblogs-backend
```

仍然支持手动配置：

```bash
sudo editor /etc/srblogs/backend.env
```

在线安装器会按 TUI 输入写入兼容的 `ADMIN_PASSWORD` 完成初始化；长期运行建议使用 `scripts/reset_admin.py` 轮换为 `ADMIN_PASSWORD_HASH`。`JWT_SECRET`、`PUBLIC_BASE_URL`、`CORS_ORIGINS` 和可选的 `SITE_START_TIME` 应与真实部署地址一致。

忘记后台密码时可重置管理员凭据：

```bash
cd /opt/srblogs/backend
sudo .venv/bin/python scripts/reset_admin.py --username admin --env-file /etc/srblogs/backend.env
sudo systemctl restart srblogs-backend
```

如需重新进入安装向导但保留文章、图片、音乐等业务数据：

```bash
cd /opt/srblogs/backend
sudo .venv/bin/python scripts/reset_install.py
sudo systemctl restart srblogs-backend
```

在线安装器会直接写入生产配置并创建 `.install.lock`。手动 Web 安装期如临时允许 `srblogs` 服务用户写入 `backend.env`，安装后应尽量收紧，例如 `root:srblogs 640` 或 `root:root 600`，以实际服务加载方式为准。

## 4. 手动更新

上传新 zip 后运行：

```bash
sudo bash /opt/srblogs/deploy/update.sh --dry-run --zip /opt/SRBlogs-main.zip
sudo bash /opt/srblogs/deploy/update.sh --zip /opt/SRBlogs-main.zip
sudo bash /opt/srblogs/deploy/doctor.sh
```

`update.sh` 启动后会先复制自身到 `/tmp/srblogs-runner.TIMESTAMP/`，后续更新、回滚和日志逻辑都从 runner 目录执行，避免依赖即将被替换的 `/opt/srblogs/deploy`。

备份目录：

```text
/opt/srblogs.backup.TIMESTAMP/
```

备份内容：

- 当前 `/opt/srblogs`
- `/etc/srblogs/backend.env`
- `/etc/nginx/conf.d/srblogs.conf`
- `/etc/systemd/system/srblogs-backend.service`

更新流程会先在 staging 中构建，再将 current 切到 previous，将 staging 切到 current，随后更新配置、重启服务并检查 `/api/health`、`/api/install/status`，已安装时还会检查 `/api/settings/public`。健康检查会优先尝试 `/api/health`，再兼容旧的 `/api/system/health`，最多重试 30 次、每次间隔 2 秒。任一关键步骤失败都会回滚。

如果回滚后的 `/api/health` 仍失败，脚本会输出：

```text
rollback attempted but healthcheck failed
```

`update.sh` 默认只保留最近 3 个 `/opt/srblogs.backup.*`。不会自动删除 `/opt/srblogs.previous.*` 或 `/opt/srblogs.failed.*`，除非显式传入 `--cleanup`。

## 4.1 WebUI 受限一键更新

后台“检查更新”会继续读取 `ShrinkShi/SRBlogs` GitHub Releases。若要允许管理员在 WebUI 中点击“立即更新”，必须先由 root 安装受限 updater：

```bash
sudo bash /opt/srblogs/deploy/install-updater.sh
```

安装内容包括 `/usr/local/sbin/srblogs-update`、`srblogs-updater.service`、`/etc/sudoers.d/srblogs-updater` 和 `/var/lib/srblogs/update/` 状态目录。Web 后端只触发固定的 `sudo -n systemctl start srblogs-updater.service`，不会以 root 运行，也不会执行用户传入命令或 URL。

如果未安装 updater service、没有 systemd、没有 sudoers 权限或不是 Linux，WebUI 会禁用“立即更新”并提示使用手动更新或执行 `deploy/install-updater.sh`。

## 5. 诊断

运行：

```bash
sudo bash /opt/srblogs/deploy/doctor.sh
```

dry-run：

```bash
sudo bash /opt/srblogs/deploy/doctor.sh --dry-run
```

`doctor.sh` 检查 Python、Node/npm、nginx、systemd、8000 端口、API 端点、后端版本、`backend/data` 写入权限、`backend.env`、前台/后台构建产物、默认 Nginx 冲突、旧 `srblogs.service`、旧明文 `ADMIN_PASSWORD`、安装状态与管理员凭据一致性、swap 和默认弱密钥。后端健康检查会输出真实可用 endpoint。存在 FAIL 时退出码为 `1`；只有 WARN 或全 PASS 时退出码为 `0`。

最后输出：

```text
Summary: PASS=12 WARN=2 FAIL=0
```

## 6. Nginx 注意事项

生成的 Nginx 配置会：

- 从 `/opt/srblogs/frontend/dist` 提供前台静态文件。
- 从 `/opt/srblogs/admin/dist` 提供 `/admin/` 管理端。
- 将 `/api/` 反向代理到 `127.0.0.1:8000`。
- 将 `/uploads/` 反向代理到后端上传服务。
- 将 `/robots.txt` 反向代理到后端路由。
- 为前台和后台配置 Vue history fallback。

生产环境应通过 Certbot、云厂商证书或托管 TLS 接入 HTTPS。

## 7. 日志与数据

- 脚本日志：`/var/log/srblogs/*.log`
- 持久数据：`/opt/srblogs/backend/data`
- 安装锁：`/opt/srblogs/backend/data/.install.lock`
- 服务状态：`systemctl status srblogs-backend --no-pager`
- 后端日志：`sudo journalctl -u srblogs-backend -n 100 --no-pager`
- Nginx 日志：通常是 `/var/log/nginx/access.log` 和 `/var/log/nginx/error.log`

不要通过 Nginx 直接暴露 `.env`、`.manual_backups`、`audit`、源代码目录或 `node_modules`。

## 8. 生产检查

- 已完成在线安装器、`/install`，或已手动配置 `/etc/srblogs/backend.env`。
- 管理员凭据已通过在线安装器、`/install` 或 `scripts/reset_admin.py` 写入。
- `JWT_SECRET` 不是默认值。
- `CORS_ORIGINS` 只包含可信来源。
- 开发端口 `5173`、`5174` 未对外暴露。
- `frontend/dist` 和 `admin/dist` 已存在。
- `/api/settings/public` 不返回 Secret。
- `backend/data` 已有备份。

参见 [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)。

## 9. 脚本静态检查

发布部署脚本变更前运行：

```bash
bash -n deploy/install-online.sh deploy/install.sh deploy/update.sh deploy/doctor.sh deploy/install-updater.sh
```

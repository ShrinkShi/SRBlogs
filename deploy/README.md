# SRBlogs Linux 部署资产

本目录提供 SRBlogs 的 Linux 可重复部署脚本。推荐生产环境使用在线安装器，优先支持 Ubuntu 22.04 的 `apt`，同时兼容 Alibaba Cloud Linux / CentOS / RHEL 系的 `dnf` / `yum`。

默认路径：

- 应用目录：`/opt/srblogs`
- 环境文件：`/etc/srblogs/backend.env`
- 后端服务：`srblogs-backend`
- 后端端口：`127.0.0.1:8000`

## 文件说明

- `install-online.sh`：在线安装入口，从 GitHub Releases 获取最新版本并进入中文 TUI。
- `install.sh`：上传 zip / 本地源码 / 离线服务器的高级手动安装入口。
- `update.sh`：带备份、staging、健康检查和回滚的手动更新。
- `install-updater.sh`：安装 WebUI 受限 updater，不让 Web 后端以 root 运行。
- `doctor.sh`：生产部署诊断。
- `setup.sh`：兼容入口，内部转调 `install.sh`。
- `build-all.sh`：构建前台、后台并检查后端语法。
- `start-backend.sh`：从项目虚拟环境启动 FastAPI。
- `srblogs-backend.service`：systemd 参考 unit。
- `nginx.srblogs.conf`：Nginx 参考配置。
- `healthcheck.sh`：HTTP 健康检查，优先检查 `/api/health`，兼容旧的 `/api/system/health`。

## 在线安装（推荐）

在全新服务器上执行：

```bash
curl -fsSL -o /tmp/srblogs-install.sh https://raw.githubusercontent.com/ShrinkShi/SRBlogs/main/deploy/install-online.sh && sudo bash /tmp/srblogs-install.sh
```

在线安装器会进入中文 TUI，并询问安装目录、配置目录、对外访问端口、后端内部端口、站点域名、管理员账号密码、是否安装受限 updater 以及是否配置 UFW 放行端口。

安装器只从 `ShrinkShi/SRBlogs` 的 GitHub Releases latest 下载版本；如果仓库没有 Release，会明确失败，不会静默拉取 `main` 分支。安装日志写入 `/var/log/srblogs/install.TIMESTAMP.log`，密码、JWT、Token、Secret 和 API Key 会脱敏。

如已存在 `/opt/srblogs`，安装器会询问覆盖安装（自动备份）、备份后覆盖或退出；如已存在 `/etc/srblogs/backend.env`，会询问保留、备份重建或退出。覆盖安装前会自动备份。

## 手动安装（高级）

适用于离线服务器、内网镜像或需要显式传入 zip/source 的场景。推荐先上传 release zip 到服务器。zip 可以直接包含 `admin/ backend/ frontend/`，也可以多一层目录，例如 `SRBlogs-main/admin`。

预览安装计划：

```bash
sudo bash deploy/install.sh --dry-run --zip /opt/SRBlogs-main.zip
```

执行安装：

```bash
sudo bash deploy/install.sh --zip /opt/SRBlogs-main.zip
```

然后访问：

```text
http://<your-server-ip>/install
```

安装向导会写入 `/etc/srblogs/backend.env`、初始化 `backend/data/settings.json`、创建 `backend/data/.install.lock`，保存 `ADMIN_PASSWORD_HASH`，并由后端生成 `JWT_SECRET`。安装完成后重启后端：

```bash
sudo systemctl restart srblogs-backend
```

运行诊断：

```bash
sudo bash /opt/srblogs/deploy/doctor.sh
```

## 手动更新已有部署

预览：

```bash
sudo bash /opt/srblogs/deploy/update.sh --dry-run --zip /opt/SRBlogs-main.zip
```

执行更新：

```bash
sudo bash /opt/srblogs/deploy/update.sh --zip /opt/SRBlogs-main.zip
sudo bash /opt/srblogs/deploy/doctor.sh
```

`update.sh` 会将当前应用、`/etc/srblogs/backend.env`、Nginx 配置和 systemd unit 统一备份到 `/opt/srblogs.backup.TIMESTAMP/`。脚本先在 staging 中完成依赖安装和构建，再切换版本。依赖安装、构建、`nginx -t`、systemd restart 或 API healthcheck 失败都会触发回滚，并对恢复后的旧版本执行 healthcheck。healthcheck 会优先尝试 `/api/health`，再兼容旧的 `/api/system/health`，最多重试 30 次、每次间隔 2 秒，并输出失败原因。

## WebUI 受限一键更新

后台“检查更新”继续读取 `ShrinkShi/SRBlogs` GitHub Releases。若要在 WebUI 点击“立即更新”，先由 root 安装受限 updater：

```bash
sudo bash /opt/srblogs/deploy/install-updater.sh
```

安装后，Web 后端只写入 `/var/lib/srblogs/update/request.json` 并触发固定的 `srblogs-updater.service`。真正更新由 root-owned `/usr/local/sbin/srblogs-update` 执行；它只允许从 `ShrinkShi/SRBlogs` Releases 下载，不接收用户传入 URL 或 shell 命令。

## 安全规则

- `install-online.sh` 不以 root 运行 Web 后端，`srblogs-backend` 始终使用 `srblogs` 系统用户。
- `install-online.sh` 只从 GitHub Releases 下载，不接收用户传入的任意下载 URL。
- `install.sh` 默认不源码编译 Python；只有传入 `--compile-python` 才允许。
- `install.sh` 默认不重写 `/etc/nginx/nginx.conf`；只有传入 `--force-nginx-main` 才允许。
- 脚本只会把明确默认站点 `default.conf`、`welcome.conf` 改名为 `.disabled.TIMESTAMP`。
- 脚本不会删除未知 Nginx 配置，也不会影响服务器上的其他站点。
- `update.sh` 不会先删除 `/opt/srblogs`；它使用 staging、previous、current 的安全切换顺序。
- 默认只清理旧的 `/opt/srblogs.backup.*`，保留最近 3 个。
- `/opt/srblogs.previous.*` 和 `/opt/srblogs.failed.*` 只有传入 `--cleanup` 才会清理。
- 日志会隐藏 `ADMIN_PASSWORD`、`JWT_SECRET`、OAuth Secret、Token 和 API Key。
- 在线安装器会按 TUI 输入写入兼容的 `ADMIN_PASSWORD` 完成初始化；长期运行建议使用 `backend/scripts/reset_admin.py` 轮换为 `ADMIN_PASSWORD_HASH`。

## 日志与数据

- 脚本日志：`/var/log/srblogs/*.log`
- 持久数据：`/opt/srblogs/backend/data`
- 上传目录：`/opt/srblogs/backend/data/uploads`
- 审计日志：`/opt/srblogs/backend/data/audit/audit.log`
- 安装锁：`/opt/srblogs/backend/data/.install.lock`
- 手动更新日志：`/opt/srblogs/backend/data/update_logs`
- 更新下载缓存：`/opt/srblogs/backend/data/update_downloads`
- WebUI updater 状态：`/var/lib/srblogs/update/status.json`
- WebUI updater 日志：`/var/lib/srblogs/update/updater.log`
- 后端日志：`sudo journalctl -u srblogs-backend -n 100 --no-pager`
- 服务状态：`systemctl status srblogs-backend --no-pager`
- 最近日志：`sudo journalctl -u srblogs-backend -n 100 --no-pager`
- Nginx 日志：通常是 `/var/log/nginx/access.log` 和 `/var/log/nginx/error.log`

忘记后台密码时：

```bash
cd /opt/srblogs/backend
sudo .venv/bin/python scripts/reset_admin.py --username admin --env-file /etc/srblogs/backend.env
sudo systemctl restart srblogs-backend
```

仅重置安装状态且保留业务数据：

```bash
cd /opt/srblogs/backend
sudo .venv/bin/python scripts/reset_install.py
sudo systemctl restart srblogs-backend
```

安装完成后应尽量收紧 `/etc/srblogs/backend.env` 权限。`doctor.sh` 会在已安装状态下检测该文件是否仍可被 `srblogs` 服务用户写入，并输出 WARN。

`backend/data` 必须保持 `srblogs` 服务用户可写，尤其是 `update_logs`、`update_downloads` 和 `uploads`。修复命令：

```bash
sudo chown -R srblogs:srblogs /opt/srblogs/backend/data
sudo chmod -R u+rwX,g+rwX /opt/srblogs/backend/data
```

## 静态检查

发布脚本变更前运行：

```bash
bash -n deploy/install-online.sh deploy/install.sh deploy/update.sh deploy/doctor.sh deploy/install-updater.sh
```

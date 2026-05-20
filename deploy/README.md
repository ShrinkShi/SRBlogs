# SRBlogs Linux 部署资产

本目录提供 SRBlogs 的 Linux 可重复部署脚本。主要支持 Alibaba Cloud Linux / CentOS / RHEL 系服务器，使用 `dnf` 或 `yum`。Ubuntu/Debian 暂不作为本版本主要验收目标。

默认路径：

- 应用目录：`/opt/srblogs`
- 环境文件：`/etc/srblogs/backend.env`
- 后端服务：`srblogs-backend`
- 后端端口：`127.0.0.1:8000`

## 文件说明

- `install.sh`：全新服务器一键安装。
- `update.sh`：带备份、staging、健康检查和回滚的一键更新。
- `doctor.sh`：生产部署诊断。
- `setup.sh`：兼容入口，内部转调 `install.sh`。
- `build-all.sh`：构建前台、后台并检查后端语法。
- `start-backend.sh`：从项目虚拟环境启动 FastAPI。
- `srblogs-backend.service`：systemd 参考 unit。
- `nginx.srblogs.conf`：Nginx 参考配置。
- `healthcheck.sh`：简单 HTTP 健康检查。

## 首次安装

推荐先上传 release zip 到服务器。zip 可以直接包含 `admin/ backend/ frontend/`，也可以多一层目录，例如 `SRBlogs-main/admin`。

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

安装向导会写入 `/etc/srblogs/backend.env`、初始化 `backend/data/settings.json`、创建 `backend/data/.install.lock`，并由后端生成 `JWT_SECRET`。安装完成后重启后端：

```bash
sudo systemctl restart srblogs-backend
```

运行诊断：

```bash
sudo bash /opt/srblogs/deploy/doctor.sh
```

## 更新已有部署

预览：

```bash
sudo bash /opt/srblogs/deploy/update.sh --dry-run --zip /opt/SRBlogs-main.zip
```

执行更新：

```bash
sudo bash /opt/srblogs/deploy/update.sh --zip /opt/SRBlogs-main.zip
sudo bash /opt/srblogs/deploy/doctor.sh
```

`update.sh` 会将当前应用、`/etc/srblogs/backend.env`、Nginx 配置和 systemd unit 统一备份到 `/opt/srblogs.backup.TIMESTAMP/`。脚本先在 staging 中完成依赖安装和构建，再切换版本。依赖安装、构建、`nginx -t`、systemd restart 或 API healthcheck 失败都会触发回滚，并对恢复后的旧版本执行 healthcheck。

## 安全规则

- `install.sh` 默认不源码编译 Python；只有传入 `--compile-python` 才允许。
- `install.sh` 默认不重写 `/etc/nginx/nginx.conf`；只有传入 `--force-nginx-main` 才允许。
- 脚本只会把明确默认站点 `default.conf`、`welcome.conf` 改名为 `.disabled.TIMESTAMP`。
- 脚本不会删除未知 Nginx 配置，也不会影响服务器上的其他站点。
- `update.sh` 不会先删除 `/opt/srblogs`；它使用 staging、previous、current 的安全切换顺序。
- 默认只清理旧的 `/opt/srblogs.backup.*`，保留最近 3 个。
- `/opt/srblogs.previous.*` 和 `/opt/srblogs.failed.*` 只有传入 `--cleanup` 才会清理。
- 日志会隐藏 `ADMIN_PASSWORD`、`JWT_SECRET`、OAuth Secret、Token 和 API Key。

## 日志与数据

- 脚本日志：`/var/log/srblogs/*.log`
- 持久数据：`/opt/srblogs/backend/data`
- 上传目录：`/opt/srblogs/backend/data/uploads`
- 审计日志：`/opt/srblogs/backend/data/audit/audit.log`
- 安装锁：`/opt/srblogs/backend/data/.install.lock`
- 后端日志：`sudo journalctl -u srblogs-backend -n 100 --no-pager`
- 服务状态：`systemctl status srblogs-backend --no-pager`
- 最近日志：`sudo journalctl -u srblogs-backend -n 100 --no-pager`
- Nginx 日志：通常是 `/var/log/nginx/access.log` 和 `/var/log/nginx/error.log`

安装完成后应尽量收紧 `/etc/srblogs/backend.env` 权限。`doctor.sh` 会在已安装状态下检测该文件是否仍可被 `srblogs` 服务用户写入，并输出 WARN。

## 静态检查

发布脚本变更前运行：

```bash
bash -n deploy/install.sh deploy/update.sh deploy/doctor.sh
```

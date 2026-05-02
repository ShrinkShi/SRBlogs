# SRBlogs Windows 本地启动

推荐使用仓库根目录下的专用脚本启动。脚本会固定端口并检查占用，不会让 Vite 自动跳端口。

## 固定地址

- 后端文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/api/health`
- 前台：`http://127.0.0.1:5173`
- 后台：`http://127.0.0.1:5174/admin/`
- 默认后台账号：`admin / change-me`

## 一键启动

双击或在 PowerShell 中运行：

```powershell
.\start-all.cmd
```

该脚本会打开三个独立窗口：

- `start-backend.cmd`
- `start-frontend.cmd`
- `start-admin.cmd`

## 单独启动

```powershell
.\start-backend.cmd
.\start-frontend.cmd
.\start-admin.cmd
```

前台和后台脚本显式使用 `npm.cmd run dev -- --host 127.0.0.1 --port <port> --strictPort`。

## 端口占用

如果 8000、5173 或 5174 已被占用，脚本会输出占用 PID，例如：

```text
[ERROR] Port 5173 is already in use by PID 12345.
Stop it with: taskkill /PID 12345 /F
```

请确认该进程确实可以停止后再执行 `taskkill`。

## 说明

- 不要等待 `npm run dev` 自然退出；它是常驻开发服务。
- 如果页面刚打开时报错，等待对应终端完成编译后刷新。
- 本项目固定 Tailwind CSS `3.4.17`，避免 Tailwind v4 与现有配置不兼容。

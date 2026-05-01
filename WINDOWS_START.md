# SRBlogs Windows 本地启动修正版

## 后端

```powershell
cd C:\Users\ASUS\Desktop\SRBlogs\backend
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env -Force
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

访问 http://127.0.0.1:8000/docs。

## 前端

```powershell
cd C:\Users\ASUS\Desktop\SRBlogs\frontend
Copy-Item .env.development.example .env.development -Force
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
npm install
npm run dev
```

访问 http://127.0.0.1:5173。

## 后台

```powershell
cd C:\Users\ASUS\Desktop\SRBlogs\admin
Copy-Item .env.development.example .env.development -Force
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
npm install
npm run dev
```

访问 http://127.0.0.1:5174/admin/。

默认账号：admin / change-me。

## 修正点

原包使用 tailwindcss latest，会安装 Tailwind v4；但项目配置是 Tailwind v3 写法。现在已固定为 tailwindcss 3.4.17。

# Security Notes

## Secret Storage

- JWT Secret、管理员密码、AI Key、OSS Key、GitHub OAuth Secret 只能保存在后端 `.env` 或服务端配置。
- 前台只能读取 `GET /api/settings/public` 返回的公开站点配置。
- 后台 settings 接口也不得返回 Secret 明文，只能返回 `xxxConfigured` 布尔值。
- 不得把 Secret 写入 `frontend/`、`admin/` 或任何会进入构建产物的文件。

## Uploads

- 上传接口必须要求管理员 JWT。
- 后端必须同时校验扩展名、MIME 和大小。
- 当前允许：`.jpg`、`.jpeg`、`.png`、`.gif`、`.webp`、`.svg`。
- 当前允许 MIME：`image/jpeg`、`image/png`、`image/gif`、`image/webp`、`image/svg+xml`。
- 当前大小上限：5 MB。

## Slug And Paths

- `slug` 必须通过 `validate_slug`。
- 禁止空字符串、`..`、`/`、`\` 和白名单外字符。
- 所有数据路径必须通过 `resolve_data_path`，最终路径必须仍位于 `backend/data` 内。
- 禁止业务路由拼接任意文件系统路径后写入。

## Markdown And Comments

- 前台 Markdown 渲染必须经过 DOMPurify 清洗。
- 评论提交内容必须由后端清洗后保存。
- Markdown 内容允许用户输入，但渲染时不得直接插入未经清洗的 HTML。
- 后台删除评论必须要求管理员 JWT。
- 删除评论前必须备份对应评论 JSON 文件。
- 删除不存在的评论必须返回 404，不允许静默成功。

## JSON And Markdown Writes

- 所有 JSON/Markdown 读写必须走 `backend/app/services/file_store.py`。
- 写入必须使用临时文件 + 原子替换。
- 覆盖或删除已有文件前必须调用 `backup_file`。
- 禁止业务路由或业务 service 直接 `open(..., "w")` 写 JSON/Markdown。

## Pending Queue Scope

状态机固定为：

- `editing`：正在编辑，尚未进入暂存队列。
- `pending`：已加入暂存队列，等待应用。
- `applied`：已成功写入后端数据。
- `failed`：应用失败，保留错误信息，允许重试或移除。

第一阶段本地 `pendingOperations` 只覆盖：

- settings 修改
- 文章新建
- 文章编辑
- 文章删除
- 草稿发布

图片上传、Secret 修改、评论管理暂不进入本地 `pendingOperations`。第一阶段队列在刷新页面后会丢失；第二阶段再做服务端持久化。

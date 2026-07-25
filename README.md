# SMS Dashboard

一个面向个人部署场景的轻量短信验证码看板：

- Android 手机通过 SmsForwarder Webhook 转发短信
- FastAPI 接收并解析短信发送方和 4～8 位验证码
- 网页每秒自动获取最新短信
- 只在内存中保留最新一条，不使用数据库
- 不包含登录功能和 Token 校验

> 安全提示：此项目未提供身份认证。任何能够访问服务地址的用户均可查看最新短信或调用接口提交内容。建议仅在可信网络中使用，或根据实际需求增加访问控制。

## 相关项目

- [SmsForwarder（短信转发器）](https://github.com/pppscn/SmsForwarder)：Android 端短信、来电和应用通知监控及转发工具。

## 项目截图

![SMS Dashboard 项目界面](docs/project-screenshot.jpg)

## 项目结构

```text
sms-dashboard-no-auth/
├─ docs/
│  └─ project-screenshot.jpg
├─ index.html
├─ main.py
├─ requirements.txt
├─ start.bat
└─ README.md
```

## 接口说明

| 方法 | 地址 | 用途 |
| --- | --- | --- |
| `GET` | `/` | 打开短信看板 |
| `GET` | `/health` | 检查服务是否运行 |
| `POST` | `/sms` | 接收 SmsForwarder 数据 |
| `GET` | `/latest` | 获取最新一条短信 |

`POST /sms` 请求示例：

```json
{
  "text": "【Google】验证码 123456",
  "device": "手机A"
}
```

## Android 手机端配置

### 1. 安装 SmsForwarder

从 [SmsForwarder 官方 Releases](https://github.com/pppscn/SmsForwarder/releases)
下载并安装 APK。首次启动时，根据系统提示完成应用初始化。

### 2. 授予必要权限

进入 Android 系统的应用信息页面，为 SmsForwarder 授予以下权限：

- **短信权限**：允许接收短信和读取短信。
- **通知类短信权限**：如果系统单独显示“通知类短信”权限，将其设置为允许。
- **电话或手机信息权限**：用于读取 SIM 卡槽及 `SubId` 等信息。
- **通知权限**：允许 SmsForwarder 发送常驻通知，有助于维持后台运行。

如需转发其他应用的通知，还需要进入系统设置中的“通知使用权”或
“设备和应用通知”，允许 SmsForwarder 读取通知。仅转发普通短信时，
通知使用权不是接收短信的必要条件。

发送短信、联系人和通话记录等权限仅用于对应的扩展功能。只接收并转发
短信时，可根据实际功能需要决定是否授权。

部分手机系统带有“验证码保护”或“禁止第三方读取验证码”功能。如果
SmsForwarder 能收到普通短信但无法读取验证码短信，需要在系统隐私或
短信保护设置中关闭针对 SmsForwarder 的验证码保护。

完成授权后，进入 SmsForwarder 的“通用设置”，开启“转发短信广播”。
如果应用仍提示权限不完整，可点击对应设置项重新触发授权，或进入 Android
系统的应用权限页面逐项检查。

### 3. 设置后台常驻

Android 系统可能在熄屏或长时间待机后终止后台应用。建议同时完成以下设置：

1. 在 SmsForwarder 的“保活措施”中优先完成页面前几项授权或设置，并启用
   前台服务或应用建议的保活选项。
2. 在系统电池设置中，将 SmsForwarder 设置为“不限制”或“允许后台高耗电”，
   并允许其忽略电池优化。
3. 在系统自启动管理中允许 SmsForwarder 自启动；如果系统提供“关联启动”
   和“后台运行”选项，也一并允许。
4. 打开最近任务列表，将 SmsForwarder 任务卡锁定，避免一键清理时被关闭。
5. 保留 SmsForwarder 的常驻通知，不要关闭该通知类别。

常见品牌的设置入口可能如下，具体名称会随系统版本变化：

| 手机品牌 | 常见设置入口 |
| --- | --- |
| 华为、荣耀 | 应用启动管理 → 关闭自动管理 → 允许自启动、关联启动和后台活动 |
| 小米、红米 | 应用设置 → 权限管理 → 自启动；省电策略设置为无限制 |
| OPPO、realme、一加 | 应用管理 → 自启动管理；电池耗电管理中允许后台运行 |
| vivo、iQOO | 权限管理 → 自启动；后台耗电管理中允许后台高耗电 |
| 三星 | 电池 → 后台使用限制 → 从休眠应用中移除，并允许自动运行 |
| 魅族 | 权限管理 → 后台管理 → 允许后台运行 |

完成设置后重启一次 SmsForwarder，并确认通知栏中存在其常驻通知。

### 4. 添加 Webhook 发送通道

在 SmsForwarder 中进入“发送通道”，新增一个 `Webhook` 通道：

```text
名称：SMS Dashboard
请求方式：POST
请求地址：https://sms.example.com/sms
Content-Type：application/json
```

请求体：

```json
{
  "text": "[msg]",
  "device": "手机A"
}
```

其中 `sms.example.com` 必须替换为服务器实际绑定的域名，末尾的 `/sms`
必须保留。`device` 可修改为便于识别的设备名称。

保存通道后，使用 SmsForwarder 提供的测试功能检查请求是否成功。服务器
正常响应时会返回类似结果：

```json
{"ok":true,"code":"123456"}
```

### 5. 添加短信转发规则

进入“转发规则 → 短信转发规则”，新增规则并选择上一步创建的 Webhook
发送通道。根据需要设置来源号码或短信内容匹配条件；如需接收全部短信，
则使用不限制来源和内容的匹配方式。保存并启用规则。

用另一部手机发送一条测试短信，确认：

1. SmsForwarder 的转发记录显示请求成功；
2. 网页显示最新短信；
3. 短信包含 4～8 位验证码时，网页能够正确提取并显示。

## Windows 宝塔部署教程

### 1. 上传项目

下载项目源码并解压到：

```text
C:\wwwroot\sms-dashboard-no-auth
```

### 2. 安装 Python 环境

在宝塔面板中打开：

```text
网站 → Python项目 → Python环境管理
```

安装 Python 3.11。本文示例环境路径为：

```text
C:\BtSoft\python\python_3.11.15\python.exe
```

如 Python 版本或安装目录不同，请同步修改后续启动命令。

### 3. 安装依赖

可以在创建 Python 项目时，将“安装依赖包”设置为：

```text
C:\wwwroot\sms-dashboard-no-auth\requirements.txt
```

也可以在宝塔终端执行：

```powershell
& "C:\BtSoft\python\python_3.11.15\python.exe" -m pip install -r "C:\wwwroot\sms-dashboard-no-auth\requirements.txt"
```

### 4. 创建 Python 项目

在宝塔面板中点击“添加 Python 项目”，填写：

```text
项目路径：C:\wwwroot\sms-dashboard-no-auth
项目名称：sms-dashboard-no-auth
Python环境：python_3.11.15
启动方式：命令行启动
环境变量：无
```

启动命令：

```text
C:\BtSoft\python\python_3.11.15\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
```

项目必须使用单个 Worker，否则不同进程保存的“最新短信”可能不一致。

### 5. 检查服务

项目启动后，在 PowerShell 中执行：

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

正常结果：

```json
{"status":"ok"}
```

### 6. 配置反向代理

首先准备一个用于访问看板的域名，并在域名服务商处添加 DNS 解析：

```text
记录类型：A
主机记录：sms
记录值：服务器公网 IP
```

DNS 生效后，在宝塔中新建反向代理网站。以下配置中的
`sms.example.com` 仅为示例，部署时必须替换为实际使用的域名：

```text
绑定域名：sms.example.com
目标 URL：http://127.0.0.1:8000
发送域名：$host
代理目录：/
```

保存反向代理配置后，在网站的 SSL 设置中申请并启用证书，同时开启
HTTP 到 HTTPS 的强制跳转。

配置完成后，两个地址的用途如下：

```text
网页地址：https://sms.example.com/
短信接收接口：https://sms.example.com/sms
```

其中 `/sms` 是本项目内置的 FastAPI 接口路径，不是服务器目录，不需要
在宝塔中创建名为 `sms` 的文件夹，也不需要单独添加一条反向代理规则。
将网站根目录 `/` 代理到 `http://127.0.0.1:8000` 后，`/sms` 接口会自动生效。

例如，实际绑定的域名为 `message.example.net`，则对应地址为：

```text
网页地址：https://message.example.net/
SmsForwarder 请求地址：https://message.example.net/sms
```

### 7. 配置 SmsForwarder

打开 SmsForwarder，新建转发规则并选择 `Webhook`。请求地址由“实际域名”
和固定接口路径 `/sms` 组成：

```text
请求方式：POST
请求地址：https://sms.example.com/sms
Content-Type：application/json
```

请将上述 `sms.example.com` 替换为第 6 步中实际绑定的域名，并保留末尾的
`/sms`。不要将请求地址填写成只有域名的 `https://sms.example.com/`，
否则请求会进入网页首页，而不会进入短信接收接口。

请求体：

```json
{
  "text": "[msg]",
  "device": "手机A"
}
```

本项目不需要配置 `Authorization` 请求头。

### 8. 发送测试短信

PowerShell 测试命令：

```powershell
curl.exe -X POST "https://sms.example.com/sms" `
  -H "Content-Type: application/json" `
  --data-raw '{"text":"【Google】验证码 123456","device":"手机A"}'
```

正常返回：

```json
{"ok":true,"code":"123456"}
```

随后打开：

```text
https://sms.example.com/
```

网页应显示测试短信及其验证码。

## 字段说明

- `text`：SmsForwarder 转发的完整短信内容。
- `device`：设备名称，可自行填写，例如“手机A”。
- `SubId`：Android 的 SIM 订阅 ID，用于区分不同 SIM 卡；本项目不会单独处理它。

## 验证码和发送方匹配规则

- 优先从“验证码、校验码、动态码、认证码、verification code、code”后面提取 4～8 位数字。
- 如果没有关键词，则查找短信中的第一组独立 4～8 位数字。
- 优先把 `【发送方】` 或 `[发送方]` 中的文字作为发送方名称。
- 无法识别发送方时显示“短信”，无法识别验证码时显示“未识别”。

## 更新项目

覆盖服务器中的项目文件后，在宝塔 Python 项目页面重启项目即可。

# StockLLM

StockLLM 是一个面向 A 股场景的本地化股票分析与报告生成系统。项目将行情获取、板块查询、舆情聚合、规则分析、LLM 报告生成、报告投递与社区互动整合到同一个应用中

## 项目概览

当前项目主链路如下：

`行情/指数数据获取 -> 历史数据缓存 -> 多指标分析与融合 -> 舆情聚合与去重 -> LLM 报告生成 -> HTML 预览/邮件发送/历史存档`


<img width="1448" height="1086" alt="img_v3_02169_9a544a70-5335-4efc-90b9-3893320b72cg" src="https://github.com/user-attachments/assets/04dead1a-a931-41b2-a81d-a75447df332f" />


## 项目结构

```text
StockLLM/
├── app.py                         # Flask 入口
├── requirements.txt              # 依赖
├── ai/                           # 大模型调用封装
├── core/
│   ├── app_settings.py           # 管理员、邮件、模型配置
│   ├── config.py                 # 路径与运行目录配置
│   ├── db.py                     # SQLite 初始化与连接
│   └── services/                 # 业务服务层
├── data_sources/                 # 行情与板块数据源
├── sentiment/                    # 舆情抓取、清洗、缓存
├── process/                      # 各类分析 case
├── frontend/
│   ├── templates/                # 页面模板与报告模板
│   └── static/                   # CSS / JS
├── scripts/                      # 数据回填与实验脚本
└── runtime/                      # 运行时缓存、报告、上传文件
```

## 安装与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

至少需要在 `.env` 中设置：

- `ADMIN_PASSWORD`：管理员密码，未配置时应用会拒绝启动
- `FLASK_SECRET_KEY`：用于签名登录会话、长度至少 32 个字符的随机字符串

如需使用 LLM 报告生成功能，还需要配置当前所选模型提供方的 API Key。仅预览界面或使用非 AI 功能时，可以留空模型 API Key，并将 `ENABLE_REPORT_SCHEDULER` 设为 `false`


### 3. 启动项目

```bash
python app.py
```

默认启动地址：

- `http://127.0.0.1:5001`

## 配置说明

当前配置集中在 [`core/app_settings.py`](core/app_settings.py) 中，并支持通过环境变量覆盖。可配置项及示例值见 [`.env.example`](.env.example)。

### 管理员

- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`

首次启动时会自动确保管理员账号存在，并写入数据库

### 模型提供方

- 报告生成模型选择：
  - `REPORT_LLM_PROVIDER`：默认 `xiaomi`，可设为 `doubao`
- 豆包：
  - `ARK_BASE_URL`
  - `ARK_MODEL`
  - `ARK_API_KEY`
- GPT：
  - `OPENAI_BASE_URL`
  - `OPENAI_MODEL`
  - `OPENAI_API_KEY`
- 千问：
  - `QWEN_BASE_URL`
  - `QWEN_MODEL`
  - `QWEN_API_KEY`
- MiMo：
  - `XIAOMI_BASE_URL`：默认 `https://token-plan-sgp.xiaomimimo.com/v1`
  - `XIAOMI_MODEL`：默认 `mimo-v2.5-pro`
  - `XIAOMI_API_KEY`
  - 也兼容文档常见命名：`MIMO_BASE_URL`、`MIMO_MODEL`、`MIMO_API_KEY`
- 联网搜索：
  - `REPORT_ENABLE_WEB_SEARCH`：可显式设为 `true` 或 `false`
  - 未显式配置时，豆包报告生成默认开启联网搜索，小米 MiMo 默认关闭
  - 小米 MiMo 需要账号具备联网搜索工具权限；如果接口提示未启用，代码会降级为普通对话

敏感配置必须通过本地环境变量或 `.env` 注入，不要写入代码、镜像或公开日志

## 数据与缓存说明

- 个股历史数据会缓存到 `runtime/cache/stock_history`
- 大盘指数数据会缓存到 `runtime/cache/market_index`
- 板块、股票目录、排行榜等快照缓存到 `runtime/cache/api`
- 舆情结果缓存到 `runtime/cache/sentiment`
- 生成过的报告上下文会额外保存到 `runtime/cache/reports`

项目对外部数据源做了多源兜底，但行情、舆情与板块数据仍然依赖第三方接口可用性

## 界面预览

### 舆情界面

<img width="2878" height="1798" alt="img_v3_02169_d22eb27e-1778-42b2-bdf3-ba2aa91e65cg" src="https://github.com/user-attachments/assets/42de3f92-ed5d-40e1-956d-be3679a3b11a" />

### 分析报告

<img width="2878" height="1792" alt="img_v3_02169_0cd060a1-076f-42d2-93b3-9574600c6dfg" src="https://github.com/user-attachments/assets/8b580c6f-08e2-43b8-9ee2-f5eeb95c87e0" />

## 开发提示

- Flask Debug 默认关闭，仅应在受控的本地开发环境通过 `FLASK_DEBUG=true` 临时启用
- SQLite 表会在启动时自动创建和迁移补列
- 论坛图片仅支持 `png/jpg/jpeg/gif/webp`
- 邮件验证码默认有效期为 10 分钟
- 历史报告按用户维度保存

## 部署说明

- Docker Compose 会把数据库与 `runtime/` 挂载到宿主机，生产环境应自行设置目录权限、备份与 TLS 证书。
- 仓库不包含会自动执行的生产部署工作流。`docs/deploy.example.yml` 仅是未启用的手动部署示例，不会被 GitHub Actions 自动加载。
- 如需启用示例，应先移入 `.github/workflows/`，逐项审核，并为 `production` Environment 配置审批保护、`CONTAINER_REGISTRY`、`APP_IMAGE_REPOSITORY` 两个 Variables，以及示例中列出的 Secrets
- `ENABLE_TEST_ENDPOINTS` 和 `ENABLE_SENTIMENT_DEBUG` 默认关闭，不应在公网环境开启


## 免责声明

本项目提供的行情、舆情、指标分析与 LLM 生成内容仅供学习、研究和信息参考，不构成任何投资建议。市场数据与模型输出可能存在延迟、遗漏或错误，使用者应独立判断并自行承担投资风险

## 许可证

代码及仓库内素材采用 [MIT License](LICENSE) 发布

## 参与贡献

提交问题或改进前，请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)

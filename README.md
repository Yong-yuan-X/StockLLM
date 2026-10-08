# StockLLM

StockLLM 是一个面向 A 股场景的本地化股票分析与报告生成系统。项目将行情获取、板块查询、舆情聚合、规则分析、LLM 报告生成、报告投递与社区互动整合到同一个 Flask 应用中。

## 项目概览

当前项目主链路如下：

`行情/指数数据获取 -> 历史数据缓存 -> 多指标分析与融合 -> 舆情聚合与去重 -> LLM 报告生成 -> HTML 预览/邮件发送/历史存档`

除了分析能力外，项目还包含：

- 用户注册、登录、邮箱验证码校验
- 自选股管理
- 大盘指数与个股图表展示
- 板块成分股查询
- 论坛发帖、评论、点赞、图片上传
- 管理员用户查看与注销

## 当前功能

### 1. 用户与权限

- 支持账号注册、登录
- 登录标识支持 `用户名 / 邮箱 / UUID`
- 注册需要邮箱验证码
- 普通用户自动分配三位数 UUID
- 管理员可查看全部用户并注销普通用户

相关接口：

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/send_email_code`
- `GET /api/users`
- `DELETE /api/users/<target_user_id>`

### 2. 大盘指数

- 展示上证指数、深证成指、创业板指
- 支持 `1年 / 3个月 / 1个月 / 当天` 周期切换
- 当天优先显示分时走势
- 图表包含价格、均线、成交量、RSI、MACD
- 支持自动刷新
- 支持对大盘指数执行分析与报告生成

相关接口：

- `GET /api/market_indices`
- `POST /api/predict_market_index`

### 3. 板块分析

- 板块搜索
- 板块成分股分页查询
- 支持缓存回退

相关接口：

- `GET /api/sector_options`
- `GET /api/sector_stocks`

### 4. 个股行情与分析

- 支持股票代码/名称搜索
- 个股图表支持多周期查看
- 支持更新本地历史数据缓存
- 支持按选定分析 case 生成趋势分析结果
- 支持风险偏好参与结果融合
- 生成结构化结果后再生成 LLM 报告

相关接口：

- `GET /api/stock_directory`
- `GET /api/stock_charts`
- `POST /api/update_stock_data`
- `POST /api/predict_stock`

### 5. 自选股与市场快照

- 自选股增删查
- 自选股快照分析
- 全市场涨跌分布
- 涨跌排行榜多源兜底

相关接口：

- `POST /api/add_stock`
- `POST /api/delete_stock`
- `GET /api/get_stocks`
- `GET /api/favorites_snapshot`
- `GET /api/market_distribution`
- `GET /api/stock_rankings`

### 6. 舆情分析

- 支持大盘、板块、个股舆情
- 支持多股票舆情聚合
- 支持起止时间范围过滤
- 标题相似度去重
- 支持预览/完整阶段返回

相关接口：

- `GET /api/sentiment/market`
- `GET /api/sentiment/sector`
- `GET /api/sentiment/stock`

### 7. 报告预览、发送与历史记录

- 分析完成后生成 HTML 报告
- 支持预览示例报告
- 支持邮件发送
- 支持按用户保存和下载历史报告

相关接口：

- `GET /report-preview`
- `POST /api/send_report`
- `GET /api/report_histories`
- `GET /api/report_histories/<history_id>/download`

### 8. 设置中心

- 保存报告接收邮箱
- 保存用户自定义 `System Prompt` / `User Prompt`
- 分析时读取用户级 Prompt 配置

相关接口：

- `GET /api/user_settings/email`
- `POST /api/user_settings/email`
- `GET /api/user_settings/llm_prompts`
- `POST /api/user_settings/llm_prompts`

### 9. 论坛

- 发帖
- 图文发帖
- 评论
- 点赞
- 帖子排序与统计

相关接口：

- `GET /api/forum/posts`
- `POST /api/forum/posts`
- `POST /api/forum/comments`
- `POST /api/forum/posts/<post_id>/like`

## 分析能力

当前内置的分析 case 包括：

- `MA`
- `RSI`
- `MACD`
- `趋势判断`
- `Bollinger Bands`
- `ADX`
- `ARIMA`
- `波动率分类`
- `Random Forest`
- `XGBoost`
- `线性回归`

大盘分析与个股分析共用大部分分析框架。系统会先输出结构化分析结果，再结合舆情上下文生成面向展示的报告内容。


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

如需使用 LLM 报告生成功能，还需要配置当前所选模型提供方的 API Key。仅预览界面或使用非 AI 功能时，可以留空模型 API Key，并将 `ENABLE_REPORT_SCHEDULER` 设为 `false`。

HTTPS 部署时还应将 `SESSION_COOKIE_SECURE` 设为 `true`。请勿把 `.env`、数据库、证书、上传文件或运行时缓存提交到仓库。

### 3. 启动项目

```bash
python app.py
```

默认启动地址：

- `http://127.0.0.1:5001`

## 运行时目录

应用启动时会自动创建以下目录：

- `runtime/cache/api`
- `runtime/cache/market_index`
- `runtime/cache/sentiment`
- `runtime/cache/stock_history`
- `runtime/cache/reports`
- `runtime/forum_uploads`
- `runtime/user_avatars`

数据库文件默认位于项目根目录：

- `stock.db`

## 配置说明

当前配置集中在 [`core/app_settings.py`](core/app_settings.py) 中，并支持通过环境变量覆盖。可配置项及示例值见 [`.env.example`](.env.example)。

### 管理员

- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`

首次启动时会自动确保管理员账号存在，并写入数据库。

### 邮件

- `MAIL_HOST`
- `MAIL_PORT`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_USE_TLS`
- `MAIL_USE_SSL`
- `MAIL_FROM_NAME`
- `MAIL_FROM_ADDRESS`

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

敏感配置必须通过本地环境变量或 `.env` 注入，不要写入代码、镜像或公开日志。

## 数据与缓存说明

- 个股历史数据会缓存到 `runtime/cache/stock_history`
- 大盘指数数据会缓存到 `runtime/cache/market_index`
- 板块、股票目录、排行榜等快照缓存到 `runtime/cache/api`
- 舆情结果缓存到 `runtime/cache/sentiment`
- 生成过的报告上下文会额外保存到 `runtime/cache/reports`

项目对外部数据源做了多源兜底，但行情、舆情与板块数据仍然依赖第三方接口可用性。

## 已实现的页面模块

根据当前前端模板，主界面包含以下模块：

- 大盘指数
- 板块分析
- 个股行情
- 个股分析报告生成
- 舆情分析
- 模型说明
- AI托管
- 历史报告
- 论坛
- 设置

## 界面预览

### 舆情界面




### 分析报告



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

## 数据来源与许可

项目依赖包分别遵循其自身许可证；当前 Python 依赖采用 MIT、BSD 或 Apache-2.0 等宽松许可证。行情与舆情数据来自第三方公开接口，其可用性、准确性和使用条件由相应数据提供方决定，使用者应自行确认适用条款

## 免责声明

本项目提供的行情、舆情、指标分析与 LLM 生成内容仅供学习、研究和信息参考，不构成任何投资建议。市场数据与模型输出可能存在延迟、遗漏或错误，使用者应独立判断并自行承担投资风险。本软件按“现状”提供，不保证可用性、准确性或适合生产环境

## 许可证

项目代码及仓库内原创素材采用 [MIT License](LICENSE) 发布。第三方依赖和外部数据不包含在该授权范围内，并继续适用其各自条款

## 参与贡献

提交问题或改进前，请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)

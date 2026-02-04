# CLS 财联社新闻监控与 AI 分析工具

基于 AI 分析的财联社热点实时监控工具，每隔 5 秒爬取最新一条信息，通过 GitHub Copilot API 进行市场情绪分析，评估新闻的市场影响力（1-10分）。

## 功能特点

- 🔄 **实时监控**: 每 5 秒自动获取财联社最新电报
- 🤖 **AI 分析**: 使用 GitHub Copilot SDK 进行智能分析
- 📊 **市场评分**: 1-10 分评估新闻市场热度（10分为最高）
- 🔍 **去重机制**: 自动跳过重复新闻
- 🛡️ **反爬对策**: 
  - API 签名生成
  - User-Agent 轮换
  - 请求重试机制
  - 连接池复用

## 项目结构

```
analysis_cls_newest_msg/
├── main.py              # 主程序入口
├── requirements.txt     # 依赖列表
├── .env.example        # 环境变量示例
├── src/
│   ├── __init__.py
│   ├── config.py       # 配置管理
│   ├── models.py       # 数据模型
│   ├── scraper.py      # 爬虫模块
│   └── analyzer.py     # 分析模块
└── tests/
    ├── __init__.py
    ├── test_scraper.py
    └── test_analyzer.py
```

## 安装

1. 克隆仓库:
```bash
git clone https://github.com/sanchez0623/analysis_cls_newest_msg.git
cd analysis_cls_newest_msg
```

2. 创建虚拟环境并安装依赖:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 配置环境变量:
```bash
cp .env.example .env
# 编辑 .env 文件，填入您的 GitHub Token
```

## 使用方法

### 基本使用

```bash
python main.py
```

### 自定义配置

通过环境变量自定义配置:

```bash
# 设置爬取间隔为 10 秒
SCRAPE_INTERVAL=10 python main.py

# 设置日志级别为 DEBUG
LOG_LEVEL=DEBUG python main.py
```

### 配置选项

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `GITHUB_TOKEN` | - | GitHub 令牌（用于 Copilot API） |
| `SCRAPE_INTERVAL` | 5 | 爬取间隔（秒） |
| `FETCH_COUNT` | 1 | 每次获取的新闻数量 |
| `REQUEST_TIMEOUT` | 10 | 请求超时时间（秒） |
| `MAX_RETRIES` | 3 | 最大重试次数 |
| `LOG_LEVEL` | INFO | 日志级别 |

## 输出示例

```
============================================================
📰 新闻快讯 | 2024-01-15 10:30:45
============================================================
内容: 央行宣布降息25个基点，支持实体经济发展
相关股票: 工商银行, 建设银行
相关主题: 货币政策, 央行
============================================================
📊 市场热度: ★★★★★★★★☆☆ (8/10)
📈 市场影响: 利好
💡 分析: 央行降息释放明确宽松信号，利好银行股和资本市场
🎯 市场影响: 可能推动银行板块和大盘整体上涨
============================================================
```

## 评分标准

| 分数 | 含义 | 示例 |
|------|------|------|
| 9-10 | 重大市场影响 | 央行重大政策、行业突破性进展 |
| 7-8 | 较大市场影响 | 重要经济数据、大型企业重大事件 |
| 5-6 | 一般市场影响 | 普通行业新闻、常规公司公告 |
| 3-4 | 较小市场影响 | 小型公司新闻、地方性事件 |
| 1-2 | 无实质影响 | 无关市场的一般信息 |

## 运行测试

```bash
python -m pytest tests/ -v
```

## 架构设计

### 爬虫模块 (scraper.py)

- **签名生成**: 使用 SHA1 + MD5 双重加密生成 API 签名
- **重试机制**: 使用 tenacity 库实现指数退避重试
- **User-Agent 轮换**: 随机选择 User-Agent 避免被封禁
- **会话管理**: 使用 requests.Session 实现连接池复用

### 分析模块 (analyzer.py)

- **双模式分析**: 
  - 优先使用 GitHub Copilot SDK 进行 AI 分析
  - 备用关键词分析引擎确保服务可用性
- **响应解析**: 智能解析 AI 返回的结构化数据

### 配置管理 (config.py)

- 使用 dataclass 管理配置
- 支持环境变量覆盖
- 集中化配置管理

## 依赖项

- `requests`: HTTP 客户端
- `python-dotenv`: 环境变量管理
- `tenacity`: 重试机制

## 注意事项

1. 请遵守财联社的使用条款，合理使用爬虫
2. 建议设置合理的爬取间隔，避免对服务器造成压力
3. 本工具仅供学习和研究使用，请勿用于商业用途
4. AI 分析结果仅供参考，不构成投资建议

## License

MIT License
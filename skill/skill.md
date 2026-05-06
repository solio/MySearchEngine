# MySearchEngine Skill

基于AI的搜索MCP，专为投研场景优化的搜索引擎。

## 功能描述

本skill提供两种核心能力：
1. **实时搜索**：根据关键词搜索股票、新闻、论坛等信息，自动过滤垃圾内容
2. **历史查询**：根据时间范围（年/月/日）和关键词查询历史搜索结果，供投研分析使用

## 能力详情

### 能力1：实时搜索（search）

根据关键词进行定向搜索，优先返回优质站点内容。

#### 请求参数

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| query | string | 是 | 搜索关键词，如"隆基绿能"或"光伏"，可以是个股名称或行业名称 |
| targeted | boolean | 否 | 是否仅在优质站点搜索，默认false |
| debug | boolean | 否 | 是否返回详细评估信息，默认false |
| use_mock | boolean | 否 | 是否使用mock模式（用于测试，不调用真实搜索引擎），默认false |

#### 返回结果字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| query | string | 搜索关键词，即用户输入的查询内容 |
| search_time | string | 搜索时间（ISO8601格式），如"2026-05-06T10:30:00" |
| mode | string | 搜索模式，"普通搜索"或"定向搜索" |
| result_count | number | 返回结果数，即经过过滤后保留的结果数量 |
| total_results | number | 搜索引擎返回的总结果数 |
| passed_results | number | 通过过滤的结果数 |
| filtered_results | number | 被过滤的结果数 |
| filter_rate | string | 过滤率百分比，如"85.3%" |
| filter_reasons | object | 过滤原因统计，key为原因，value为数量 |
| param_update_suggestion | string/null | 参数更新建议，无建议时为null，当模型认为需要调整过滤参数时返回建议内容 |
| results | array | 搜索结果列表 |
| results[].title | string | 搜索结果标题 |
| results[].url | string | 搜索结果链接 |
| results[].domain | string | 搜索结果域名，如"xueqiu.com" |
| results[].content | string | 摘要内容，搜索结果的正文摘要 |
| results[].is_quality_site | boolean | 是否优质站点，true表示来自优质站点白名单 |
| results[].score | number | 评分（0-100），综合内容质量、站点质量等因素的评分 |
| results[].debug_info | object/null | 调试信息，debug=true时返回，包含详细的评估过程 |

---

### 能力2：历史查询（query_history）

根据时间范围（年/月/日）和关键词查询历史搜索结果。
支持查询特定时间范围内的个股或行业搜索数据。

#### 请求参数

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| year | number | 是 | 年份，如2026 |
| month | number | 否 | 月份，如4（注意：不需要补零，1-12），不提供则查询全年数据 |
| day | number | 否 | 日期，如30（需要month存在，1-31），不提供则查询整月数据 |
| query | string | 否 | 关键词过滤，支持个股名称或行业名称，模糊匹配，不提供则返回所有记录 |

#### 返回结果字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| year | number | 查询的年份 |
| month | number/null | 查询的月份，未提供时为null |
| day | number/null | 查询的日期，未提供时为null |
| query_filter | string/null | 关键词过滤条件，未提供时为null |
| count | number | 查询到的搜索记录数 |
| records | array | 搜索记录列表，每条记录对应一次历史搜索 |
| records[].id | string | 记录ID（由日期时间构成），如"20260430_112531" |
| records[].file_path | string | 原文件路径，记录在本地文件系统中的完整路径 |
| records[].search_time | string | 搜索时间（ISO8601格式），如"2026-05-06T10:30:00" |
| records[].query | string | 查询关键词，即当时搜索的内容（个股名称或行业名称） |
| records[].mode | string | 搜索模式，"普通搜索"或"定向搜索" |
| records[].result_count | number | 搜索结果数，当时返回的结果数量 |
| records[].total_results | number | 搜索引擎返回的总结果数 |
| records[].passed_results | number | 通过过滤的结果数 |
| records[].filtered_results | number | 被过滤的结果数 |
| records[].filter_rate | string | 过滤率百分比，如"85.3%" |
| records[].filter_reasons | object | 过滤原因统计，key为原因，value为数量 |
| records[].results | array | 该次搜索的结果列表 |
| records[].results[].title | string | 搜索结果标题 |
| records[].results[].url | string | 搜索结果链接 |
| records[].results[].domain | string | 搜索结果域名，如"xueqiu.com" |
| records[].results[].content | string | 摘要内容，搜索结果的正文摘要 |
| records[].results[].is_quality_site | boolean | 是否优质站点，true表示来自优质站点白名单 |
| records[].results[].score | number | 评分（0-100），综合内容质量、站点质量等因素的评分 |

---

## 使用示例

### Python调用示例

```python
import skill

# 实时搜索个股
search_result = skill.search(
    query="隆基绿能",
    targeted=True,
    debug=True,
    use_mock=True
)
print(search_result)

# 实时搜索行业
industry_result = skill.search(
    query="光伏",
    targeted=True,
    use_mock=True
)
print(industry_result)

# 查询某年所有数据
history_year = skill.query_history(year=2026)
print(history_year)

# 查询某年某月的数据
history_month = skill.query_history(year=2026, month=4)
print(history_month)

# 查询精确某天的数据
history_day = skill.query_history(year=2026, month=4, day=30)
print(history_day)

# 查询某年某个股的数据
history_stock = skill.query_history(year=2026, query="隆基绿能")
print(history_stock)

# 查询某月某行业的数据
history_industry = skill.query_history(year=2026, month=4, query="光伏")
print(history_industry)
```

### 命令行使用示例

```bash
# 实时搜索
python -m skill search "隆基绿能" --targeted --debug --mock

# 实时搜索行业
python -m skill search "光伏" --targeted --mock

# 查询某年
python -m skill history 2026

# 查询某年某月
python -m skill history 2026 4

# 查询某年某月某日
python -m skill history 2026 4 30

# 查询某年某个股的数据
python -m skill history 2026 --query "隆基绿能"

# 查询某月某行业的数据
python -m skill history 2026 4 --query "光伏"
```

## 目录结构

```
search-engine/
├── api/                # 搜索API客户端
├── config/             # 配置文件（优质站点列表等）
├── filters/            # 过滤器
├── models/             # 数据模型
├── search_results/     # 搜索结果存储（按日期分目录）
│   └── 20260430/
│       ├── 20260430_112531-搜索结果.md
│       └── ...
├── thoughts/           # 思考过程记录
├── skill/              # skill模块目录
│   ├── __init__.py
│   ├── skill.py        # skill主入口
│   └── skill.md        # 本文件
└── skill.py            # 兼容入口（重定向到skill/skill.py）
```

## 数据说明

search_results目录下的数据可供其他模块（如统计目录的prompt_engineer）使用。
数据按日期组织，格式为YYYYMMDD，每个目录下包含当天的搜索结果文件。

## 优质站点列表

配置文件：`config/quality_sites.yaml`

当前支持的优质站点：
- xueqiu.com（雪球）
- cls.cn（财联社）
- 36kr.com（36氪）
- yicai.com（第一财经）
- caixin.com（财新）
- stcn.com（证券时报）
- cs.com.cn（中国证券报）
- nbd.com.cn（每日经济新闻）
- zhihu.com（知乎）
- guba.eastmoney.com（股吧）

## 垃圾关键词过滤

当前会自动过滤包含以下关键词的内容：
- 实时行情、分时走势、K线图、均价线、MACD、KDJ、交易量、技术分析
- 大盘指数、股吧首页、F10资料、财务指标、盘口分析、资金流向、龙虎榜
- 个股点评、千股千评、每日一股、涨停预测、牛股推荐

# MySearchEngine Skill

基于AI的搜索MCP，专为投研场景优化的搜索引擎。

## 功能描述

本skill提供两种核心能力：
1. **实时搜索**：根据关键词搜索股票、新闻、论坛等信息，自动过滤垃圾内容
2. **历史查询**：根据年月查询历史搜索结果，供投研分析使用

## 能力详情

### 能力1：实时搜索（search）

根据关键词进行定向搜索，优先返回优质站点内容。

#### 请求参数

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| query | string | 是 | 搜索关键词，如"隆基绿能" |
| targeted | boolean | 否 | 是否仅在优质站点搜索，默认false |
| debug | boolean | 否 | 是否返回详细评估信息，默认false |

#### 返回结果字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| query | string | 搜索关键词 |
| search_time | string | 搜索时间（ISO8601格式） |
| mode | string | 搜索模式，"普通搜索"或"定向搜索" |
| result_count | number | 返回结果数 |
| total_results | number | 搜索引擎返回的总结果数 |
| passed_results | number | 通过过滤的结果数 |
| filtered_results | number | 被过滤的结果数 |
| filter_rate | string | 过滤率百分比 |
| filter_reasons | object | 过滤原因统计，key为原因，value为数量 |
| param_update_suggestion | string/null | 参数更新建议，无建议时为null |
| results | array | 搜索结果列表 |
| results[].title | string | 标题 |
| results[].url | string | 链接 |
| results[].domain | string | 域名 |
| results[].content | string | 摘要内容 |
| results[].is_quality_site | boolean | 是否优质站点 |
| results[].score | number | 评分（0-100） |
| results[].debug_info | object/null | 调试信息，debug=true时返回 |

---

### 能力2：历史查询（query_history）

根据年月查询历史搜索结果。

#### 请求参数

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| year | number | 是 | 年份，如2026 |
| month | number | 是 | 月份，如4（注意：不需要补零，1-12） |

#### 返回结果字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| year | number | 年份 |
| month | number | 月份 |
| count | number | 查询到的搜索记录数 |
| records | array | 搜索记录列表 |
| records[].id | string | 记录ID（由日期时间构成） |
| records[].file_path | string | 原文件路径 |
| records[].search_time | string | 搜索时间（ISO8601格式） |
| records[].query | string | 查询关键词 |
| records[].mode | string | 搜索模式，"普通搜索"或"定向搜索" |
| records[].total_results | number | 搜索引擎返回的总结果数 |
| records[].passed_results | number | 通过过滤的结果数 |
| records[].filtered_results | number | 被过滤的结果数 |
| records[].filter_rate | string | 过滤率百分比 |
| records[].filter_reasons | object | 过滤原因统计 |
| records[].results | array | 该次搜索的结果列表 |
| records[].results[].title | string | 标题 |
| records[].results[].url | string | 链接 |
| records[].results[].domain | string | 域名 |
| records[].results[].content | string | 摘要内容 |
| records[].results[].is_quality_site | boolean | 是否优质站点 |
| records[].results[].score | number | 评分（0-100） |

---

## 使用示例

### Python调用示例

```python
import skill_mysearchengine

# 实时搜索
search_result = skill_mysearchengine.search(
    query="隆基绿能",
    targeted=True,
    debug=True
)
print(search_result)

# 查询历史
history = skill_mysearchengine.query_history(
    year=2026,
    month=4
)
print(history)
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
└── skill.md            # 本文件
```

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

# AI搜索MCP

自托管的AI友好搜索引擎，专为投研场景优化。

## 快速开始

### 1. 部署 SearXNG

```bash
docker run -d -p 8080:8080 --name searxng searxng/searxng
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 测试搜索

```bash
python main.py "隆基绿能"
```

### 4. 定向搜索（仅优质站点）

```bash
python main.py "隆基绿能" --targeted
```

## 功能特性

- 规则引擎快速过滤垃圾信息
- 优质站点定向搜索
- 可配置的白名单和关键词
- 搜索结果评分重排序

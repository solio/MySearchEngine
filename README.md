# AI搜索MCP

自托管的AI友好搜索引擎，专为投研场景优化。

## 快速开始

### 方案一：使用Mock模式（无需安装任何东西，推荐先试用）

```bash
pip install -r requirements.txt
python main.py "隆基绿能" --mock --debug
```

### 方案二：使用Docker + SearXNG（推荐生产使用）

#### 1. 安装Docker Desktop

Mac:
```bash
# 访问 https://www.docker.com/products/docker-desktop/ 下载安装
# 或使用Homebrew
brew install --cask docker
```

安装后启动Docker Desktop应用。

#### 2. 部署SearXNG

```bash
docker run -d -p 8080:8080 --name searxng searxng/searxng
```

#### 3. 测试搜索

```bash
pip install -r requirements.txt
python main.py "隆基绿能" --debug
```

### 方案三：使用DuckDuckGo（无需Docker）

代码会自动降级使用DuckDuckGo，无需特殊配置。

## 使用方法

### 普通搜索

```bash
python main.py "隆基绿能" --mock
```

### 定向搜索（仅优质站点）

```bash
python main.py "隆基绿能" --targeted --mock
```

### 调试模式（查看评估详情）

```bash
python main.py "隆基绿能" --mock --debug
```

### 指定站点搜索

```bash
python main.py "隆基绿能" --sites xueqiu.com,cls.cn --mock
```

## 功能特性

- 规则引擎快速过滤垃圾信息
- 优质站点定向搜索
- 可配置的白名单和关键词
- 搜索结果评分重排序
- 详细评估统计和debug模式
- 多种搜索源自动降级（SearXNG → DuckDuckGo → Mock）

## 优质站点配置

编辑 `config/quality_sites.yaml` 来配置：
- 优质站点白名单
- 垃圾关键词
- URL模式匹配规则

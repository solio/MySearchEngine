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

#### 3. 配置SearXNG

需要配置SearXNG允许JSON格式，进入容器修改配置文件：
```bash
docker exec searxng sed -i 's/# formats: \[html, csv, json, rss\]/formats: [html, json]/' /etc/searxng/settings.yml
docker restart searxng
```

#### 4. 测试搜索

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

### 批量投研

先创建股票列表文件（格式：`股票代码|股票名称`，每行一个）：

```
601012|隆基绿能
002594|比亚迪
300750|宁德时代
```

然后执行批量搜索：

```bash
python batch.py --file example_stocks.txt --mock
```

使用定向搜索：

```bash
python batch.py --file example_stocks.txt --targeted --mock --debug
```

## Skill使用方法

本项目已支持作为skill被其他agent调用，skill文件位于 `skill/` 子目录。

### 实时搜索

```bash
python -m skill search "隆基绿能" --targeted --debug --mock
```

### 查询历史搜索结果

```bash
# 查询2026年4月的历史搜索记录
python -m skill history 2026 4
```

## 在代码中使用

```python
import skill

# 实时搜索
result = skill.search("隆基绿能", targeted=True, debug=True, use_mock=True)

# 查询历史
history = skill.query_history(year=2026, month=4)
```

## 功能特性

- 规则引擎快速过滤垃圾信息
- 优质站点定向搜索
- 可配置的白名单和关键词
- 搜索结果评分重排序
- 详细评估统计和debug模式
- 多种搜索源自动降级（SearXNG → DuckDuckGo → Mock）
- Skill支持，可被其他agent调用
- 历史搜索结果查询能力
- 批量投研功能，支持按股票列表批量搜索

## 优质站点配置

编辑 `config/quality_sites.yaml` 来配置：
- 优质站点白名单
- 垃圾关键词
- URL模式匹配规则

## Skill文档

详细的skill使用文档请参考 [skill/skill.md](skill/skill.md)

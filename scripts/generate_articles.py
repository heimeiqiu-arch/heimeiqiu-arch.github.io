#!/usr/bin/env python3
"""Generate a researched batch of Chinese Hugo articles using the OpenAI Responses API."""
import datetime as dt
import difflib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

API_URL = "https://api.openai.com/v1/responses"
MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")
COUNT = int(os.getenv("DAILY_ARTICLE_COUNT", "50"))
POSTS_ROOT = Path("content/posts")
OUTPUT_DIR = POSTS_ROOT / "中文"
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

def response_text(payload):
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for part in item.get("content", []):
            if part.get("type") == "output_text":
                return part.get("text", "")
    raise RuntimeError("The model response did not contain output text.")

def call_api(prompt, max_tokens):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it as a GitHub Actions repository secret.")
    request_body = {
        "model": MODEL,
        "input": prompt,
        "tools": [{"type": "web_search", "search_context_size": "medium"}],
        "tool_choice": "required",
        "include": ["web_search_call.action.sources"],
        "text": {"format": {"type": "json_object"}},
        "max_output_tokens": max_tokens,
        "store": False,
    }
    encoded = json.dumps(request_body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=encoded,
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                data = json.loads(response.read().decode("utf-8"))
            if data.get("status") == "incomplete":
                raise RuntimeError("Model response was incomplete; increase output budget or retry.")
            return json.loads(response_text(data))
        except urllib.error.HTTPError as error:
            message = error.read().decode("utf-8", errors="replace")[:1000]
            if error.code in (429, 500, 502, 503, 504) and attempt < 4:
                time.sleep(min(60, 2 ** (attempt + 1)))
                continue
            raise RuntimeError(f"OpenAI API returned HTTP {error.code}: {message}") from error
        except urllib.error.URLError as error:
            if attempt < 4:
                time.sleep(min(60, 2 ** (attempt + 1)))
                continue
            raise RuntimeError(f"Could not reach OpenAI API: {error}") from error
    raise RuntimeError("OpenAI API retries exhausted.")

def read_existing():
    titles, slugs = [], set()
    for path in POSTS_ROOT.rglob("*.md"):
        if path.name == "_index.md":
            continue
        text = path.read_text(encoding="utf-8")
        match = re.search(r'(?m)^title:\s*["\']?(.+?)["\']?\s*$', text)
        if match:
            titles.append({"title": match.group(1), "slug": path.stem})
        slugs.add(path.stem)
    return titles, slugs

def similarity(a, b):
    compact_a = re.sub(r"[\W_]+", "", a.lower())
    compact_b = re.sub(r"[\W_]+", "", b.lower())
    sequence = difflib.SequenceMatcher(None, compact_a, compact_b).ratio()
    def grams(value):
        return {value[i:i + 2] for i in range(max(0, len(value) - 1))}
    ga, gb = grams(compact_a), grams(compact_b)
    overlap = len(ga & gb) / max(1, len(ga | gb))
    return max(sequence, overlap)

def closest_titles(topic, existing, limit=10):
    return sorted(existing, key=lambda item: similarity(topic, item["title"]), reverse=True)[:limit]

def make_topics(existing):
    titles = "\n".join(f"- {row['title']} [{row['slug']}]" for row in existing)
    prompt = f"""你是 CBPayments 中文内容策划。先联网研究近期公开信息和用户问题，再规划今天的 {COUNT} 个中文长文选题。
业务范围：国际线上支付、虚拟卡的合规使用、SaaS 和 AI 服务订阅、广告平台账单、跨境电商付款、企业费用管理与常见支付故障。
目标是回答真实读者问题并带来合适的潜在客户，不要为了占搜索词拆分近似页面，不要重复已有文章。

已有文章标题和路径：
{titles}

请按以下要求：
1. 输出 JSON 对象，格式为 {{ "topics": [{{"title":"...","primary_keyword":"...","search_intent":"...","slug":"english-kebab-case","category":"数字服务或数字广告或线上支付或企业支付"}}]}}。
2. 必须刚好给出 {COUNT} 个题目，每篇解决不同具体问题、场景或决策，不要只替换品牌、地区、卡组织或同义词。
3. 搜索意图要有购买前评估、排障、账单管理、企业流程等变化；围绕业务范围，避免重复问题。
4. 选题须有公开可靠来源可核实；不编造搜索量、趋势或官方规则。
5. 标题用简体中文，slug 用小写英文字母和连字符，且彼此唯一。
6. 不要生成文章正文，只返回合法 JSON。"""
    result = call_api(prompt, 12000)
    topics = result.get("topics")
    if not isinstance(topics, list) or len(topics) != COUNT:
        raise RuntimeError(f"Topic planner returned {len(topics) if isinstance(topics, list) else 0} topics; expected {COUNT}.")
    seen_slugs, seen_titles = set(), []
    for index, topic in enumerate(topics):
        slug = topic.get("slug", "")
        title = topic.get("title", "")
        if not SLUG.fullmatch(slug) or slug in seen_slugs:
            raise RuntimeError(f"Topic {index + 1} has an invalid or duplicate slug.")
        if not title or any(similarity(title, old) >= 0.82 for old in seen_titles):
            raise RuntimeError(f"Topic {index + 1} is too similar to another topic.")
        if any(similarity(title, item["title"]) >= 0.86 for item in existing):
            raise RuntimeError(f"Topic repeats an existing article: {title}")
        seen_slugs.add(slug)
        seen_titles.append(title)
    return topics

def make_article(topic, existing, index):
    nearby = closest_titles(topic["title"], existing, limit=12)
    internal = "\n".join(f"- {row['title']}: /posts/{row['slug']}/" for row in nearby)
    prompt = f"""你是负责 CBPayments 中文网站的资深编辑。联网检索并写出这篇文章，主题为：{topic['title']}
主要搜索词：{topic['primary_keyword']}
读者意图：{topic['search_intent']}
建议分类：{topic['category']}

可用于自然内链的现有文章（只选真正相关的，不要强行插入）：
{internal}

输出 JSON 对象，字段为：
{{"description":"搜索摘要","tags":["标签1","标签2"],"categories":["分类"],"body":"完整 Markdown 正文"}}

要求：
- 正文至少 2400 个汉字（不含标题、链接、标点），目标 2600 至 3500 个汉字，务必达到 2000 个汉字以上。
- 以读者问题为中心，先给结论和适用范围，再分层解释操作、选择或排障步骤；提供实用清单、例子或决策条件，不能靠重复段落凑长度。
- 仅写与题目有关的原创解释。不得为关键词堆砌、批量改写或重复其他文章；不得伪造亲测、用户评价、数据、法规、产品能力或官方规则。
- 使用联网查到的可核实事实，并在正文的相关段落放至少 3 个 Markdown 外部来源链接；优先引用服务商、支付网络、政府或监管机构的官方页面。明确标注信息日期或地区差异。
- 可按上下文加入上述已有文章的 1 至 3 个内链。不要编造 URL；无相关文章时不要加内链。
- 与 CBPayments 的联系只在自然相关时出现，不能承诺支付一定成功、保证获批、规避地区/商户限制或绕过平台规则。需要描述服务时仅使用已知信息：CBPayments 是虚拟卡服务；不确定的费率、适用地区或商户接受情况不要写。
- 使用简体中文，Hugo Markdown 格式。title 已在主题中给出，正文从引言开始；可使用二级和三级标题。description 用 60 至 120 个中文字概括准确内容。
- 只返回合法 JSON，不加代码围栏或 JSON 外解释。"""
    result = call_api(prompt, 8000)
    body = result.get("body", "").strip()
    chinese_count = len(HAN.findall(body))
    links = re.findall(r"\[[^\]]+\]\(https://[^)]+\)", body)
    if chinese_count < 2000:
        raise RuntimeError(f"{topic['slug']} is only {chinese_count} Chinese characters.")
    if len(links) < 3:
        raise RuntimeError(f"{topic['slug']} has fewer than 3 cited source links.")
    description = result.get("description", "").strip()
    tags = result.get("tags")
    categories = result.get("categories") or [topic["category"]]
    if not description or not isinstance(tags, list) or not tags:
        raise RuntimeError(f"{topic['slug']} is missing SEO description or tags.")
    if topic["slug"] in {item["slug"] for item in existing}:
        raise RuntimeError(f"Slug already exists: {topic['slug']}")
    if any(similarity(topic["title"], item["title"]) >= 0.86 for item in existing):
        raise RuntimeError(f"Article title duplicates an existing page: {topic['title']}")
    date = dt.datetime.now(ZoneInfo("Asia/Shanghai")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    quote = lambda value: json.dumps(str(value), ensure_ascii=False)
    front = [
        "---",
        f"title: {quote(topic['title'])}",
        f"date: {date.isoformat()}",
        f"slug: {quote(topic['slug'])}",
        f"description: {quote(description)}",
        "tags:",
        *[f"  - {quote(tag)}" for tag in tags[:8]],
        "draft: false",
        "categories:",
        *[f"  - {quote(category)}" for category in categories[:3]],
        "---",
        "",
    ]
    return "\n".join(front) + body + "\n", chinese_count

def main():
    if COUNT < 1 or COUNT > 50:
        raise RuntimeError("DAILY_ARTICLE_COUNT must be between 1 and 50.")
    existing, _ = read_existing()
    topics = make_topics(existing)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    accepted = []
    for index, topic in enumerate(topics):
        path = OUTPUT_DIR / f"{topic['slug']}.md"
        if path.exists():
            raise RuntimeError(f"Output file already exists: {path}")
        article, chinese_count = make_article(topic, existing + accepted, index)
        path.write_text(article, encoding="utf-8")
        accepted.append({"title": topic["title"], "slug": topic["slug"]})
        print(f"Generated {index + 1}/{COUNT}: {topic['title']} ({chinese_count} Chinese characters)")
        time.sleep(1)
    print(f"Generated {len(accepted)} researched articles in {OUTPUT_DIR}.")

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Article generation stopped: {error}", file=sys.stderr)
        sys.exit(1)

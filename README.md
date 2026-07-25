#!/usr/bin/env python3
"""
Claude APIを使って、config/site.config.json のキーワードから
アフィリエイト記事を自動生成し、articles/data/ にJSONで保存するスクリプト。

環境変数:
  ANTHROPIC_API_KEY  必須。Claude APIキー。

使い方:
  python scripts/generate_article.py
"""
import json
import os
import re
import sys
import datetime
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "site.config.json"
PRODUCTS_PATH = ROOT / "config" / "products.json"
DATA_DIR = ROOT / "articles" / "data"
MANIFEST_PATH = ROOT / "articles" / "manifest.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def slugify(text: str) -> str:
    # 日本語キーワードは日付+連番でslug化する（URLに日本語を含めない）
    today = datetime.date.today().isoformat()
    return f"{today}-{abs(hash(text)) % 10000}"


def pick_next_keywords(config, manifest, n):
    used = set(manifest.get("used_keywords", []))
    remaining = [k for k in config["keywords"] if k not in used]
    if not remaining:
        # 全部使い切ったら最初からループする
        remaining = config["keywords"]
    return remaining[:n]


def build_prompt(config, products, keyword):
    tag = config.get("amazon_associate_tag", "")
    product_lines = []
    for p in products.get("products", []):
        product_lines.append(
            f'- id={p["id"]} 商品名={p["name"]} ASIN={p["asin"]} 想定価格={p.get("price_hint","")} 特徴={p.get("one_line","")}'
        )
    product_block = "\n".join(product_lines) if product_lines else "（登録商品なし。一般的な商品カテゴリの説明のみ行うこと）"

    system = (
        "あなたは日本語のアフィリエイトブログのライターです。"
        f"サイトのテーマは「{config['niche']}」です。"
        "誇大な効能・断定的な医療/安全性の主張は避け、事実ベースで正直なレビュー記事を書きます。"
        "PR記事であることが読者に明確にわかるよう、ステルスマーケティングにならない書き方をします。"
    )

    user = f"""次のキーワードで、SEOを意識した日本語のアフィリエイト記事を書いてください。

キーワード: {keyword}

登録済み商品リスト（このリストにある商品だけを紹介してよい。無い場合は一般的な選び方の解説のみ行い、実在しない商品名やASINを創作しないこと）:
{product_block}

出力は以下のJSON形式のみで返してください（他のテキストは一切含めない）:
{{
  "title": "記事タイトル（32文字前後、キーワードを含む）",
  "summary": "meta description用の100文字程度の要約",
  "body_html": "記事本文のHTML断片（h2/h3, p, ul/li, strong を使う。<html><body>等の外枠タグは含めない。文字数の目安は1200〜1800字）",
  "used_product_ids": ["紹介に使ったproducts.jsonのid。使わなければ空配列"]
}}

body_html内で商品を紹介する場合は、次のクラスのdivを使ってください（ASINと{ '{amazon_tag}' }はそのまま文字列で埋め込んでよい。ビルドスクリプト側では置換しません。手動で products.json の asin を使ってURLを組み立ててください）:
<div class="product-box"><strong>商品名</strong><br>特徴の説明<br><span class="price">想定価格</span><br><a class="affiliate-btn" href="https://www.amazon.co.jp/dp/ASIN?tag={tag}" rel="nofollow sponsored" target="_blank">Amazonで見る</a></div>
"""
    return system, user


def call_claude(system, user):
    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY を環境変数から自動取得
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(block.text for block in resp.content if block.type == "text")
    # モデルがコードフェンスで返した場合に備えて除去
    text = re.sub(r"^```json\s*|\s*```$", "", text.strip())
    return json.loads(text)


def main():
    config = load_json(CONFIG_PATH, {})
    products = load_json(PRODUCTS_PATH, {"products": []})
    manifest = load_json(MANIFEST_PATH, {"used_keywords": [], "articles": []})

    n = config.get("articles_per_run", 2)
    keywords = pick_next_keywords(config, manifest, n)

    if not keywords:
        print("生成対象のキーワードがありません。config/site.config.json の keywords を確認してください。")
        sys.exit(0)

    for kw in keywords:
        system, user = build_prompt(config, products, kw)
        try:
            result = call_claude(system, user)
        except Exception as e:
            print(f"[ERROR] keyword='{kw}' の生成に失敗しました: {e}", file=sys.stderr)
            continue

        slug = slugify(kw)
        entry = {
            "slug": slug,
            "keyword": kw,
            "title": result["title"],
            "summary": result["summary"],
            "body_html": result["body_html"],
            "date": datetime.date.today().isoformat(),
        }
        save_json(DATA_DIR / f"{slug}.json", entry)

        manifest["used_keywords"].append(kw)
        manifest["articles"].append({"slug": slug, "title": entry["title"], "date": entry["date"]})
        save_json(MANIFEST_PATH, manifest)
        print(f"生成完了: {entry['title']} ({slug})")


if __name__ == "__main__":
    main()

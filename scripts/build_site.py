#!/usr/bin/env python3
"""
articles/data/*.json を読み込み、templates/ を使って
docs/ 以下に静的サイト（GitHub Pages公開用）を生成するスクリプト。

使い方:
  python scripts/build_site.py
"""
import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "site.config.json"
DATA_DIR = ROOT / "articles" / "data"
TEMPLATES_DIR = ROOT / "templates"
DOCS_DIR = ROOT / "docs"
DOCS_ARTICLES_DIR = DOCS_DIR / "articles"


def main():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    author_name = config.get("author_name", "編集部")
    author_emoji = config.get("author_emoji", "📝")
    author_bio = config.get("author_bio", "")

    DOCS_DIR.mkdir(exist_ok=True)
    DOCS_ARTICLES_DIR.mkdir(exist_ok=True)
    shutil.copy(TEMPLATES_DIR / "base_style.css", DOCS_DIR / "style.css")

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    article_tpl = env.get_template("article.html.j2")
    index_tpl = env.get_template("index.html.j2")

    articles = []
    for f in sorted(DATA_DIR.glob("*.json"), reverse=True):
        entry = json.loads(f.read_text(encoding="utf-8"))
        articles.append(entry)

        html = article_tpl.render(
            title=entry["title"],
            summary=entry["summary"],
            date=entry["date"],
            body_html=entry["body_html"],
            site_name=config["site_name"],
            author_name=author_name,
            author_emoji=author_emoji,
            author_bio=author_bio,
        )
        (DOCS_ARTICLES_DIR / f"{entry['slug']}.html").write_text(html, encoding="utf-8")

    last_updated = max((a["date"] for a in articles), default="")

    index_html = index_tpl.render(
        site_name=config["site_name"],
        site_description=config["site_description"],
        articles=articles,
        author_name=author_name,
        author_emoji=author_emoji,
        author_bio=author_bio,
        last_updated=last_updated,
    )
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")

    print(f"ビルド完了: 記事{len(articles)}件を docs/ に出力しました。")


if __name__ == "__main__":
    main()

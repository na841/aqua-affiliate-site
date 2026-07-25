name: Weekly Auto Post

on:
  schedule:
    # UTC基準。UTC 21:00 = 日本時間 翌6:00（毎週月曜 JST朝に実行）
    - cron: "0 21 * * SUN"
  workflow_dispatch: {}

permissions:
  contents: write

jobs:
  generate-and-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r scripts/requirements.txt

      - name: Generate articles
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python scripts/generate_article.py

      - name: Build site
        run: python scripts/build_site.py

      - name: Commit and push
        run: |
          git config user.name "auto-publisher-bot"
          git config user.email "actions@users.noreply.github.com"
          git add articles docs
          git diff --cached --quiet || git commit -m "Auto: weekly article update"
          git push

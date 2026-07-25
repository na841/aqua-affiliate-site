# 全自動アフィリエイトサイト 雛形

Claude API で記事を自動生成し、GitHub Pages に無料公開し、GitHub Actions で毎週自動更新する構成の雛形です。

## 構成
config/site.config.json ← サイト名・ジャンル・キーワード・アフィリエイトタグ
config/products.json ← 紹介する商品（ASINを手動登録）
scripts/generate_article.py ← Claude APIで記事生成 → articles/data/.json に保存
scripts/build_site.py ← articles/data/.json → docs/ 以下にHTML生成
templates/ ← 記事・トップページのテンプレート、CSS
.github/workflows/weekly-post.yml ← 毎週日曜(UTC)自動実行 → 生成→ビルド→コミット→push
docs/ ← GitHub Pagesで公開する実体（このフォルダをPagesの公開先に指定）
## セットアップ手順

1. GitHubアカウント作成 → 新規リポジトリを作成（Public）
2. このフォルダの中身をリポジトリにpush
3. リポジトリの Settings → Pages → Source を `main` ブランチ / `/docs` フォルダ に設定
4. Settings → Secrets and variables → Actions → `ANTHROPIC_API_KEY` を登録
   （Claude APIのキーは https://console.anthropic.com/ から取得）
5. `config/site.config.json` を自分のジャンルに書き換える
6. `config/products.json` に紹介したい商品のASINを手動で登録
   （Amazon商品ページURLの `/dp/XXXXXXXXXX` の部分がASIN）
7. Actionsタブから `Weekly Auto Post` を手動実行（workflow_dispatch）して動作確認
8. 問題なければ、毎週日曜UTC21:00（日本時間 月曜6:00）に自動実行されます

## 費用の目安

- GitHubホスティング：無料
- Claude API：記事1本あたり数円〜十数円程度（週2本なら月100円未満が目安）
- ドメイン：github.io を使えば無料（独自ドメインは別途年数千円）

## 重要な注意点

- **Amazonアソシエイトの審査**：新規・無アクセスのサイトはいきなり承認されないことが多いです。
  まず記事を10本前後たまえてから申請する、または楽天アフィリエイト・A8.net・もしもアフィリエイト
  など審査のハードルが比較的低いASPから始めるのが現実的です。
- **完全放置は検索エンジン的にリスクがあります**：生成された記事は公開前に一度目を通し、
  事実確認と誤情報のチェックをすることを強く推奨します。
- **ステマ規制（景品表示法）**：2023年10月から、広告であることを隠した表示は法律で禁止されています。
  本テンプレートは記事末に広告表示を自動挿入していますが、内容や配置が十分か必ず確認してください。
- **収益化には時間がかかります**：数ヶ月〜それ以上かかるのが一般的です。

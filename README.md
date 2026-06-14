# TBH Market Price Tracker

TBH (Task Bar Hero) の Steamマーケット価格を1時間ごとに自動取得・記録します。

## 📊 データ

取得したデータは [`data/prices.json`](data/prices.json) に保存されます。

| フィールド | 内容 |
|---|---|
| `items` | 各アイテムの最新価格・出品数 |
| `history` | 1時間ごとの価格履歴（最大7日分） |
| `last_updated` | 最終取得日時（UTC） |

## 🚀 セットアップ

### 1. このリポジトリをフォーク or クローン

```bash
git clone https://github.com/あなたのユーザー名/tbh-market.git
cd tbh-market
```

### 2. GitHub Actions を有効化

リポジトリの **Settings → Actions → General** を開き、
`Allow all actions and reusable workflows` を選択して保存。

### 3. 自動実行を確認

**Actions タブ** → `Fetch TBH Market Prices` ワークフローが表示されていればOK。
毎時0分（UTC）に自動実行されます。

手動で今すぐ実行するには `Run workflow` ボタンを押してください。

## ⚙️ カスタマイズ

### 取得間隔を変える

`.github/workflows/fetch_prices.yml` の cron 式を変更:

```yaml
# 毎時（デフォルト）
- cron: '0 * * * *'

# 30分ごと
- cron: '*/30 * * * *'

# 6時間ごと
- cron: '0 */6 * * *'
```

### 監視アイテムを増やす

`scripts/fetch_prices.py` の `SEARCH_QUERIES` リストに検索ワードを追加してください。

## 📡 データの使い方

`data/prices.json` はそのままGitHub Raw URLで取得できます:

```
https://raw.githubusercontent.com/あなたのユーザー名/tbh-market/main/data/prices.json
```

ウィジェットやスクリプトからこのURLを参照すれば、常に最新価格が取得できます。

## 📝 ライセンス

MIT

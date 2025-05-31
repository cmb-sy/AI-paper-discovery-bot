# AI論文推薦システム

このプロジェクトは、ArXiv APIからAI関連の最新論文を自動的に取得し、引用数や出版日などの情報とともにSlackへ通知するシステムです。

![Slackへの投稿例](https://via.placeholder.com/600x400?text=Slack+Post+Example)

## 主な機能

- **自動論文収集**: ArXiv APIから最新のAI関連論文を取得
- **引用数表示**: Semantic Scholar APIを使用して論文の引用数を表示
- **スマートフィルタリング**: キーワード、引用数、出版日に基づく論文の絞り込み
- **定期的な自動通知**: GitHub Actionsによる毎日の自動実行
- **カスタマイズ可能**: 検索カテゴリ、フィルター条件などを柔軟に設定可能

## クイックスタート

### 前提条件

- Python 3.6以上
- Slackワークスペース（Webhook URL作成のため）
- GitHubアカウント（自動実行のため）

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/essay-recommend.git
cd essay-recommend

# 仮想環境を作成・有効化
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# または venv\Scripts\activate  # Windows

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 設定

1. **Slack Webhook URLの取得**
   - Slackワークスペースで新しいアプリを作成
   - 「Incoming Webhooks」を有効化
   - Webhook URLを取得

2. **設定ファイルの編集**
   - `config.yaml`を開き、フィルタリング設定などを確認・編集
   - ローカル実行の場合は`webhook_url`にSlack Webhook URLを設定

### 実行

```bash
# スクリプトを実行
python arxiv_to_slack.py
```

## 自動実行の設定（GitHub Actions）

GitHub Actionsを使用すれば、サーバーを用意することなく論文の自動通知が可能です。

1. **リポジトリをGitHubにプッシュ**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/essay-recommend.git
   git push -u origin main
   ```

2. **Secretの設定**
   - リポジトリページの「Settings」→「Secrets and variables」→「Actions」に移動
   - 「New repository secret」をクリック
   - Name: `SLACK_WEBHOOK_URL`
   - Value: あなたのSlack Webhook URL
   - 「Add secret」をクリック

3. **Actionsの確認**
   - 「Actions」タブでワークフローの状態を確認
   - 毎日UTC 0:00（日本時間9:00）に自動実行
   - 必要に応じて手動実行も可能

## 詳細設定

### 設定ファイル（config.yaml）

```yaml
# Slack設定
slack:
  webhook_url: "YOUR_SLACK_WEBHOOK_URL"  # GitHub Actionsでは自動置換

# arXiv設定
arxiv:
  # 検索するAI関連のカテゴリ
  categories:
    - "cs.AI"    # 人工知能
    - "cs.CL"    # 計算言語学・自然言語処理
    - "cs.CV"    # コンピュータビジョン
    # 他のカテゴリも追加可能
  
  # 最大取得論文数
  max_results: 15
  
  # 何日前の論文を検索するか
  days_back: 1
  
  # フィルタリング設定
  filters:
    # 過去X年以内の論文
    max_years_old: 3
    
    # キーワードフィルター
    keywords:
      - "transformer"
      - "LLM"
      - "diffusion"
      # 他のキーワードも追加可能
    
    # 最低引用数
    min_citations: 10
    
    # フィルター条件（"or"または"and"）
    filter_logic: "or"
```

### カスタマイズのポイント

- **検索カテゴリの変更**: `arxiv.categories`リストを編集
- **フィルタリング条件の調整**: キーワード追加、引用数閾値の変更、日付範囲の変更
- **メッセージのカスタマイズ**: `arxiv_to_slack.py`の`format_paper_for_slack`関数を編集

### ワークフロー構成（GitHub Actions）

ワークフローは`.github/workflows/daily-paper-post.yml`で設定されています:

```yaml
name: 論文自動投稿
on:
  schedule:
    - cron: '0 0 * * *'  # 毎日UTC 0:00に実行
  workflow_dispatch:  # 手動実行も可能

jobs:
  post-papers:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python arxiv_to_slack.py
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## トラブルシューティング

### 一般的な問題

1. **論文が取得できない**
   - インターネット接続を確認
   - ArXiv APIのステータスを確認（メンテナンス中の場合あり）
   - 検索条件が厳しすぎないか確認

2. **Slackに投稿されない**
   - Webhook URLが正しいか確認
   - Slackアプリの権限設定を確認
   - ログファイル（`arxiv_to_slack.log`）でエラーを確認

3. **GitHub Actionsが動作しない**
   - Secretが正しく設定されているか確認
   - ワークフローファイルの構文エラーがないか確認
   - Actionsタブでログを確認

## ログと監視

- 実行ログは`arxiv_to_slack.log`に保存されます
- GitHub Actionsの実行結果はActionsタブで確認できます
- エラー発生時はログを確認して対処してください

## 依存パッケージ

- `arxiv`: ArXiv APIアクセス用
- `requests`: HTTP通信用
- `slack_sdk`: Slack連携用
- `PyYAML`: 設定ファイル読込用

## ライセンス

MITライセンス

## 貢献

バグ報告や機能要望は、GitHubのIssueを通じてお寄せください。プルリクエストも歓迎します。

---

詳細情報や質問については、[GitHubリポジトリ](https://github.com/yourusername/essay-recommend)をご覧ください。

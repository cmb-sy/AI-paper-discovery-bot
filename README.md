# AI 論文推薦システム

このプロジェクトは、ArXiv API から AI 関連の最新論文を自動的に取得し、引用数や出版日などの情報とともに Slack へ通知するシステムです。

## 主な機能

- **自動論文収集**: ArXiv API から最新の AI 関連論文を取得
- **引用数表示**: Semantic Scholar API を使用して論文の引用数を表示
- **スマートフィルタリング**: キーワード、引用数、出版日に基づく論文の絞り込み
- **定期的な自動通知**: GitHub Actions による毎日の自動実行
- **カスタマイズ可能**: 検索カテゴリ、フィルター条件などを柔軟に設定可能

## スタート

### 前提条件

- Python 3.6 以上
- Slack ワークスペース（Webhook URL 作成のため）
- GitHub アカウント（自動実行のため）

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

1. **Slack Webhook URL の取得**

   - Slack ワークスペースで新しいアプリを作成
   - 「Incoming Webhooks」を有効化
   - Webhook URL を取得

2. **設定ファイルの編集**
   - `config.yaml`を開き、フィルタリング設定などを確認・編集
   - ローカル実行の場合は`webhook_url`に Slack Webhook URL を設定

### 実行

```bash
# スクリプトを実行
python arxiv_to_slack.py
```

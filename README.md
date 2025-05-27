# essay-recommend

このプロジェクトは、AIや機械学習に関連する論文を選別し、1日1回日本語訳をSlackへ通知するシンプルなアプリケーションです。

## 構成

- **src/api/arxiv.py**: arXiv APIと通信し、関連する論文を取得します。
- **src/api/slack.py**: Slack APIと通信し、選別された論文を通知します。
- **src/models/paper.py**: 論文のデータモデルを定義します。
- **src/services/paper_selector.py**: 論文を選別するロジックを実装します。
- **src/services/translator.py**: 論文の要約を日本語に翻訳します。
- **src/services/notifier.py**: 選別された論文をSlackに通知します。
- **src/utils/logger.py**: アプリケーションのロギング機能を提供します。
- **src/utils/config_loader.py**: 設定ファイルを読み込みます。
- **src/main.py**: アプリケーションのエントリーポイントです。

## 設定

- **config/config.yaml**: APIキーや通知先のSlackチャンネルなどの設定を含みます。

## テスト

- **tests/test_paper_selector.py**: 論文選別機能のユニットテスト。
- **tests/test_translator.py**: 翻訳機能のユニットテスト。
- **tests/test_notifier.py**: 通知機能のユニットテスト。

## スクリプト

- **scripts/daily_notification.py**: 1日1回の通知を実行します。

## 依存関係

- **requirements.txt**: プロジェクトの依存関係をリストします。

## 環境変数

- **.env.example**: 環境変数の例を示します。

このプロジェクトを使用することで、最新のAIや機械学習に関する研究を簡単に追跡し、チームと共有することができます。
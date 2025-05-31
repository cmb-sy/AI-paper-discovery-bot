"""
ユーティリティ関数を提供するモジュール
"""
from datetime import datetime

def get_timestamp():
    """現在時刻のフォーマットされた文字列を返す"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def print_with_timestamp(message):
    """タイムスタンプ付きのメッセージを出力する"""
    print(f"{get_timestamp()} - {message}")

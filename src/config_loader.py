"""
設定ファイルを読み込むモジュール
"""
import os
import sys
import yaml
from dotenv import load_dotenv
from .utils import print_with_timestamp

# グローバル変数として設定を保持
config = {}

def load_config():
    """設定ファイルを読み込み、グローバル変数configにセットする"""
    global config
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.yaml')
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print_with_timestamp(f"設定ファイルの読み込みに失敗しました: {e}")
        sys.exit(1)

def get_config():
    """設定情報を取得する"""
    if not config:
        return load_config()
    return config

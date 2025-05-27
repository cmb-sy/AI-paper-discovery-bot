import yaml

def load_config(config_file):
    with open(config_file, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def get_slack_channel(config):
    return config.get('slack', {}).get('channel')

def get_arxiv_api_key(config):
    return config.get('arxiv', {}).get('api_key')

def get_translation_api_key(config):
    return config.get('translation', {}).get('api_key')
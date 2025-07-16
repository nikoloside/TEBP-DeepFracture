import yaml
import os
import re

def replace_variables(value, variables):
    """
    Replace variables in a string value
    """
    if isinstance(value, str):
        for var_name, var_value in variables.items():
            value = value.replace(f"${{{var_name}}}", str(var_value))
    return value

def process_config_recursive(config, variables):
    """
    Recursively process config dictionary to replace variables
    """
    if isinstance(config, dict):
        for key, value in config.items():
            config[key] = process_config_recursive(value, variables)
    elif isinstance(config, list):
        for i, item in enumerate(config):
            config[i] = process_config_recursive(item, variables)
    elif isinstance(config, str):
        config = replace_variables(config, variables)
    return config

def load_config(config_path="config.yaml"):
    """
    load config file and replace variables
    """
    if not os.path.exists(config_path):
        # if current directory not exist, try to find in project root directory
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    # Extract variables (like foundation_path)
    variables = {}
    if isinstance(config, dict):
        for key, value in config.items():
            if isinstance(value, str) and not value.startswith('${'):
                variables[key] = value
    
    # Process config to replace variables
    config = process_config_recursive(config, variables)
    
    return config

def get_training_config():
    """
    get training config
    """
    config = load_config()
    return config.get('03 Training', {}) 
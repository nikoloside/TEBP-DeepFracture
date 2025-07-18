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

def find_config_file(config_path="config.yaml"):
    """
    Find config file in current directory or project root
    """
    # First try the provided path
    if os.path.exists(config_path):
        return config_path
    
    # Try current directory
    current_dir_config = os.path.join(os.getcwd(), "config.yaml")
    if os.path.exists(current_dir_config):
        return current_dir_config
    
    # Try project root (assuming we're in a subdirectory)
    # Go up directories until we find config.yaml
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while current_dir != os.path.dirname(current_dir):  # Stop at root
        root_config = os.path.join(current_dir, "config.yaml")
        if os.path.exists(root_config):
            return root_config
        current_dir = os.path.dirname(current_dir)
    
    # If still not found, try relative to this file
    this_file_dir = os.path.dirname(os.path.abspath(__file__))
    relative_config = os.path.join(this_file_dir, "config.yaml")
    if os.path.exists(relative_config):
        return relative_config
    
    raise FileNotFoundError(f"Could not find config.yaml in any parent directory")

def load_config(config_path="config.yaml"):
    """
    Load config file and replace variables
    """
    try:
        config_file_path = find_config_file(config_path)
    except FileNotFoundError:
        # Fallback to original behavior
        if not os.path.exists(config_path):
            # Try to find in project root directory
            config_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
        else:
            config_file_path = config_path
    
    with open(config_file_path, 'r', encoding='utf-8') as file:
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
    Get training config section
    """
    config = load_config()
    return config

def get_data_generation_config():
    """
    Get data generation config section
    """
    config = load_config()
    return config

def get_cook_data_config():
    """
    Get cook data config section
    """
    config = load_config()
    return config

def get_runtime_config():
    """
    Get runtime config section
    """
    config = load_config()
    return config

def get_foundation_path():
    """
    Get foundation path from config
    """
    config = load_config()
    return config.get('foundation_path', '')

def get_shape_category():
    """
    Get shape category from config
    """
    config = load_config()
    return config.get('shape_category', '') 
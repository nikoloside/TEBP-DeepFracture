#!/usr/bin/env python3
"""
Auto Predict Runtime Runner
Automatically modifies shape and csvNum parameters in predict-runtime.py and runs the script
"""

import os
import sys
import subprocess
import argparse
import re
import yaml
from typing import List, Tuple

def load_config(config_file: str = "predict_config.yaml") -> dict:
    """
    Load configuration from YAML file
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: Configuration file {config_file} not found")
        return {}
    except Exception as e:
        print(f"Error loading configuration file: {e}")
        return {}

def modify_predict_runtime(shape: str, csv_num: int, model_shape: str = None) -> bool:
    """
    Modify the predict-runtime.py file with new shape and csvNum values
    
    Args:
        shape: The shape to use (e.g., "bunny", "squirrel", "lion", etc.)
        csv_num: The CSV number to use
        model_shape: The model shape (if None, uses the same as shape)
    
    Returns:
        bool: True if modification was successful, False otherwise
    """
    model_shape = shape
    
    predict_file = "predict-runtime.py"
    
    if not os.path.exists(predict_file):
        print(f"Error: {predict_file} not found in current directory")
        return False
    
    try:
        # Read the current file
        with open(predict_file, 'r') as f:
            content = f.read()
        
        # Replace shape parameter
        content = re.sub(r'shape = "[^"]*"', f'shape = "{shape}"', content)
        
        # Replace csvNum parameter
        content = re.sub(r'csvNum\s*=\s*\d+', f'csvNum={csv_num}', content)
        
        # Replace modelShape parameter
        content = re.sub(r'modelShape = "[^"]*"', f'modelShape = "{model_shape}"', content)

        # Replace auto_run parameter
        content = re.sub(r'auto_run\s*=\s*False', f'auto_run={True}', content)
        
        # Write the modified content back
        with open(predict_file, 'w') as f:
            f.write(content)
        
        print(f"Successfully modified {predict_file}:")
        print(f"  - shape: {shape}")
        print(f"  - csvNum: {csv_num}")
        print(f"  - modelShape: {model_shape}")
        
        return True
        
    except Exception as e:
        print(f"Error modifying {predict_file}: {e}")
        return False

def run_predict_runtime() -> bool:
    """
    Run the predict-runtime.py script
    
    Returns:
        bool: True if execution was successful, False otherwise
    """
    try:
        print("\n" + "="*50)
        print("Starting predict-runtime.py execution...")
        print("="*50)
        
        # Run the script
        result = subprocess.run([sys.executable, "predict-runtime.py"], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print("\n" + "="*50)
            print("predict-runtime.py completed successfully!")
            print("="*50)
            return True
        else:
            print(f"\nError: predict-runtime.py failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"Error running predict-runtime.py: {e}")
        return False

def get_available_shapes() -> List[str]:
    """
    Get list of available shapes from the maxValues dictionary in predict-runtime.py
    
    Returns:
        List[str]: List of available shape names
    """
    try:
        with open("predict-runtime.py", 'r') as f:
            content = f.read()
        
        # Extract shapes from maxValues dictionary
        match = re.search(r'maxValues\s*=\s*\{([^}]+)\}', content)
        if match:
            shapes_str = match.group(1)
            # Extract shape names from the dictionary
            shapes = re.findall(r'"([^"]+)"', shapes_str)
            return shapes
        
        return []
    except:
        return []

def batch_run(shapes: List[str], csv_numbers: List[int], model_shapes: List[str] = None) -> None:
    """
    Run multiple combinations of shapes and csv numbers
    
    Args:
        shapes: List of shapes to test
        csv_numbers: List of CSV numbers to test
        model_shapes: List of model shapes (if None, uses same as shapes)
    """
    if model_shapes is None:
        model_shapes = shapes
    
    total_runs = len(shapes) * len(csv_numbers)
    current_run = 0
    
    print(f"Starting batch run with {total_runs} combinations...")
    
    for shape in shapes:
        for csv_num in csv_numbers:
            current_run += 1
            print(f"\n{'='*60}")
            print(f"Run {current_run}/{total_runs}: shape={shape}, csvNum={csv_num}")
            print(f"{'='*60}")
            
            # Find corresponding model_shape
            model_shape = shape
            if len(model_shapes) == len(shapes):
                model_shape = model_shapes[shapes.index(shape)]
            
            # Modify and run
            if modify_predict_runtime(shape, csv_num, model_shape):
                if not run_predict_runtime():
                    print(f"Failed to run for shape={shape}, csvNum={csv_num}")
            else:
                print(f"Failed to modify for shape={shape}, csvNum={csv_num}")
    
    print(f"\n{'='*60}")
    print(f"Batch run completed! Total runs: {total_runs}")
    print(f"{'='*60}")

def list_batch_configs(config: dict) -> None:
    """
    List available batch configurations from config file
    
    Args:
        config: Configuration dictionary
    """
    if 'batch_configs' not in config:
        print("No batch configurations found in config file")
        return
    
    print("Available batch configurations:")
    for name, config_data in config['batch_configs'].items():
        print(f"  {name}:")
        print(f"    Shapes: {config_data['shapes']}")
        print(f"    CSV Numbers: {config_data['csv_numbers']}")
        print(f"    Description: {config_data['description']}")
        print()

def main():
    parser = argparse.ArgumentParser(description="Auto Predict Runtime Runner")
    parser.add_argument("--shape", type=str, help="Shape to use (e.g., bunny, squirrel, lion)")
    parser.add_argument("--csv-num", type=int, help="CSV number to use")
    parser.add_argument("--model-shape", type=str, help="Model shape (if different from shape)")
    parser.add_argument("--batch", action="store_true", help="Run in batch mode")
    parser.add_argument("--shapes", nargs="+", help="List of shapes for batch mode")
    parser.add_argument("--csv-numbers", nargs="+", type=int, help="List of CSV numbers for batch mode")
    parser.add_argument("--list-shapes", action="store_true", help="List available shapes")
    parser.add_argument("--config", type=str, default="predict_config.yaml", help="Configuration file path")
    parser.add_argument("--batch-config", type=str, help="Use predefined batch configuration from config file")
    parser.add_argument("--list-configs", action="store_true", help="List available batch configurations")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # List batch configurations
    if args.list_configs:
        list_batch_configs(config)
        return
    
    # List available shapes
    if args.list_shapes:
        available_shapes = get_available_shapes()
        if available_shapes:
            print("Available shapes:")
            for shape in available_shapes:
                print(f"  - {shape}")
        else:
            print("Could not determine available shapes from predict-runtime.py")
        return
    
    # Use predefined batch configuration
    if args.batch_config:
        if 'batch_configs' not in config or args.batch_config not in config['batch_configs']:
            print(f"Error: Batch configuration '{args.batch_config}' not found")
            if 'batch_configs' in config:
                print("Available configurations:")
                for name in config['batch_configs'].keys():
                    print(f"  - {name}")
            return
        
        batch_config = config['batch_configs'][args.batch_config]
        print(f"Using batch configuration: {args.batch_config}")
        print(f"Description: {batch_config['description']}")
        batch_run(batch_config['shapes'], batch_config['csv_numbers'])
        return
    
    # Single run mode
    if not args.batch:
        # Use defaults from config if not specified
        if not args.shape and 'defaults' in config:
            args.shape = config['defaults']['shape']
        if not args.csv_num and 'defaults' in config:
            args.csv_num = config['defaults']['csv_num']
        if not args.model_shape and 'defaults' in config:
            args.model_shape = config['defaults']['model_shape']
        
        if not args.shape or not args.csv_num:
            print("Error: --shape and --csv-num are required for single run mode")
            print("Use --help for usage information")
            return
        
        if modify_predict_runtime(args.shape, args.csv_num, args.model_shape):
            run_predict_runtime()
        else:
            print("Failed to modify predict-runtime.py")
    
    # Batch run mode
    else:
        if not args.shapes or not args.csv_numbers:
            print("Error: --shapes and --csv-numbers are required for batch mode")
            print("Use --help for usage information")
            return
        
        batch_run(args.shapes, args.csv_numbers)

if __name__ == "__main__":
    main() 
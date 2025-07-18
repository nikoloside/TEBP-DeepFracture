# Auto Predict Runtime Runner

This tool automatically modifies the `shape` and `csvNum` parameters in `predict-runtime.py` and runs the script with different configurations.

## Files

- `auto_predict_runner.py` - Main Python script for auto-running
- `run_predict.sh` - Shell script wrapper for easier usage
- `predict_config.yaml` - Configuration file with predefined settings
- `README_auto_runner.md` - This documentation file

## Installation

Make sure you have the required Python packages:

```bash
pip install pyyaml
```

Make the shell script executable:

```bash
chmod +x run_predict.sh
```

## Usage

### 1. Single Run Mode

Run with a specific shape and CSV number:

```bash
# Using Python directly
python3 auto_predict_runner.py --shape bunny --csv-num 260

# Using shell script
./run_predict.sh --shape bunny --csv-num 260
```

### 2. Batch Run Mode

Run multiple combinations of shapes and CSV numbers:

```bash
# Test multiple shapes with multiple CSV numbers
python3 auto_predict_runner.py --batch --shapes bunny squirrel lion --csv-numbers 260 261 262

# Using shell script
./run_predict.sh --batch --shapes bunny squirrel lion --csv-numbers 260 261 262
```

### 3. Using Predefined Configurations

The tool comes with predefined batch configurations in `predict_config.yaml`:

```bash
# List available configurations
python3 auto_predict_runner.py --list-configs

# Use a predefined configuration
python3 auto_predict_runner.py --batch-config comprehensive_test

# Using shell script
./run_predict.sh --batch-config comprehensive_test
```

### 4. List Available Shapes

View all available shapes from the `maxValues` dictionary:

```bash
python3 auto_predict_runner.py --list-shapes
```

### 5. Using Default Values

If you don't specify parameters, the tool will use defaults from the config file:

```bash
# Uses defaults from predict_config.yaml
python3 auto_predict_runner.py
```

## Configuration File

The `predict_config.yaml` file contains:

### Available Shapes
```yaml
available_shapes:
  - squirrel
  - bunny
  - base
  - pot
```

### Predefined Batch Configurations
```yaml
batch_configs:
  all_shapes_single_csv:
    shapes: [bunny, squirrel, lion, bar]
    csv_numbers: [260]
    description: "Test all shapes with CSV number 260"
  
  bunny_multiple_csv:
    shapes: [bunny]
    csv_numbers: [260, 261, 262, 263, 264]
    description: "Test bunny with CSV numbers 260-264"
  
  comprehensive_test:
    shapes: [bunny, squirrel, lion]
    csv_numbers: [260, 261, 262]
    description: "Comprehensive test with 3 shapes and 3 CSV numbers"
```

### Default Settings
```yaml
defaults:
  shape: bunny
  csv_num: 260
  model_shape: bunny
```

## Examples

### Example 1: Quick Test
```bash
# Test bunny with CSV 260
./run_predict.sh --shape bunny --csv-num 260
```

### Example 2: Comprehensive Testing
```bash
# Test all shapes with CSV 260
./run_predict.sh --batch-config all_shapes_single_csv
```

### Example 3: Multiple CSV Numbers
```bash
# Test bunny with multiple CSV numbers
./run_predict.sh --batch-config bunny_multiple_csv
```

### Example 4: Custom Batch Run
```bash
# Custom combination
./run_predict.sh --batch --shapes bunny squirrel --csv-numbers 260 261 262
```

## How It Works

1. **Modification**: The tool uses regex to find and replace the `shape`, `csvNum`, and `modelShape` parameters in `predict-runtime.py`
2. **Execution**: It then runs the modified script using `subprocess`
3. **Batch Processing**: For batch runs, it iterates through all combinations and runs each one
4. **Error Handling**: The tool provides clear error messages and continues with the next run if one fails

## Output

The tool provides detailed output showing:
- Which parameters were modified
- Progress through batch runs
- Success/failure status for each run
- Total execution time

## Troubleshooting

### Common Issues

1. **File not found**: Make sure you're in the correct directory with `predict-runtime.py`
2. **Permission denied**: Make sure the shell script is executable (`chmod +x run_predict.sh`)
3. **Import errors**: Make sure all required Python packages are installed
4. **Configuration errors**: Check that `predict_config.yaml` is valid YAML

### Debug Mode

To see more detailed output, you can modify the `run_predict_runtime()` function to capture and display stderr:

```python
result = subprocess.run([sys.executable, "predict-runtime.py"], 
                      capture_output=True, 
                      text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
```

## Customization

You can easily customize the tool by:

1. **Adding new batch configurations** to `predict_config.yaml`
2. **Modifying the regex patterns** in `modify_predict_runtime()` for different parameter formats
3. **Adding new command-line arguments** in the `argparse` setup
4. **Extending the batch processing logic** for more complex scenarios 
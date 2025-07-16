# Data-Generation Flow

## Overview

This project involves several steps to process 3D object files and run simulations using various tools and services. Below are the detailed steps involved in the process:

### 1. Download OBJ Files
We use the Objeverse API and ShapeNet to download the OBJ files. 

### 2. Transform OBJ to Bullet Scene File
We transform the downloaded OBJ files into Bullet scene files for BEM simulation. 
This transformation is including a normalization process and using Maya with Bullet Plugin or C++ Bullet Code. 
We have written a python script to automate this process as much as possible.

### 3. Attach CSV Config to Bullet File
We write a script to generate the CSV configuration and Bullet files required for the FractureRB. This script ensures that all necessary files are created and properly formatted.

### 4. Set-up CSV-Bullet Folder for Vutlr Instance
We build a pipeline to automatically generate a Vutlr instance. The FractureRB Docker component will be automatically generated as part of this pipeline.

### 5. Run Command and Process Results in Dashboard
After running the command, the Vutlr instance will be generated and will process the FractureRB Docker component. The running process will be displayed on the dashboard, and the results will be automatically saved to Google Drive.

## 6. Configuration
We have a configuration file to save all the settings and parameters required for the above steps. This file ensures that the process runs smoothly and consistently.

## Usage
1. Download the OBJ files using the Objeverse API.
2. Run the shell script to transform the OBJ files into Bullet scene files using Maya.
3. Execute the script to generate the CSV config and Bullet files for the FractureRB Docker component.
4. Build the pipeline to generate the Vutlr instance.
5. Run the command to generate the Vutlr instance and process the FractureRB Docker component. Monitor the process on the dashboard and check the results saved in Google Drive.

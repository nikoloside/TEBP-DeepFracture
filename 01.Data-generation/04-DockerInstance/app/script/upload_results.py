import os
import subprocess

def upload_to_google_drive(file_path, drive_folder_id):
    # Use gdrive command line tool to upload the file to Google Drive
    subprocess.run(["gdrive", "upload", "--parent", drive_folder_id, file_path], check=True)

def upload_simulation_results():
    # Define the folder containing simulation results
    simulation_results_folder = "/path/to/simulation/results"
    
    # Define the Google Drive folder ID where results will be uploaded
    drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    
    # Iterate over all files in the simulation results folder
    for root, dirs, files in os.walk(simulation_results_folder):
        for file in files:
            file_path = os.path.join(root, file)
            upload_to_google_drive(file_path, drive_folder_id)
            print(f"Uploaded {file_path} to Google Drive folder {drive_folder_id}")

if __name__ == "__main__":
    upload_simulation_results()

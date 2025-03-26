import os
import subprocess

def install_google_drive():
    # Update and install required packages
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    subprocess.run(["sudo", "apt-get", "install", "-y", "wget", "gnupg"], check=True)

    # Download and install Google Drive client
    subprocess.run(["wget", "https://dl.google.com/drive-file-stream/GoogleDriveFileStream.deb"], check=True)
    subprocess.run(["sudo", "dpkg", "-i", "GoogleDriveFileStream.deb"], check=True)
    subprocess.run(["sudo", "apt-get", "install", "-f"], check=True)

    # Clean up
    os.remove("GoogleDriveFileStream.deb")

def configure_google_drive():
    # Create configuration directory
    config_dir = os.path.expanduser("~/.config/drivefs")
    os.makedirs(config_dir, exist_ok=True)

    # Write configuration file
    config_file = os.path.join(config_dir, "drivefs.conf")
    with open(config_file, "w") as f:
        f.write("[DriveFS]\n")
        f.write(f"google_drive_key={os.getenv('GOOGLE_DRIVE_KEY')}\n")
        f.write(f"google_drive_url={os.getenv('GOOGLE_DRIVE_URL')}\n")

def main():
    install_google_drive()
    configure_google_drive()
    print("Google Drive has been successfully initialized in Docker Ubuntu.")

if __name__ == "__main__":
    main()

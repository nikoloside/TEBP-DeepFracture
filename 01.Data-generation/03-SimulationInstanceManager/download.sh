#!/bin/bash

# INSTANCE_NAME=$(hostname)  # e.g. spc01
INSTANCE_NAME=$1  # e.g. spc01
TARGET=$2
TIMES=20
FILE_ID="folder_id_for_google_drive_download"
FILE_NAME=/root/.config/rclone/rclone.conf

echo "[*] Detected instance: $INSTANCE_NAME"

# Download rclone.conf
sudo mkdir -p /root/.config/rclone
sudo wget --no-check-certificate "https://docs.google.com/uc?export=download&id=${FILE_ID}" -O ${FILE_NAME}

# git clone github
if [ ! -d fracture-docker ]; then
  git clone https://github.com/nikoloside/fracturerb-docker.git
fi

cd fracturerb-docker

# Override config.json
cat <<EOF > config.json
{
  "host_name": "${INSTANCE_NAME}",
  "category_name": "${TARGET}",
  "run_times": $TIMES,
  "gdrive_name": "fracture-gdrive",
  "gdrive_bullet_path": "BulletData",
  "gdrive_result_path": "SharedResults/${INSTANCE_NAME}",
  "local_bullet_path": "/mnt/bullet",
  "local_result_path": "/mnt/results"
}
EOF

echo "[*] Generated config.json with result path: SharedResults/${INSTANCE_NAME}"

# start auto setup & exec fracture program
sudo chmod +x start.sh

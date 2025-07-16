#!/bin/bash

CONFIG="config.yaml"

# check if install yq（YAML parser）
if ! command -v yq &> /dev/null; then
  echo "Install yq：brew install yq"
  exit 1
fi


# Configuration: VM_NAME ex. spc01, TARGET abstract_animal
VM_NAME=$1
TARGET=$2
CORE=$3

if ! [[ "$CORE" =~ ^[0-9]+$ ]]; then
    CORE=8
fi

if ! command -v yq &> /dev/null; then
  echo "Please install yq：brew install yq"
  exit 1
fi
RESOURCE_GROUP="fracture-group"
LOCATION="eastus"
RESOURCE_GROUP=$(yq '.resourceGroup' config.yaml)
LOCATION=$(yq '.location' config.yaml)
IMAGE="Ubuntu2404"
SIZE="Standard_D8s_v3"  # Changed to D8s_v3 for 8 CPU cores
ADMIN_USER="azureuser"
SSH_KEY_PATH=$(yq '.ssh_path' config.yaml)

# Google Drive download.sh  file ID
DOWNLOAD_ID=$(yq '.download_id' config.yaml)

# Search for Spot-eligible SKUs with 16 vCPUs
echo "🔍 Searching for Spot-eligible SKUs with $CORE vCPUs..."

SKU=$(az vm list-skus --location $LOCATION --output json |
  jq -r '.[] | select(.resourceType=="virtualMachines") |
         select(.capabilities[]? | select(.name=="vCPUs" and .value=="'$CORE'")) |
         select(.capabilities[]? | select(.name=="LowPriorityCapable" and .value=="True")) |
         select(.capabilities[]? | select(.name=="HyperVGenerations" and .value=="V2")) |
         .name' |
  head -n 1)

if [ -z "$SKU" ]; then
  echo "❌ No supported Spot with $CORE vCPU VM SKU。"
  exit 1
fi

echo "✅ Found SKU: $SKU"



# Create cloud-init Instance Config（Auto download download.sh and exec）
cat > cloud-init-${VM_NAME}.yaml <<EOF
#cloud-config
runcmd:
  - cd /home/azureuser/
  - wget --no-check-certificate "https://docs.google.com/uc?export=download&id=${DOWNLOAD_ID}" -O /home/azureuser/download.tar.gz
  - tar -xzvf /home/azureuser/download.tar.gz -C /home/azureuser/
  - sudo chmod +x /home/azureuser/download.sh
  - sudo /home/azureuser/download.sh "${VM_NAME}" "${TARGET}"
EOF

# Create fracture-proj resource group
RG_EXISTS=$(az group exists --name $RESOURCE_GROUP)

if [ "$RG_EXISTS" != "true" ]; then
  echo "🔧 Create resource group：$RESOURCE_GROUP"
  az group create --name $RESOURCE_GROUP --location $LOCATION
else
  echo "✅ Resource group exist：$RESOURCE_GROUP"
fi

# Create VM
az vm create \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --image $IMAGE \
  --size $SKU \
  --priority Spot \
  --max-price -1 \
  --eviction-policy Deallocate \
  --admin-username $ADMIN_USER \
  --ssh-key-value "${SSH_KEY_PATH}" \
  --custom-data cloud-init-${VM_NAME}.yaml \
  --public-ip-sku Standard \
  --output table
  

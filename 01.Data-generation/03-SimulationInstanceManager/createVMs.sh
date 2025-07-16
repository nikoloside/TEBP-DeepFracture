#!/bin/bash

CONFIG="config.yaml"

# check if install yq（YAML parser）
if ! command -v yq &> /dev/null; then
  echo "Install yq：brew install yq"
  exit 1
fi

# Read VM config and create VM with corresponding target
vms=($(yq '.vms[]' $CONFIG))
targets=($(yq '.targets[]' $CONFIG))

for i in "${!vms[@]}"; do
  VM_NAME="${vms[$i]}"
  TARGET="${targets[$i]}"
  echo "🚀 Create VM: $VM_NAME with target: $TARGET"
  ./createVM.sh $VM_NAME $TARGET 16
done

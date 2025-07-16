#!/bin/bash

# Configuration
RESOURCE_GROUP=$1
VM_NAME=$2

if [ -z "$RESOURCE_GROUP" ] || [ -z "$VM_NAME" ]; then
  echo "Usage: ./deleteVM.sh <ResourceGroupName> <VMName>"
  exit 1
fi

echo "🛑 Stop VM: $VM_NAME"
az vm stop --resource-group "$RESOURCE_GROUP" --name "$VM_NAME"

OS_DISK=$(az vm show --resource-group "$RESOURCE_GROUP" --name "$VM_NAME" --query "storageProfile.osDisk.name" -o tsv)
NIC=$(az vm show --resource-group "$RESOURCE_GROUP" --name "$VM_NAME" --query "networkProfile.networkInterfaces[0].id" -o tsv | awk -F'/' '{print $NF}')
PUBLIC_IP=$(az network nic show --resource-group "$RESOURCE_GROUP" --name "$NIC" --query "ipConfigurations[0].publicIpAddress.id" -o tsv 2>/dev/null | awk -F'/' '{print $NF}')

echo "🗑️ Delete SPC: $VM_NAME"
az vm delete --resource-group "$RESOURCE_GROUP" --name "$VM_NAME" --yes

if [ -n "$OS_DISK" ]; then
  echo "💾 Delete OS Disk: $OS_DISK"
  az disk delete --resource-group "$RESOURCE_GROUP" --name "$OS_DISK" --yes
fi

if [ -n "$NIC" ]; then
  echo "🌐 Delete NIC: $NIC"
  az network nic delete --resource-group "$RESOURCE_GROUP" --name "$NIC"
fi

if [ -n "$PUBLIC_IP" ]; then
  echo "🌍 Delete Public IP: $PUBLIC_IP"
  az network public-ip delete --resource-group "$RESOURCE_GROUP" --name "$PUBLIC_IP"
fi

nsgName="${VM_NAME}NSG"
ipName="${VM_NAME}PublicIP"
vnetName="${VM_NAME}VNET"

echo "🌍 Delete NSG: $nsgName"
az network nsg delete --name "$nsgName" --resource-group "$RESOURCE_GROUP"

echo "🌍 Delete Public IP: $ipName"
az network public-ip delete --name "$ipName" --resource-group "$RESOURCE_GROUP"

echo "🌍 Delete VNET: $vnetName"
az network vnet delete --name "$vnetName" --resource-group "$RESOURCE_GROUP"

echo "✅ All Deletion Done"

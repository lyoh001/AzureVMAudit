param location string = resourceGroup().location
param prefix string = replace(resourceGroup().name, 'rg', '')
// param prefix string = concat(replace(resourceGroup().name, 'rg', ''), substring(newGuid(), 0, 7))

resource datalake 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  kind: 'StorageV2'
  location: location
  name: '${prefix}dl'
  properties: {
    accessTier: 'Hot'
    isHnsEnabled: true
  }
  sku: {
    name: 'Standard_LRS'
    tier: 'Standard'
  }
}

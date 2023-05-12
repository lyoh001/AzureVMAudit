param location string = resourceGroup().location
param prefix string = replace(resourceGroup().name, 'rg', '')
// param prefix string = concat(replace(resourceGroup().name, 'rg', ''), substring(newGuid(), 0, 7))

resource databricks 'Microsoft.Databricks/workspaces@2023-02-01' = {
  location: location
  name: '${prefix}dbws'
  sku: {
    name: 'standard'
  }
  properties: {
    managedResourceGroupId: '${subscription().id}/resourceGroups/${prefix}dbwsrg'
  }
}

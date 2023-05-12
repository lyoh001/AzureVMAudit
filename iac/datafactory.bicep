param location string = resourceGroup().location
param prefix string = replace(resourceGroup().name, 'rg', '')
// param prefix string = concat(replace(resourceGroup().name, 'rg', ''), substring(newGuid(), 0, 7))

resource data_factory 'Microsoft.DataFactory/factories@2018-06-01' = {
  location: location
  name: '${prefix}dfv2'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
}

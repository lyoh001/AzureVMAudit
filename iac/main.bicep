targetScope = 'subscription'
@secure()
param token string
@secure()
param password string

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${deployment().name}rg'
  location: deployment().location
}

module databricks 'databricks.bicep' = {
  name: 'databricks'
  scope: rg
}

module datafactory 'datafactory.bicep' = {
  name: 'datafactory'
  scope: rg
}

module datalake 'datalake.bicep' = {
  name: 'datalake'
  scope: rg
}

module funcapp 'funcapp.bicep' = {
  name: 'funcapp'
  scope: rg
}

module logicapps 'logicapps.bicep' = {
  name: 'logicapps'
  scope: rg
}
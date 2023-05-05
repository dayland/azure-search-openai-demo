param sites_infoasst_func_kbdmk_name string = 'infoasst-func-kbdmk'
param serverfarms_infoasst_asp_kbdmk_externalid string = '/subscriptions/fb1ffc74-dba7-4cf6-8aac-d07612837cc7/resourceGroups/infoasst-searchoai-geearl-605/providers/Microsoft.Web/serverfarms/infoasst-asp-kbdmk'

resource sites_infoasst_func_kbdmk_name_resource 'Microsoft.Web/sites@2022-09-01' = {
  name: sites_infoasst_func_kbdmk_name
  location: 'West Europe'
  tags: {
    ProectName: 'Information Assistant'
  }
  kind: 'functionapp,linux'
  properties: {
    enabled: true
    hostNameSslStates: [
      {
        name: '${sites_infoasst_func_kbdmk_name}.azurewebsites.net'
        sslState: 'Disabled'
        hostType: 'Standard'
      }
      {
        name: '${sites_infoasst_func_kbdmk_name}.scm.azurewebsites.net'
        sslState: 'Disabled'
        hostType: 'Repository'
      }
    ]
    serverFarmId: serverfarms_infoasst_asp_kbdmk_externalid
    reserved: true
    isXenon: false
    hyperV: false
    vnetRouteAllEnabled: false
    vnetImagePullEnabled: false
    vnetContentShareEnabled: false
    siteConfig: {
      numberOfWorkers: 1
      linuxFxVersion: 'PYTHON|3.10'
      acrUseManagedIdentityCreds: false
      alwaysOn: true
      http20Enabled: false
      functionAppScaleLimit: 0
      minimumElasticInstanceCount: 0
    }
    scmSiteAlsoStopped: false
    clientAffinityEnabled: false
    clientCertEnabled: false
    clientCertMode: 'Required'
    hostNamesDisabled: false
    customDomainVerificationId: 'EC5C0478DE41906ECB7BA163D1D668CEC053B08AA5D53857A223C5A597DF49DF'
    containerSize: 1536
    dailyMemoryTimeQuota: 0
    httpsOnly: true
    redundancyMode: 'None'
    publicNetworkAccess: 'Enabled'
    storageAccountRequired: false
    keyVaultReferenceIdentity: 'SystemAssigned'
  }
}

resource sites_infoasst_func_kbdmk_name_ftp 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2022-09-01' = {
  parent: sites_infoasst_func_kbdmk_name_resource
  name: 'ftp'
  location: 'West Europe'
  tags: {
    ProectName: 'Information Assistant'
  }
  properties: {
    allow: true
  }
}

resource sites_infoasst_func_kbdmk_name_scm 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2022-09-01' = {
  parent: sites_infoasst_func_kbdmk_name_resource
  name: 'scm'
  location: 'West Europe'
  tags: {
    ProectName: 'Information Assistant'
  }
  properties: {
    allow: true
  }
}

resource sites_infoasst_func_kbdmk_name_web 'Microsoft.Web/sites/config@2022-09-01' = {
  parent: sites_infoasst_func_kbdmk_name_resource
  name: 'web'
  location: 'West Europe'
  tags: {
    ProectName: 'Information Assistant'
  }
  properties: {
    numberOfWorkers: 1
    defaultDocuments: [
      'Default.htm'
      'Default.html'
      'Default.asp'
      'index.htm'
      'index.html'
      'iisstart.htm'
      'default.aspx'
      'index.php'
    ]
    netFrameworkVersion: 'v4.0'
    linuxFxVersion: 'PYTHON|3.10'
    requestTracingEnabled: false
    remoteDebuggingEnabled: true
    remoteDebuggingVersion: 'VS2019'
    httpLoggingEnabled: false
    acrUseManagedIdentityCreds: false
    logsDirectorySizeLimit: 35
    detailedErrorLoggingEnabled: false
    publishingUsername: '$infoasst-func-kbdmk'
    scmType: 'None'
    use32BitWorkerProcess: false
    webSocketsEnabled: false
    alwaysOn: true
    managedPipelineMode: 'Integrated'
    virtualApplications: [
      {
        virtualPath: '/'
        physicalPath: 'site\\wwwroot'
        preloadEnabled: true
      }
    ]
    loadBalancing: 'LeastRequests'
    experiments: {
      rampUpRules: []
    }
    autoHealEnabled: false
    vnetRouteAllEnabled: false
    vnetPrivatePortsCount: 0
    publicNetworkAccess: 'Enabled'
    cors: {
      allowedOrigins: [
        'https://ms.portal.azure.com'
      ]
      supportCredentials: false
    }
    localMySqlEnabled: false
    ipSecurityRestrictions: [
      {
        ipAddress: '100.64.193.70/32'
        action: 'Allow'
        tag: 'Default'
        priority: 100
        name: 'deployment'
        description: 'vs code deployment of function code'
      }
      {
        ipAddress: 'Any'
        action: 'Allow'
        priority: 2147483647
        name: 'Allow all'
        description: 'Allow all access'
      }
    ]
    ipSecurityRestrictionsDefaultAction: 'Allow'
    scmIpSecurityRestrictions: [
      {
        ipAddress: 'Any'
        action: 'Allow'
        priority: 2147483647
        name: 'Allow all'
        description: 'Allow all access'
      }
    ]
    scmIpSecurityRestrictionsDefaultAction: 'Allow'
    scmIpSecurityRestrictionsUseMain: false
    http20Enabled: false
    minTlsVersion: '1.2'
    scmMinTlsVersion: '1.2'
    ftpsState: 'FtpsOnly'
    preWarmedInstanceCount: 0
    functionAppScaleLimit: 0
    functionsRuntimeScaleMonitoringEnabled: false
    minimumElasticInstanceCount: 0
    azureStorageAccounts: {
    }
  }
}

resource sites_infoasst_func_kbdmk_name_9095e80c_3d52_49f2_a5f7_96a6c7edbb0c 'Microsoft.Web/sites/deployments@2022-09-01' = {
  parent: sites_infoasst_func_kbdmk_name_resource
  name: '9095e80c-3d52-49f2-a5f7-96a6c7edbb0c'
  location: 'West Europe'
  properties: {
    status: 4
    author_email: 'N/A'
    author: 'ms-azuretools-vscode'
    deployer: 'ms-azuretools-vscode'
    message: 'Created via a push deployment'
    start_time: '2023-04-04T22:09:55.6060091Z'
    end_time: '2023-04-04T22:11:16.2777585Z'
    active: true
  }
}

resource sites_infoasst_func_kbdmk_name_pdf_prep 'Microsoft.Web/sites/functions@2022-09-01' = {
  parent: sites_infoasst_func_kbdmk_name_resource
  name: 'pdf_prep'
  location: 'West Europe'
  properties: {
    script_root_path_href: 'https://infoasst-func-kbdmk.azurewebsites.net/admin/vfs/home/site/wwwroot/pdf_prep/'
    script_href: 'https://infoasst-func-kbdmk.azurewebsites.net/admin/vfs/home/site/wwwroot/pdf_prep/__init__.py'
    config_href: 'https://infoasst-func-kbdmk.azurewebsites.net/admin/vfs/home/site/wwwroot/pdf_prep/function.json'
    test_data_href: 'https://infoasst-func-kbdmk.azurewebsites.net/admin/vfs/home/data/Functions/sampledata/pdf_prep.dat'
    href: 'https://infoasst-func-kbdmk.azurewebsites.net/admin/functions/pdf_prep'
    config: {
    }
    language: 'python'
    isDisabled: false
  }
}

resource sites_infoasst_func_kbdmk_name_sites_infoasst_func_kbdmk_name_azurewebsites_net 'Microsoft.Web/sites/hostNameBindings@2022-09-01' = {
  parent: sites_infoasst_func_kbdmk_name_resource
  name: '${sites_infoasst_func_kbdmk_name}.azurewebsites.net'
  location: 'West Europe'
  properties: {
    siteName: 'infoasst-func-kbdmk'
    hostNameType: 'Verified'
  }
}

resource sites_infoasst_func_kbdmk_name_2023_04_04T22_28_39_0691030 'Microsoft.Web/sites/snapshots@2015-08-01' = {
  parent: sites_infoasst_func_kbdmk_name_resource
  name: '2023-04-04T22_28_39_0691030'
}
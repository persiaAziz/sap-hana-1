from azure.storage.file import FileService
from azure.storage.file import ContentSettings


#create storage account
import os
import sys
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import StorageAccountCreateParameters
from azure.mgmt.storage.models import Sku, SkuName, Kind
from azure.mgmt.containerinstance import ContainerInstanceManagementClient

tfvars_path = sys.argv[2]
STORAGE_ACCOUNT_NAME = "sapsystemstorage12"
GROUP_NAME = sys.argv[1]
CLIENT_ID = os.environ['AZURE_CLIENT_ID']
CLIENT_SECRET = os.environ['AZURE_SECRET']
TENANT_ID = os.environ['AZURE_TENANT']
subscription_id = os.environ['AZURE_SUBSCRIPTION_ID'] # your Azure Subscription Id
credentials = ServicePrincipalCredentials(
            client_id=CLIENT_ID,
            secret=CLIENT_SECRET,
            tenant=TENANT_ID
            )
resource_client = ResourceManagementClient(credentials, subscription_id)
storage_client = StorageManagementClient(credentials, subscription_id)
sku=Sku(name=SkuName('Standard_RAGRS'))
parameters =  StorageAccountCreateParameters(
                 sku=sku,
                 kind='Storage',
                 location='centralus')

storage_async_operation = storage_client.storage_accounts.create(
            GROUP_NAME,
            STORAGE_ACCOUNT_NAME,
            parameters
          )          
storage_account = storage_async_operation.result()
STORAGE_ACCOUNT_KEY=storage_client.storage_accounts.list_keys(GROUP_NAME,STORAGE_ACCOUNT_NAME).keys[0].value
#create container
FILE_SHARE_NAME='sapsystemshare'
TERRAFORM_DIRECTORY='sapsystem'
file_service = FileService(account_name=STORAGE_ACCOUNT_NAME, account_key=STORAGE_ACCOUNT_KEY)
file_service.create_share(FILE_SHARE_NAME)
file_service.create_directory(FILE_SHARE_NAME, TERRAFORM_DIRECTORY)
file_service.create_file_from_path(
            FILE_SHARE_NAME,
            TERRAFORM_DIRECTORY,
            'terraform.tfvars',
            tfvars_path)



MYREGSITRY='sapsystemregistry'
# create container group
aci_client = ContainerInstanceManagementClient(credentials,subscription_id)
cg_models = aci_client.container_groups.models
registry_credentials = [cg_models.ImageRegistryCredential(server='persiaregistry.azurecr.io',
                                                         username=CLIENT_ID,
                                                         password=CLIENT_SECRET)
                       ]
container_list = []
container_resource_requests = cg_models.ResourceRequests(memory_in_gb = 1, cpu = 1)
container_resource_requirements = cg_models.ResourceRequirements(requests = container_resource_requests)
CONTAINER_VOL_MOUNT='sapsystemvolumemount'
vol_mount = [cg_models.VolumeMount(name=CONTAINER_VOL_MOUNT,mount_path="/aci")]
env_vars=[
          cg_models.EnvironmentVariable(name='AZURE_SUBSCRIPTION_ID',value=subscription_id),
          cg_models.EnvironmentVariable(name='AZURE_CLIENT_ID',value=CLIENT_ID),
          cg_models.EnvironmentVariable(name='AZURE_SECRET',value=CLIENT_SECRET),
          cg_models.EnvironmentVariable(name='AZURE_TENANT',value=TENANT_ID),
          cg_models.EnvironmentVariable(name='ARM_SUBSCRIPTION_ID',value=subscription_id),
          cg_models.EnvironmentVariable(name='ARM_CLIENT_ID',value=CLIENT_ID),
          cg_models.EnvironmentVariable(name='ARM_CLIENT_SECRET',value=CLIENT_SECRET),
          cg_models.EnvironmentVariable(name='ARM_TENANT_ID',value=TENANT_ID)
         ]
container_list.append(cg_models.Container(name='sapsystem',
                                          image='persiaregistry.azurecr.io/saplandscape',
                                          resources=container_resource_requirements,
                                          volume_mounts=vol_mount,
                                          environment_variables=env_vars
                                         ))
container_vols = []

container_azure_file = cg_models.AzureFileVolume(share_name=FILE_SHARE_NAME,
                                                 storage_account_name=STORAGE_ACCOUNT_NAME, 
                                                 storage_account_key=STORAGE_ACCOUNT_KEY)
input_volume = cg_models.Volume(name=CONTAINER_VOL_MOUNT,azure_file=container_azure_file)
container_vols.append(input_volume)
#ports = [cg_models.Port(port=80, protocol="TCP")]
#Container_IpAddress = cg_models.IpAddress(ports=ports, type='public')
cg_parameters = cg_models.ContainerGroup(location='centralus',
                                         containers=container_list,
                                         image_registry_credentials=registry_credentials,
                                         restart_policy=None,
                                         os_type='linux',
                                         volumes=container_vols,

                                         )

CONTAINER_GROUP_NAME = "sapsystemcontainer_groupname"
response = aci_client.container_groups.create_or_update(resource_group_name=GROUP_NAME,
                                                        container_group_name=CONTAINER_GROUP_NAME,
                                                        container_group=cg_parameters)
print(response)

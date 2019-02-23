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

STORAGE_ACCOUNT_NAME = "persiastorage12"
GROUP_NAME = sys.argv[1]
subscription_id = os.environ['AZURE_SUBSCRIPTION_ID'] # your Azure Subscription Id
credentials = ServicePrincipalCredentials(
            client_id=os.environ['AZURE_CLIENT_ID'],
            secret=os.environ['AZURE_SECRET'],
            tenant=os.environ['AZURE_TENANT']
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
STORAGE_KEY=storage_client.storage_accounts.list_keys(GROUP_NAME,STORAGE_ACCOUNT_NAME).keys[0].value
#create container
FILE_SHARE_NAME='persiashare'
file_service = FileService(account_name=STORAGE_ACCOUNT_NAME, account_key=STORAGE_KEY)
file_service.create_share(FILE_SHARE_NAME)
file_service.create_directory(FILE_SHARE_NAME, 'persia')
file_service.create_file_from_path(
            FILE_SHARE_NAME,
            '/tmp/persia',
            'terraform.tfvars',
            '/tmp/persia/terraform.tfvars')

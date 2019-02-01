from azure.storage.blob import BlockBlobService, PublicAccess

def upload(az_blob_service, fileToUpload, blob_container_name):
    az_blob_service.create_container(blob_container_name)
    saveas  = fileToUpload.split('/')[-1]
    az_blob_service.create_blob_from_path(blob_container_name, saveas, full_path_to_file)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Process ')
    parser.add_argument('-u', "--s_account", required=True, help='storage account')
    parser.add_argument('-p', "--s_key", required=True, help='storage account key')
    parser.add_argument('-i', "--container", required=True, help='Name of the container to upload')
    parser.add_argument('-f', "--files", required=True, help='Name of the files to upload')

    args = parser.parse_args()
    az_blob_service = BlockBlobService(account_name=args.s_account, account_key=args.s_key)
    upload(az_blob_service, args.files, args.container)

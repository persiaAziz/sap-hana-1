'''
This script uploads files to the provided container in an azure blob
input: storage account, storage account key, container name, files to upload
Example:
     python AZ_blob_uploader.py -u 'YYYYYY' -p 'XXXXXX' -i container-test -f "file1" "file2"
'''
import argparse
from azure.storage.blob import BlockBlobService, PublicAccess

def upload(az_blob_service, filesToUpload, blob_container_name):
    az_blob_service.create_container(blob_container_name)
    for afile in filesToUpload:
        print("Uploading {0} to {1}".format(afile,blob_container_name))
        saveas  = afile.split('/')[-1]
        az_blob_service.create_blob_from_path(blob_container_name, afile, saveas)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Process ')
    parser.add_argument('-u', "--s_account", required=True, help='storage account')
    parser.add_argument('-p', "--s_key", required=True, help='storage account key')
    parser.add_argument('-i', "--container", required=True, help='Name of the container to upload')
    parser.add_argument('-f', "--files", required=True, type=str,  nargs='+', help='Name of the files to upload')
    args = parser.parse_args()
    try:
        az_blob_service = BlockBlobService(account_name=args.s_account, account_key=args.s_key)
        upload(az_blob_service, args.files, args.container)
    except:
        print("Couldnot upload the files to {0}. Please check you account credentials and the filepaths".format(args.container))

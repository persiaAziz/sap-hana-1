# SAP bits downloader
Script: SMP_Downloader.py

This script searches the SAP service market place by product Id and downloads the files
Input: 
    1. SAP user ID
    2. SAP user password
    3. List of package IDs to search for

# File uploader
Script: AZ_blob_uploader.py

This script uploads files to the provided container in an Azure blob
Input: storage account, storage account key, container name, files to upload
Example:
```sh
     python AZ_blob_uploader.py -u 'YYYYYY' -p 'XXXXXX' -i container-test -f "file1" "file2"
```

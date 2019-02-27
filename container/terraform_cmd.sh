#!/bin/bash

ls -l /tmp/
cat /tmp/sapsystem/terraform.tfvars

yes | ssh-keygen -b 4096 -t rsa -f /tmp/sshkey -q -N ""
git clone https://github.com/Azure/sap-hana.git
cp /tmp/sapsystem/terraform.tfvars sap-hana/deploy/vm/modules/single_node_hana/
cd sap-hana/deploy/vm/modules/single_node_hana
ls
echo "Single node deployment starting........"
terraform init -no-color
if [ $? -ne 0 ]; then
        echo "Single HANA Installation: Terraform Init failed"
        exit 1
fi

terraform apply -auto-approve -no-color 
if [ $? -ne 0 ]; then
        echo "Single HANA Installation: Terraform Apply failed"
        exit 1
fi


terraform destroy -auto-approve -no-color
if [ $? -ne 0 ]; then
        echo "Single HANA Installation: Terraform Destroy failed"
        exit 1
fi

echo "Single Instance HANA installation test succeeded"
exit 0

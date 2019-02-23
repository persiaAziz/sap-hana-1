FROM hashicorp/terraform:light

RUN apk add --update bash make ansible openssh jq py-pip gcc python python-dev musl-dev libffi-dev openssl-dev
RUN pip install --upgrade pip
RUN pip install cffi>=1.4.1
RUN pip install ansible[azure]
WORKDIR .
COPY terraform_cmd.sh terraform_cmd.sh
#COPY terraform.tfvars terraform.tfvars
#COPY terraform_ha_pair.tfvars terraform_ha_pair.tfvars

ENTRYPOINT ["/bin/sh","terraform_cmd.sh"]

resource "azurerm_container_group" "grouppersia_aciterraform" {
  name                = "grouppersia_aciterraform"
  location            = "centralus"
  resource_group_name = "persia_ACI_test"
  ip_address_type     = "public"
  dns_name_label      = "persia-aci"
  os_type             = "Linux"

  image_registry_credential {
    username = "${var.registry_user}"
    password = "${var.registry_pass}"
    server   = "persiaregistry.azurecr.io"
  }

  container {
    name   = "persiaaciterraform"
    image  = "persiaregistry.azurecr.io/suse_image"
    cpu    = "0.5"
    memory = "1.5"

    ports = {
      port     = 80
      protocol = "TCP"
    }
  }
}


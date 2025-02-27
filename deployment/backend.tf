terraform {
  backend "consul" {
    address = "consul.fluence.dev"
    scheme  = "https"
    path    = "terraform/fluence-network-exporter"
  }
}

provider "consul" {
  address    = "https://consul.fluence.dev"
  datacenter = local.region
}

provider "nomad" {
  address = "https://nomad.fluence.dev"
  region  = local.region
}

provider "vault" {
  address = "https://vault.fluence.dev"
}

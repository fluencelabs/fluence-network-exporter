locals {
  env    = terraform.workspace
  region = terraform.workspace == "mainnet" ? "kras" : terraform.workspace
}

variable "image" {
  description = "container image"
  type        = string
  default     = "fluencelabs/fluence-network-exporter:3.5.0" # x-release-please-version
}

resource "consul_keys" "configs" {
  key {
    path   = "configs/observability/fluence-network-exporter/config.yml"
    value  = file("configs/${local.env}.yml")
    delete = true
  }
}

resource "vault_policy" "fluence-network-exporter" {
  name = "${local.region}/fluence-network-exporter"

  policy = <<-EOH
    path "kv/fluence-network-exporter/${local.region}/transaction-key"
    {
      capabilities = ["read"]
    }

    path "kv/fluence-network-exporter/${local.region}/chain"
    {
      capabilities = ["read"]
    }
  EOH
}

resource "nomad_job" "fluence-network-exporter" {
  depends_on = [
    vault_policy.fluence-network-exporter,
  ]

  jobspec          = file("${path.module}/job.nomad.hcl")
  purge_on_destroy = true

  hcl2 {
    vars = {
      image  = var.image
      env    = local.env
      region = local.region
    }
  }
}

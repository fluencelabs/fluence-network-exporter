variable "env" {
  type = string
}

variable "region" {
  type = string
}

variable "image" {
  type = string
}

job "fluence-network-exporter" {
  region = var.region
  datacenters = [
    "*",
  ]
  namespace = "observability"
  node_pool = "all"

  group "fluence-network-exporter" {
    network {
      port "http" {}
    }

    service {
      name = "fluence-network-exporter"
      port = "http"

      check {
        type     = "http"
        path     = "/"
        port     = "http"
        interval = "10s"
        timeout  = "1s"
      }
    }

    task "fluence-network-exporter" {
      driver = "docker"

      vault {
        policies = [
          "${var.region}/fluence-network-exporter",
        ]
      }

      env {
        PORT                          = NOMAD_PORT_http
        CONFIG_FILE                   = "/local/config.yml"
      }

      config {
        image = var.image
        ports = [
          "http",
        ]
      }

      template {
        data        = <<-EOH
        {{ key "configs/observability/fluence-network-exporter/config.yml" }}
        EOH
        destination = "local/config.yml"
      }

      template {
        data        = <<-EOH
        {{- with secret "kv/fluence-network-exporter/${var.region}/transaction-key" -}}
        PRIVATE_KEY="{{ .Data.private_key }}"
        {{- end -}}
        EOH
        destination = "secrets/key.env"
        env         = true
      }

      resources {
        cpu        = 50
        memory     = 128
        memory_max = 256
      }
    }
  }
}

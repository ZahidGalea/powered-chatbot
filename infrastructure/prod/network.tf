## VPC CREATION
resource "google_compute_network" "vpc" {
  name                    = "${local.project_default_name_hyped}-vpc"
  auto_create_subnetworks = false
}

## SUBNET
resource "google_compute_subnetwork" "subnetwork" {
  name          = "${local.project_default_name_hyped}-${local.env}"
  region        = local.gcp_default_region
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.0.0.0/18" # 16382 IPs
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    metadata             = "INCLUDE_ALL_METADATA"
  }


  secondary_ip_range = [
    {
      # GKE for Processing
      range_name    = "${local.project_default_name_hyped}-gke"
      ip_cidr_range = "10.0.64.0/21" # Was 10.0.48.0/21
    },
        {
      # GKE for Processing
      range_name    = "${local.project_default_name_hyped}-services"
      ip_cidr_range = "10.0.72.0/21" # Was 10.0.56.0/21
    },
  ]

}

## NAT

resource "google_compute_router" "cloudnat-router" {
  name    = "cloudnat-router"
  region  = local.gcp_default_region
  network = google_compute_network.vpc.name
  bgp {
    asn = 64514
  }
}


resource "google_compute_router_nat" "nat" {
  project                            = local.gcp_project_id
  name                               = "cloudnat-config"
  router                             = google_compute_router.cloudnat-router.name
  region                             = google_compute_router.cloudnat-router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}


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

## FIREWALLS
## VM Deny everything firewall
resource "google_compute_firewall" "deny-all" {
  name      = "deny-all"
  network   = google_compute_network.vpc.name
  direction = "INGRESS"
  deny {
    protocol = "all"
  }
  target_tags   = ["acid-dataplatform-vm"]
  source_ranges = ["0.0.0.0/0"]
  priority      = 10
}
# Let the VM connect to the outside world
resource "google_compute_firewall" "egress_rule" {
  name      = "egress-traffic"
  network   = google_compute_network.vpc.name
  direction = "EGRESS"
  priority  = 9
  allow {
    protocol = "all"  # or any other ports you need
  }

  target_tags        = ["acid-dataplatform-vm"]
  destination_ranges = ["0.0.0.0/0"]
}

## Only GCP Specific IPs
resource "google_compute_firewall" "allow-iap-traffic" {
  name      = "allow-iap-traffic"
  network   = google_compute_network.vpc.name
  direction = "INGRESS"
  allow {
    protocol = "tcp"
    ports    = ["22", "80", "443", "8000"]
  }
  target_tags = ["acid-dataplatform-vm"]

  # Modificar aquí para restringir por IP
  source_ranges = ["35.235.240.0/20"]
  priority      = 9
}

resource "google_container_cluster" "default-gke" {
  name           = "${local.project_default_name_hyped}-gke"
  node_locations = [local.gcp_default_zone]
  location       = local.gcp_default_region
  project        = local.gcp_project_id
  description    = "ACID Data platform GKE"
  provider       = google-beta

  remove_default_node_pool = true
  initial_node_count       = 1
  network                  = google_compute_network.vpc.name
  subnetwork               = google_compute_subnetwork.subnetwork.name

  logging_service    = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"

  default_max_pods_per_node = 32

  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }

  ip_allocation_policy {
    cluster_secondary_range_name  = "${local.project_default_name_hyped}-gke"
    services_secondary_range_name = "${local.project_default_name_hyped}-services"
  }

  # Enable Autopilot
  enable_autopilot = true
}
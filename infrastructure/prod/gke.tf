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

}

# Separately Managed Node Pool
resource "google_container_node_pool" "acid-data-platform-gke-primary-nodes" {
  name           = "${google_container_cluster.default-gke.name}-node-pool"
  node_locations = [local.gcp_default_zone]
  location       = local.gcp_default_region
  project        = local.gcp_project_id
  cluster        = google_container_cluster.default-gke.name
  node_count     = 3


  node_config {
    disk_type    = "pd-standard"
    machine_type = "e2-standard-2"
    disk_size_gb = "100"

    service_account = google_service_account.chatbot-gke-sa.email
    oauth_scopes    = [
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/servicecontrol",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/trace.append",
    ]

    tags = ["gke-nodes"]

    resource_labels = {
      env = local.env
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }
}
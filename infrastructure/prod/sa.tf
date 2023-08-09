resource "google_service_account" "chatbot-gke-sa" {
  account_id   = "${local.project_default_name_hyped}-gke-sa"
  display_name = "Dataplatform GKE Service account"
}


module "project-iam-bindings" {
  count = 0
  source   = "terraform-google-modules/iam/google//modules/projects_iam"
  projects = [local.gcp_project_id]
  mode     = "additive"

  bindings = {
    "roles/bigquery.dataEditor" = [
      "serviceAccount:${google_service_account.chatbot-gke-sa.email}"
    ]
    "roles/secretmanager.secretAccessor" = [
      "serviceAccount:${google_service_account.chatbot-gke-sa.email}"
    ]

  }
}

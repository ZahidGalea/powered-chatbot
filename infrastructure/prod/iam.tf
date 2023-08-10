resource "google_service_account" "chatbot-gke-sa" {
  account_id   = "${local.project_default_name_hyped}-gke-sa"
  display_name = "Dataplatform GKE Service account"
}


module "project-iam-bindings" {
  source   = "terraform-google-modules/iam/google//modules/projects_iam"
  projects = [local.gcp_project_id]
  mode     = "additive"

  bindings = {
    "roles/editor" = [
      "serviceAccount:${local.compute_default_sa}",
      "serviceAccount:${google_service_account.chatbot-gke-sa.email}"
    ],
  }
}

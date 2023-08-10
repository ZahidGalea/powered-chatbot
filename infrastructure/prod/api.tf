module "project-services" {
  source  = "terraform-google-modules/project-factory/google//modules/project_services"
  version = "~> 14.2"

  project_id = local.gcp_project_id

  activate_apis = [
    "cloudresourcemanager.googleapis.com",
    "dataform.googleapis.com",
    "dataplex.googleapis.com",
    "container.googleapis.com",
    "iap.googleapis.com",
    "apikeys.googleapis.com",
    "servicemanagement.googleapis.com",
    "servicecontrol.googleapis.com",
    "endpoints.googleapis.com"
  ]
}
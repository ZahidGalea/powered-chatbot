locals {
  gcp_project_id              = "chatbot-llm-395402"
  gcp_project_number          = "823059968408"
  gcp_default_region          = "us-east1"
  gcp_default_zone            = "us-east1-b"
  project_default_name_scored = "chatbot_llm"
  project_default_name_hyped  = "chatbot-llm"
  env                         = "prod"
  compute_default_sa          = "823059968408-compute@developer.gserviceaccount.com"
}

provider "google" {
  project = local.gcp_project_id
  region  = local.gcp_default_region
}


# Backend configuration
terraform {
  backend "gcs" {
    bucket = "chatbot-llm-iac-backed-prod"
    prefix = "terraform/chatbot-llm/state"
  }
}
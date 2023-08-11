resource "google_compute_address" "esp_address" {
  name         = "chatbot-esp"
  address_type = "EXTERNAL"
  region       = local.gcp_default_region
  address      = "34.73.82.200"
}

output "esp_address" {
  value = google_compute_address.esp_address.address
}

resource "google_project_service" "endpoints_service" {
  service                    = "chatbot.endpoints.${local.gcp_project_id}.cloud.goog"
  disable_dependent_services = true
}


resource "google_endpoints_service" "chatbot_endpoint" {
  service_name   = "chatbot.endpoints.${local.gcp_project_id}.cloud.goog"
  openapi_config = file("openapi/chatbot-service.yml")
}

resource "google_endpoints_service_iam_member" "controller" {
  service_name = google_endpoints_service.chatbot_endpoint.service_name
  role         = "roles/servicemanagement.serviceController"
  member       = "serviceAccount:${google_service_account.chatbot-gke-sa.email}"
}

resource "google_endpoints_service_iam_member" "consumer" {
  service_name = google_endpoints_service.chatbot_endpoint.service_name
  role         = "roles/servicemanagement.serviceConsumer"
  member       = "serviceAccount:${google_service_account.chatbot-gke-sa.email}"
}


resource "google_apikeys_key" "dataverse" {
  name         = "dataverse-llm-endpoint"
  display_name = "dataverse-llm-endpoint"
  project      = local.gcp_project_id

  restrictions {
    api_targets {
      service = google_endpoints_service.chatbot_endpoint.service_name
      methods = ["POST*"]
    }
  }
}

output "apikey" {
  value     = google_apikeys_key.dataverse.key_string
  sensitive = true
}

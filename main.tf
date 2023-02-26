# VARIABLES
variable "deployment_id" {
    type = string
    description = "Unique ID for the deployment. Useful for managing multiple deployments"
}
variable "env" {
    type = string
    description = "Environment name. eg. dev, prod, etc."
}
variable "gcp_config" {
    type = map(string)
    description = "GCP configuration"
}
variable "google_sheet_id" {
    type = string
    description = "ID of the Google Sheet to write the email data to"
}

# PROVIDER CONFIGURATION
provider "google" {
    project = var.gcp_config["project"]
    region  = var.gcp_config["region"]
    zone    = var.gcp_config["zone"]
}
# BACKEND CONFIG
terraform {
    backend "gcs" {
        bucket = "tf-states-12698"
        prefix = "terraform/state"
    }
}

# RESOURCES
# Pub/Sub Topic
resource "google_pubsub_topic" "email_topic" {
    name = "email-topic"
}
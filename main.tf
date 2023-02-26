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
# Pub/Sub Topic to receive email updates
resource "google_pubsub_topic" "email_topic" {
    name = "${var.deployment_id}-${var.env}-topic"
}
# Build bucket for storing build artifacts
resource "google_storage_bucket" "build_bucket" {
    name = "${var.deployment_id}-${var.env}-build-bucket"
    location = var.gcp_config["region"]
    storage_class = "REGIONAL"
    force_destroy = true
}
# Build artifact for the cloud funciton
resource "google_storage_bucket_object" "build_artifact" {
    name = "processor_function.zip"
    bucket = google_storage_bucket.build_bucket.name
    source = "build/processor_function.zip"
}
# Processor cloud function
resource "google_cloudfunctions2_function" "processor_function"{
    name = "${var.deployment_id}-${var.env}-processor-function"
    description = "Function to process email data"
    build_config {
        runtime = "python310"
        entry_point = "handler"
        source {
            storage_source {
                bucket = google_storage_bucket.build_bucket.name
                object = google_storage_bucket_object.build_artifact.name
            }
        }
    }
    environment_variables = {
        GOOGLE_SHEET_ID = var.google_sheet_id
    }
}
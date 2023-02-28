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
        bucket = "terraform-92637"
        prefix = ""
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
    uniform_bucket_level_access = true
}

# Build artifact for the cloud funciton
locals {
    processor_function_build = {
        "path" = "build/processor_function.zip"
        "version_hash" = filesha256("build/processor_function.zip")
    }
}

resource "google_storage_bucket_object" "build_artifact" {
    name = "processor_function.${local.processor_function_build.version_hash}.zip"
    bucket = google_storage_bucket.build_bucket.name
    source = local.processor_function_build.path
}
# Service account for the cloud function
resource "google_service_account" "processor_svc" {
    account_id = "${var.deployment_id}-${var.env}-svc"
    display_name = "Service account for the processor function"
}
# Processor cloud function
resource "google_cloudfunctions2_function" "processor_function"{
    name = "${var.deployment_id}-${var.env}-processor-function"
    description = "Function to process email data"
    location = var.gcp_config["region"]
    build_config {
        runtime = "python310"
        entry_point = "handler"
        source {
            storage_source {
                bucket = google_storage_bucket.build_bucket.name
                object = google_storage_bucket_object.build_artifact.name
            }
        }
        environment_variables = {
            GOOGLE_SHEET_ID = var.google_sheet_id
        }
    }
    service_config {
      available_memory = "256M"
      timeout_seconds = 30
      service_account_email = google_service_account.processor_svc.email
    }
    event_trigger {
        event_type = "google.cloud.pubsub.topic.v1.messagePublished"
        pubsub_topic = google_pubsub_topic.email_topic.id
        retry_policy = "RETRY_POLICY_RETRY"
    }     
}
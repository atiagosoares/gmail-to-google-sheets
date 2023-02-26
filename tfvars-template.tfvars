# Template for the .tfvars files
# Create a copy of this file and name it terraform.tfvars, then fill in the values with your own

# The terraform.tfvars file is ignored by git, so you can safely put your secrets in there

deployment_id = "my-deployment" # Unique name for this deployment. Useful to manage multiple deployments
env = "my-env" # Environment name. e.g. dev, test, prod

gcp_config = {
  project = "my-project" # GCP project ID
  region     = "us-central1" # GCP region
  zone       = "us-central1-a" # GCP zone
}
tf_state_bucket = "value" # GCS bucket name for storing terraform state

google_sheet_id = "value" # ID of the Google Sheet that emails will be written to
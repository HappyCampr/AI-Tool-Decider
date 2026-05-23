variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "image" {
  type        = string
  description = "Artifact Registry image URI for the Cloud Run service."
}

variable "service_name" {
  type    = string
  default = "ai-tool-decider"
}

variable "allow_unauthenticated" {
  type    = bool
  default = true
}

variable "container_port" {
  type    = number
  default = 8080
}

variable "timeout" {
  type    = string
  default = "300s"
}

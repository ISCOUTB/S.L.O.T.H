variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "environment must be either 'development', 'staging' or 'production'."
  }
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "etl-design"
}

variable "availability_zones" {
  description = "List of availability zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}

# ============================ Swarm variables ============================

variable "manager_count" {
  description = "Number of manager nodes in the Swarm (preferably odd: 1, 3, 5)"
  type        = number
  default     = 1

  validation {
    condition     = var.manager_count > 0 && var.manager_count % 2 == 1
    error_message = "manager_count must be greater than 0 and an odd number."
  }
}

variable "worker_count" {
  description = "Number of worker nodes in the Swarm"
  type        = number
  default     = 2

  validation {
    condition     = var.worker_count >= 0
    error_message = "worker_count must be greater than or equal to 0."
  }
}

variable "allowed_ssh_cidr" {
  description = "CIDR allowed for SSH access (example: your_public_ip/32)"
  type        = list(string)
  default     = ["0.0.0.0/0"]

  validation {
    condition = alltrue([
      for cidr in var.allowed_ssh_cidr :
      can(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}/[0-9]{1,2}$", cidr))
    ])
    error_message = "Must be a valid CIDR (e.g. 192.168.1.1/32)"
  }
}

variable "instance_type" {
  description = "EC2 instance type to deploy nodes"
  type        = string
  default     = "t3.micro"
}

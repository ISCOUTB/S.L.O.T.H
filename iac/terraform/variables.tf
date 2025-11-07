variable "manager_count" {
  description = "Number of manager nodes in the Swarm (preferably odd: 1, 3, 5)"
  type        = number
  default     = 1

  validation {
    condition     = var.manager_count > 0
    error_message = "manager_count must be greater than 0."
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
  type        = string
  default     = "0.0.0.0/0"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
} # VPC
resource "aws_vpc" "swarm" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "swarm-vpc"
  }
}

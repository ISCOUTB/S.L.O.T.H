# ============================================
# VPC Outputs
# ============================================

output "vpc_id" {
  description = "ID of the VPC created"
  value       = aws_vpc.swarm.id
}

output "subnet_ids" {
  description = "IDs of the subnets created"
  value       = aws_subnet.swarm[*].id
}

# ============================================
# EC2 Instance Outputs
# ============================================

output "manager_ips" {
  description = "Public and Private IPs of Manager nodes"
  value = {
    for idx, instance in aws_instance.managers :
    "manager-${idx + 1}" => {
      public_ip  = instance.public_ip
      private_ip = instance.private_ip
    }
  }
}

output "manager_public_ips" {
  description = "Public IPs of all manager nodes"
  value = aws_instance.managers[*].public_ip
}

output "manager_private_ips" {
  description = "Private IPs of all manager nodes"
  value       = aws_instance.managers[*].private_ip
}

output "lead_manager_ip" {
  description = "Public IP of the lead manager node"
  value       = length(aws_instance.managers) > 0 ? aws_instance.managers[0].public_ip : null
}

output "swarm_manager_ip" {
  description = "Public IP of the first manager (primary)"
  value       = aws_instance.managers[0].public_ip
}

output "worker_ips" {
  description = "Public and Private IPs of Worker nodes"
  value = {
    for idx, instance in aws_instance.workers :
    "worker-${idx + 1}" => {
      public_ip  = instance.public_ip
      private_ip = instance.private_ip
    }
  }
}

output "worker_public_ips" {
  description = "Public IPs of all worker nodes"
  value = aws_instance.workers[*].public_ip
}

output "worker_private_ips" {
  description = "Private IPs of all worker nodes"
  value       = aws_instance.workers[*].private_ip
}

# ============================================
# SSH & Inventory Outputs
# ============================================

output "ansible_inventory" {
  description = "Path to the generated Ansible inventory file"
  value       = local_file.ansible_inventory.filename
}

output "ssh_key_path" {
  description = "Path to SSH private key"
  value       = local_sensitive_file.ssh_key_pem.filename
  sensitive   = true
}

# ============================================
# Security & Network Outputs
# ============================================

output "security_group_id" {
  description = "Security Group ID"
  value       = aws_security_group.swarm.id
}

# ============================================
# Cluster Metadata
# ============================================

output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "cluster_name" {
  description = "Full cluster name"
  value       = local.cluster_name
}

output "region" {
  description = "AWS region where resources are deployed"
  value       = data.aws_region.current.region
}

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

output "swarm_manager_ip" {
  description = "Public IP of the first manager (primary)"
  value       = aws_instance.managers[0].public_ip
}

output "swarm_vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.swarm.id
}

output "swarm_subnet_id" {
  description = "Subnet ID"
  value       = aws_subnet.public.id
}

output "security_group_id" {
  description = "Security Group ID"
  value       = aws_security_group.swarm_sg.id
}

output "ssh_key_path" {
  description = "Path to SSH private key"
  value       = local_sensitive_file.ssh_key_pem.filename
  sensitive   = true
}

output "cluster_info" {
  description = "Cluster information"
  value = {
    environment  = module.swarm_test.environment
    cluster_name = module.swarm_test.cluster_name
    vpc_id       = module.swarm_test.vpc_id
    region       = module.swarm_test.region
  }
}

output "manager_ips" {
  description = "Manager node public IPs"
  value       = module.swarm_test.manager_ips
}

output "worker_ips" {
  description = "Worker node public IPs"
  value       = module.swarm_test.worker_ips
}

output "ssh_key_path" {
  description = "Path to SSH private key"
  value       = module.swarm_test.ssh_key_path
  sensitive   = true
}

output "ansible_inventory" {
  description = "Path to Ansible inventory"
  value       = module.swarm_test.ansible_inventory
}

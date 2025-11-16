# ============================================
# Module Invocation
# ============================================

module "swarm_test" {
  source = "../../module/swarm-cluster"

  environment        = var.environment
  project_name       = var.project_name
  manager_count      = var.manager_count
  worker_count       = var.worker_count
  instance_type      = var.instance_type
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  allowed_ssh_cidr   = var.allowed_ssh_cidr
  tags               = var.tags
}

# ============================================
# Ansible Provisioning
# ============================================

# Provision Docker on all nodes
resource "null_resource" "ansible_provision_docker" {
  depends_on = [
    module.swarm_test
  ]

  triggers = {
    # Re-run if manager IPs change
    manager_ips = join(",", module.swarm_test.manager_public_ips)
    worker_ips  = join(",", module.swarm_test.worker_public_ips)
    # Re-run if instance count changes
    instance_count = "${var.manager_count}-${var.worker_count}"
  }

  provisioner "local-exec" {
    working_dir = "${path.root}/../../.."
    command     = <<-EOT
      echo "Waiting 60 seconds for instances to be ready..."
      sleep 60
      echo "Installing Docker on all nodes..."
      ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook \
        -i ${module.swarm_test.ansible_inventory} \
        ansible/docker.yml
    EOT
  }

  provisioner "local-exec" {
    when    = destroy
    command = "echo 'Docker provisioner cleanup (if needed)'"
  }
}

# Initialize Docker Swarm cluster
resource "null_resource" "ansible_init_swarm" {
  depends_on = [
    null_resource.ansible_provision_docker
  ]

  triggers = {
    # Re-run if manager IPs change (swarm needs re-init)
    manager_ips = join(",", module.swarm_test.manager_public_ips)
  }

  provisioner "local-exec" {
    working_dir = "${path.root}/../../.."
    command     = <<-EOT
      echo "Initializing Docker Swarm cluster..."
      ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook \
        -i ${module.swarm_test.ansible_inventory} \
        ansible/swarm-init.yml
    EOT
  }

  provisioner "local-exec" {
    when    = destroy
    command = "echo 'Swarm cleanup (nodes will be destroyed)'"
  }
}

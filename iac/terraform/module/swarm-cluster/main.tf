# ============================================
# Module: Docker Swarm Cluster
# ============================================

# ============================================
# Locals
# ============================================

locals {
  common_tags = merge(
    {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    },
    var.tags
  )

  cluster_name = "${var.project_name}-${var.environment}"
}

# ============================================
# VPC and Networking
# ============================================

resource "aws_vpc" "swarm" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.cluster_name}-vpc"
    }
  )
}

# Internet Gateway
resource "aws_internet_gateway" "swarm" {
  vpc_id = aws_vpc.swarm.id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.cluster_name}-igw"
    }
  )
}

# Public subnet
resource "aws_subnet" "swarm" {
  count = length(var.availability_zones)

  vpc_id                  = aws_vpc.swarm.id
  cidr_block              = cidrsubnet(aws_vpc.swarm.cidr_block, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.cluster_name}-subnet-${count.index + 1}"
    }
  )
}

# Public route table
resource "aws_route_table" "swarm" {
  vpc_id = aws_vpc.swarm.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.swarm.id
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.cluster_name}-rt"
    }
  )
}

# Associate subnet to route table
resource "aws_route_table_association" "swarm" {
  count = length(aws_subnet.swarm)

  subnet_id      = aws_subnet.swarm[count.index].id
  route_table_id = aws_route_table.swarm.id
}

# ============================================
# Security Group
# ============================================

# Security Group for Docker Swarm
resource "aws_security_group" "swarm" {
  name        = "${local.cluster_name}-sg"
  description = "Security group for Docker Swarm cluster - ${var.environment}"
  vpc_id      = aws_vpc.swarm.id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.cluster_name}-sg"
    }
  )

  # SSH only from specified IP
  ingress {
    description = "SSH from allowed CIDR"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  # Docker Swarm communication (inside VPC)
  ingress {
    description = "Docker Swarm manager"
    from_port   = 2377
    to_port     = 2377
    protocol    = "tcp"
    self        = true
  }

  # Docker Swarm: node communication (TCP)
  ingress {
    description = "Docker Swarm gossip TCP"
    from_port   = 7946
    to_port     = 7946
    protocol    = "tcp"
    self        = true
  }

  # Docker Swarm: node communication (UDP)
  ingress {
    description = "Docker Swarm gossip UDP"
    from_port   = 7946
    to_port     = 7946
    protocol    = "udp"
    self        = true
  }

  # Docker Swarm: overlay network
  ingress {
    description = "Docker overlay network"
    from_port   = 4789
    to_port     = 4789
    protocol    = "udp"
    self        = true
  }

  # HTTP for published services
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS for published services
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Custom application port"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ============================================
# SSH Key Pair
# ============================================

# SSH Key
resource "tls_private_key" "swarm" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "swarm_key" {
  key_name   = "${local.cluster_name}-key"
  public_key = tls_private_key.swarm.public_key_openssh

  tags = local.common_tags
}

# Save private key to file
resource "local_sensitive_file" "ssh_key_pem" {
  filename        = abspath("${path.root}/ssh-keys/${var.environment}-swarm-key.pem")
  content         = tls_private_key.swarm.private_key_pem
  file_permission = "0600"
}

# ============================================
# EC2 Instances
# ============================================

# MANAGER instances
resource "aws_instance" "managers" {
  count = var.manager_count

  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = aws_key_pair.swarm_key.key_name

  subnet_id              = aws_subnet.swarm[count.index % length(aws_subnet.swarm)].id
  vpc_security_group_ids = [aws_security_group.swarm.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name

  associate_public_ip_address = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.cluster_name}-${count.index + 1}"
      Role = "manager"
    }
  )

  root_block_device {
    volume_size = 30
    volume_type = "gp3"

    tags = merge(
      local.common_tags,
      {
        Name = "${local.cluster_name}-manager-${count.index + 1}-root"
      }
    )
  }

  depends_on = [aws_internet_gateway.swarm]
}

# WORKER instances
resource "aws_instance" "workers" {
  count = var.worker_count

  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = aws_key_pair.swarm_key.key_name

  subnet_id              = aws_subnet.swarm[count.index % length(aws_subnet.swarm)].id
  vpc_security_group_ids = [aws_security_group.swarm.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name

  associate_public_ip_address = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.cluster_name}-worker-${count.index + 1}"
      Role = "worker"
    }
  )

  root_block_device {
    volume_size = 30
    volume_type = "gp3"

    tags = merge(
      local.common_tags,
      {
        Name = "${local.cluster_name}-worker-${count.index + 1}-root"
      }
    )
  }

  depends_on = [aws_internet_gateway.swarm]

}

# IAM Role for EC2 (required for SSM, logs, etc.)
resource "aws_iam_role" "ec2_role" {
  name = "${local.cluster_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "ssm_policy" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${local.cluster_name}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# ============================================
# Ansible Inventory Generation
# ============================================

# Generate dynamic inventory for Ansible
resource "local_file" "ansible_inventory" {
  content = templatefile("${path.module}/templates/inventory.tpl", {
    managers     = aws_instance.managers
    workers      = aws_instance.workers
    ssh_key_file = local_sensitive_file.ssh_key_pem.filename
    ssh_user     = "ubuntu"
    environment  = var.environment
  })

  filename        = abspath("${path.root}/inventories/${var.environment}-inventory.ini")
  file_permission = "0644"
}

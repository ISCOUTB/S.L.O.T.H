# Public subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.swarm.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "swarm-public-subnet"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "swarm" {
  vpc_id = aws_vpc.swarm.id

  tags = {
    Name = "swarm-igw"
  }
}

# Public route table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.swarm.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.swarm.id
  }

  tags = {
    Name = "swarm-public-rt"
  }
}

# Associate subnet to route table
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Security Group for Docker Swarm
resource "aws_security_group" "swarm_sg" {
  name        = "docker-swarm-sg"
  description = "Security group for Docker Swarm cluster"
  vpc_id      = aws_vpc.swarm.id

  tags = {
    Name = "Docker-Swarm-SG"
  }

  # SSH only from specified IP
  ingress {
    description = "SSH from allowed CIDR"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  # Docker Swarm: API de management (solo intra-cluster)
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

  # Allow all outbound traffic
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# SSH Key
resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "aws_key_pair" "swarm_key" {
  key_name   = "swarm-key"
  public_key = tls_private_key.ssh_key.public_key_openssh

  tags = {
    Name = "Swarm SSH Key"
  }
}

# Save private key to file
resource "local_sensitive_file" "ssh_key_pem" {
  filename        = "${path.module}/../keys/swarm-key.pem"
  content         = tls_private_key.ssh_key.private_key_pem
  file_permission = "0600"
}

# MANAGER instances
resource "aws_instance" "managers" {
  count                  = var.manager_count
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.swarm_key.key_name
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.swarm_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name

  associate_public_ip_address = true

  tags = {
    Name = "swarm-manager-${count.index + 1}"
    Role = "manager"
  }

  depends_on = [aws_internet_gateway.swarm]
}

# WORKER instances
resource "aws_instance" "workers" {
  count                  = var.worker_count
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.swarm_key.key_name
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.swarm_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name

  associate_public_ip_address = true

  tags = {
    Name = "swarm-worker-${count.index + 1}"
    Role = "worker"
  }

  depends_on = [aws_internet_gateway.swarm]
}

# IAM Role for EC2 (required for SSM, logs, etc.)
resource "aws_iam_role" "ec2_role" {
  name = "swarm-ec2-role"

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
}

resource "aws_iam_role_policy_attachment" "ssm_policy" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "swarm-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# Generate dynamic inventory for Ansible
resource "local_file" "ansible_inventory" {
  filename = "${path.module}/../ansible/inventory.ini"
  content = templatefile("${path.module}/inventory.tpl", {
    managers = aws_instance.managers
    workers  = aws_instance.workers
  })

  depends_on = [
    aws_instance.managers,
    aws_instance.workers
  ]
}

# Provision with Ansible
resource "null_resource" "ansible_provision" {
  depends_on = [
    local_file.ansible_inventory,
    local_sensitive_file.ssh_key_pem
  ]

  triggers = {
    inventory = local_file.ansible_inventory.content
  }

  provisioner "local-exec" {
    working_dir = "${path.module}/.."
    command     = "sleep 30 && ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i ./ansible/inventory.ini --private-key ./keys/swarm-key.pem ./ansible/docker.yml"
  }
}

# Initialize Docker Swarm
resource "null_resource" "swarm_init" {
  depends_on = [null_resource.ansible_provision]

  provisioner "local-exec" {
    working_dir = "${path.module}/.."
    command     = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i ./ansible/inventory.ini --private-key ./keys/swarm-key.pem ./ansible/swarm-init.yml"
  }
}

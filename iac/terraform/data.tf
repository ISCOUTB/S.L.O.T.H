# Data source to get the latest Ubuntu 24.04 AMI
data "aws_ami" "ubuntu" {
  owners      = ["099720109477"]
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}

# Data source to get available AZs
data "aws_availability_zones" "available" {
  state = "available"
}

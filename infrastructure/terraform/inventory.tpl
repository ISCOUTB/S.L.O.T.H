[managers]
%{ for idx, manager in managers ~}
manager-${idx + 1} ansible_host=${manager.public_ip} ansible_user=ubuntu private_ip=${manager.private_ip}
%{ endfor ~}

[workers]
%{ for idx, worker in workers ~}
worker-${idx + 1} ansible_host=${worker.public_ip} ansible_user=ubuntu private_ip=${worker.private_ip}
%{ endfor ~}

[swarm:children]
managers
workers

[all:vars]
ansible_python_interpreter=/usr/bin/python3
ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'

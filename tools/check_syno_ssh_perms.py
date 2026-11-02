import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.1.100', 22, os.environ.get("ADMIN_USER", "admin"), os.environ.get("ADMIN_PASS", ""))
stdin, stdout, stderr = client.exec_command('ls -ld /var/services/homes /var/services/homes/admin ~/.ssh ~/.ssh/authorized_keys')
print(stdout.read().decode())
stdin, stdout, stderr = client.exec_command('grep -E "Pubkey|AuthorizedKeys" /etc/ssh/sshd_config')
print(stdout.read().decode())
client.close()

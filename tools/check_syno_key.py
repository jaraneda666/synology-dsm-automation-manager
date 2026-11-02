import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.1.100', 22, os.environ.get("ADMIN_USER", "admin"), os.environ.get("ADMIN_PASS", ""))
stdin, stdout, stderr = client.exec_command('ls -la ~/.ssh/ 2>/dev/null; cat ~/.ssh/authorized_keys 2>/dev/null')
print(stdout.read().decode())
client.close()

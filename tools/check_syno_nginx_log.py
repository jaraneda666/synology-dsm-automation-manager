import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.1.100', 22, os.environ.get("ADMIN_USER", "admin"), os.environ.get("ADMIN_PASS", ""))

stdin, stdout, stderr = client.exec_command("find /var/log/nginx/ -type f -exec tail -n 5 {} +")
print(stdout.read().decode())
client.close()

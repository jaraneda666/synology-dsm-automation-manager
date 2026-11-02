import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.1.100', 22, os.environ.get("ADMIN_USER", "admin"), os.environ.get("ADMIN_PASS", ""))

cmd1 = 'curl -k -s -I https://localhost/ -H "Host: portainer.admin.synology.me"'
stdin, stdout, stderr = client.exec_command(cmd1)
print("=== FROM LOCALHOST ===\n" + stdout.read().decode())

cmd2 = 'curl -k -s -I https://192.168.1.100/ -H "Host: portainer.admin.synology.me"'
stdin, stdout, stderr = client.exec_command(cmd2)
print("=== FROM LAN ===\n" + stdout.read().decode())

cmd3 = 'curl -k -s -I https://192.168.1.100/ -H "Host: router.admin.synology.me"'
stdin, stdout, stderr = client.exec_command(cmd3)
print("=== ROUTER FROM LAN ===\n" + stdout.read().decode())

client.close()

import paramiko

target = "192.168.1.100"
user = os.environ.get("ADMIN_USER", "admin")
pwd = os.environ.get("ADMIN_PASS", "")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(target, 22, user, pwd, timeout=10)

stdin, stdout, stderr = client.exec_command("cat /usr/syno/etc/www/AccessControl.json 2>/dev/null")
print("=== AccessControl.json ===")
print(stdout.read().decode())

stdin, stdout, stderr = client.exec_command("grep -E '\"fqdn\"|\"access_control\"' /usr/syno/etc/www/ReverseProxy.json 2>/dev/null")
print("=== ReverseProxy Access Controls ===")
print(stdout.read().decode())

client.close()

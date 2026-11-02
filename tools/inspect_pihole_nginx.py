import paramiko

target = "192.168.1.100"
user = os.environ.get("ADMIN_USER", "admin")
pwd = os.environ.get("ADMIN_PASS", "")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(target, 22, user, pwd, timeout=10)

stdin, stdout, stderr = client.exec_command("cat /etc/nginx/sites-enabled/server.ReverseProxy.conf")
content = stdout.read().decode('utf-8', errors='replace')
for block in content.split("server {"):
    if "pihole.admin.synology.me" in block:
        print("=== PIHOLE NGINX SERVER BLOCK ===")
        print("server {" + block)

client.close()

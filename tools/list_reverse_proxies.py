import paramiko
import re

target = "192.168.1.100"
user = os.environ.get("ADMIN_USER", "admin")
pwd = os.environ.get("ADMIN_PASS", "")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(target, 22, user, pwd, timeout=10)

stdin, stdout, stderr = client.exec_command("cat /etc/nginx/sites-enabled/server.ReverseProxy.conf")
content = stdout.read().decode('utf-8', errors='replace')

servers = content.split("server {")
print(f"Total Reverse Proxy configs: {len(servers)-1}")
for s in servers[1:]:
    name = re.search(r"server_name\s+([^;]+);", s)
    proxy = re.search(r"proxy_pass\s+([^;]+);", s)
    hsts = "HSTS" if "Strict-Transport-Security" in s else "No-HSTS"
    domain = name.group(1).strip() if name else "Unknown"
    target_url = proxy.group(1).strip() if proxy else "Unknown"
    print(f"- {domain:35} -> {target_url:30} [{hsts}]")

client.close()

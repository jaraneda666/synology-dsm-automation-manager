import paramiko
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.1.100', 22, os.environ.get("ADMIN_USER", "admin"), os.environ.get("ADMIN_PASS", ""))

stdin, stdout, stderr = client.exec_command('cat /usr/syno/etc/www/AccessControl.json')
print("=== AccessControl.json ===")
print(stdout.read().decode())

stdin, stdout, stderr = client.exec_command('cat /usr/syno/etc/www/ReverseProxy.json')
rp = json.loads(stdout.read().decode())
print("=== ReverseProxy.json Status ===")
for k, v in rp.items():
    if isinstance(v, dict):
        desc = v.get("description", "")
        fqdn = v.get("frontend", {}).get("fqdn", "")
        acl = v.get("frontend", {}).get("acl", None)
        print(f"- {desc:15} | {fqdn:32} | ACL: {acl}")

stdin, stdout, stderr = client.exec_command("grep -E 'server_name|include.*acl' /etc/nginx/sites-enabled/server.ReverseProxy.conf")
print("\n=== NGINX SITES ENABLED ACL INCLUDES ===")
print(stdout.read().decode())

client.close()

import paramiko
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.1.100', 22, os.environ.get("ADMIN_USER", "admin"), os.environ.get("ADMIN_PASS", ""))
stdin, stdout, stderr = client.exec_command('cat /usr/syno/etc/www/ReverseProxy.json')
rp = json.loads(stdout.read().decode())
for k, v in rp.items():
    desc = v.get('description', 'Sin desc')
    fqdn = v.get('frontend', {}).get('fqdn', 'Sin fqdn')
    acl = v.get('frontend', {}).get('acl', None)
    backend = f"{v.get('backend', {}).get('fqdn')}:{v.get('backend', {}).get('port')}"
    print(f"{k} | {desc:25} | {fqdn:32} | {backend:22} | ACL: {acl}")
client.close()

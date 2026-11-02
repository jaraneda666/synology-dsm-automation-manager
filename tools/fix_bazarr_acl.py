import json
import paramiko

target = "192.168.1.100"
user = os.environ.get("ADMIN_USER", "admin")
pwd = os.environ.get("ADMIN_PASS", "")
acl_id = "daf80561-c4c6-4b03-8bcc-191d9e9fc374"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(target, 22, user, pwd, timeout=10)

def run_sudo(cmd):
    stdin, stdout, stderr = client.exec_command(f"echo {pwd} | sudo -S {cmd}")
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    return code, out

def write_remote_file(remote_path, content_bytes):
    stdin, stdout, stderr = client.exec_command(f"cat > {remote_path}")
    stdin.write(content_bytes)
    stdin.channel.shutdown_write()
    code = stdout.channel.recv_exit_status()
    return code

_, rp_orig = run_sudo("cat /usr/syno/etc/www/ReverseProxy.json")
rp_data = json.loads(rp_orig)

for k, v in rp_data.items():
    if isinstance(v, dict) and v.get("description") == "Bazarr":
        v["frontend"]["acl"] = acl_id
        print("ACL assigned to Bazarr!")

write_remote_file("/tmp/ReverseProxy.json.new", json.dumps(rp_data, indent=4).encode('utf-8'))
run_sudo("cp /tmp/ReverseProxy.json.new /usr/syno/etc/www/ReverseProxy.json && chmod 644 /usr/syno/etc/www/ReverseProxy.json")
run_sudo("/usr/syno/bin/synow3tool --gen-all")
c, out = run_sudo("nginx -t")
print(f"nginx -t: {c}")
if c == 0:
    run_sudo("/usr/syno/bin/synow3tool --deploy-hup")
    print("synow3tool deployed successfully!")

_, out = run_sudo("grep -A 1 'bazarr.admin.synology.me' /etc/nginx/sites-enabled/server.ReverseProxy.conf")
print("Bazarr config in Nginx:")
print(out)

client.close()

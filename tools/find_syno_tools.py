import paramiko

target = "192.168.1.100"
user = os.environ.get("ADMIN_USER", "admin")
pwd = os.environ.get("ADMIN_PASS", "")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(target, 22, user, pwd, timeout=10)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(f"echo {pwd} | sudo -S {cmd}")
    return stdout.read().decode().strip()

print("=== TOOLS ===")
print(run("find /usr/syno/bin /usr/syno/sbin -name '*nginx*' -o -name '*w3*' 2>/dev/null"))

print("\n=== SYSTEMCTL NGINX ===")
print(run("synosystemctl --help 2>/dev/null || systemctl status nginx 2>/dev/null"))

client.close()

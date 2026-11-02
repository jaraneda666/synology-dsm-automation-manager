import paramiko

target = "192.168.1.100"
user = os.environ.get("ADMIN_USER", "admin")
pwd = os.environ.get("ADMIN_PASS", "")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(target, 22, user, pwd, timeout=10)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(f"echo {pwd} | sudo -S {cmd}")
    return stdout.read().decode('utf-8', errors='replace').strip()

print("=== ADMIN STATUS ===")
print(run("/usr/syno/sbin/synouser --get admin"))

print("\n=== FIREWALL IPTABLES INPUT ===")
print(run("iptables -L INPUT -n -v"))

print("\n=== REVERSE PROXY CONFIGS ===")
print(run("cat /etc/nginx/sites-enabled/server.ReverseProxy.conf 2>/dev/null"))

print("\n=== TCP LISTENING PORTS ===")
print(run("netstat -tulnp | grep -E 'LISTEN' | awk '{print $1, $4, $7}'"))

print("\n=== SECURITY ADVISOR LAST SCAN ===")
print(run("tail -n 30 /var/log/synolog/synosys.log | grep -i security 2>/dev/null || echo 'No security log'"))

client.close()

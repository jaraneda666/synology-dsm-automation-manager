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

print("--- TCP LISTENERS ---")
print(run("netstat -tlpn | grep LISTEN"))

print("\n--- SYNOLOGY FIREWALL (iptables rules) ---")
print(run("iptables -L INPUT -n -v"))

print("\n--- USERS (admin, guest, admin) ---")
print(run("/usr/syno/sbin/synouser --get admin 2>&1"))
print(run("/usr/syno/sbin/synouser --get guest 2>&1"))
print(run("/usr/syno/sbin/synouser --get admin 2>&1"))

print("\n--- DSM PORTAL & SECURITY SETTINGS ---")
print(run("grep -E 'runman|https|port|admin|autoblock|dos' /etc/synoinfo.conf"))

print("\n--- NGINX SITES / REVERSE PROXY ---")
print(run("ls -la /usr/syno/etc/www/ /usr/syno/etc/www/app.d/ 2>/dev/null; ls -la /etc/nginx/sites-enabled/ 2>/dev/null"))

print("\n--- DOCKER / CONTAINER MANAGER ---")
print(run("docker ps --format '{{.Names}} - {{.Image}} - {{.Ports}}' 2>/dev/null || /usr/local/bin/docker ps 2>/dev/null || echo 'No docker binary'"))

client.close()

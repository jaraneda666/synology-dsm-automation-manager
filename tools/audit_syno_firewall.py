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

queries = [
    ("FIREWALL_FILES", "find /usr/syno/etc/ -name '*firewall*' 2>/dev/null"),
    ("FIREWALL_STATUS", "synogetkeyvalue /etc/synoinfo.conf run_firewall 2>/dev/null; synogetkeyvalue /etc/synoinfo.conf enable_firewall 2>/dev/null"),
    ("AUTOBLOCK_STATUS", "synogetkeyvalue /etc/synoinfo.conf autoblock_enable 2>/dev/null; cat /etc/synoautoblock.conf 2>/dev/null || cat /usr/syno/etc/synoautoblock.conf 2>/dev/null"),
    ("AUTOBLOCK_BLOCKED_COUNT", "wc -l /etc/synoautoblock.db 2>/dev/null || sqlite3 /etc/synoautoblock.db 'SELECT count(*) FROM AutoBlockIP;' 2>/dev/null"),
    ("CERTIFICATES", "cat /usr/syno/etc/certificate/_archive/DEFAULT 2>/dev/null; ls -la /usr/syno/etc/certificate/_archive/ 2>/dev/null"),
    ("DSM_PORTS", "synogetkeyvalue /etc/synoinfo.conf runmanhttp 2>/dev/null; synogetkeyvalue /etc/synoinfo.conf runmanhttps 2>/dev/null; synogetkeyvalue /etc/synoinfo.conf redirect_http_to_https 2>/dev/null"),
    ("ACCOUNT_PASSWORDS", "cat /etc/shadow | grep -E '^admin:|^admin:|^guest:'"),
    ("ACTIVE_DOCKER_CONTAINERS", "/var/packages/ContainerManager/target/usr/bin/docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || /var/packages/Docker/target/usr/bin/docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null"),
]

for title, cmd in queries:
    print(f"=== {title} ===")
    print(run(cmd))
    print()

client.close()

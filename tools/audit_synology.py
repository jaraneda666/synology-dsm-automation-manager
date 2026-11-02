import paramiko
import sys

target = "192.168.1.100"
user = os.environ.get("ADMIN_USER", "admin")
pwd = os.environ.get("ADMIN_PASS", "")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(target, 22, user, pwd, timeout=10)
    
    def run_sudo(cmd):
        stdin, stdout, stderr = client.exec_command(f"echo {pwd} | sudo -S {cmd}")
        return stdout.read().decode('utf-8', errors='replace').strip()

    commands = [
        ("PORTS_AND_SERVICES", "netstat -tulnp"),
        ("DOCKER_CONTAINERS", "docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || echo 'Docker no disponible'"),
        ("SYNOLOGY_FIREWALL", "iptables -S INPUT 2>/dev/null"),
        ("AUTOBLOCK_SETTINGS", "grep -E 'autoblock' /etc/synoinfo.conf 2>/dev/null"),
        ("USER_ADMIN_STATUS", "synouser --get admin 2>/dev/null; echo '--- GUEST ---'; synouser --get guest 2>/dev/null"),
        ("OTP_2FA_SETTINGS", "grep -E 'otp' /etc/synoinfo.conf 2>/dev/null"),
        ("HTTP_HTTPS_SETTINGS", "grep -E 'runmanhttp|runmanhttps|redirect_http_to_https|tls_version|hsts' /etc/synoinfo.conf 2>/dev/null"),
        ("QUICKCONNECT_EZINTERNET", "grep -E 'quickconnect|router_conf' /etc/synoinfo.conf 2>/dev/null"),
        ("SSHD_CONFIG", "grep -E -v '^#|^$' /etc/ssh/sshd_config"),
        ("REVERSE_PROXY_CONF", "ls -la /etc/nginx/app.d/ 2>/dev/null; cat /etc/nginx/app.d/server.ReverseProxy.conf 2>/dev/null || echo 'Sin reverse proxy configurado'"),
    ]

    for title, cmd in commands:
        print(f"=== {title} ===")
        out = run_sudo(cmd)
        print(out)
        print()

except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()

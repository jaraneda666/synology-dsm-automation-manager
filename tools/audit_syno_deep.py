import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.100", 22, os.environ.get("ADMIN_USER", "admin"), os.environ.get("ADMIN_PASS", ""), timeout=10)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(f"echo '{os.environ.get('ADMIN_PASS', '')}' | sudo -S {cmd}")
    return stdout.read().decode('utf-8', errors='replace').strip()

print("=== IPTABLES FILTER RULES ===")
print(run("iptables -L -n -v --line-numbers"))

print("\n=== FIREWALL FILES & CONFIGS ===")
print(run("cat /usr/syno/etc/firewall.d/firewall_settings.json 2>/dev/null"))
print("---")
print(run("cat /usr/syno/etc/user.data.conf/firewall.config 2>/dev/null"))
print("---")
print(run("ls -la /etc/firewall* /usr/syno/etc/firewall* 2>/dev/null"))

print("\n=== DOCKER NETWORKS & PORTS ===")
print(run("docker network ls"))
print(run("docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Networks}}'"))

print("\n=== LISTENING PORTS ON SYNOLOGY ===")
print(run("netstat -tulnp | grep -v '127.0.0.1' | grep LISTEN"))

client.close()

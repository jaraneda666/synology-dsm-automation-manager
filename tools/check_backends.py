import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.1.100', 22, os.environ.get("ADMIN_USER", "admin"), os.environ.get("ADMIN_PASS", ""))

for p, name in [(9000, "Portainer"), (8444, "PiHole"), (8182, "Sshwifty"), (8096, "Jellyfin")]:
    stdin, stdout, stderr = client.exec_command(f"curl -s -I http://localhost:{p}/ | head -n 3")
    print(f"=== {name} (port {p}) ===")
    print(stdout.read().decode())

client.close()

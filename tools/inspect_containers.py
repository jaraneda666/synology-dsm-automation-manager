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

print("=== SSHWIFTY INSPECT ===")
print(run("/var/packages/ContainerManager/target/usr/bin/docker inspect sshwifty_web | grep -A 20 '\"Env\"'"))

print("\n=== PORTAINER INSPECT ===")
print(run("/var/packages/ContainerManager/target/usr/bin/docker inspect portainer | grep -A 10 '\"Env\"'"))

client.close()

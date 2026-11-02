import paramiko

target = "192.168.1.100"
user = os.environ.get("ADMIN_USER", "admin")
pwd = os.environ.get("ADMIN_PASS", "")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(target, 22, user, pwd, timeout=10)

stdin, stdout, stderr = client.exec_command("find / -name '*acl.daf80561*' 2>/dev/null")
files = stdout.read().decode().strip().splitlines()
print("Archivos encontrados:", files)
for f in files:
    stdin, stdout, stderr = client.exec_command(f"cat {f}")
    print(f"=== {f} ===")
    print(stdout.read().decode())

client.close()

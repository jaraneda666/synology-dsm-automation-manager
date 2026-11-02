import paramiko

target = "192.168.1.100"
user = os.environ.get("ADMIN_USER", "admin")
pwd = os.environ.get("ADMIN_PASS", "")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(target, 22, user, pwd, timeout=10)

stdin, stdout, stderr = client.exec_command(f"echo {pwd} | sudo -S nginx -t")
print("nginx -t exit code:", stdout.channel.recv_exit_status())
print("stdout:\n", stdout.read().decode())
print("stderr:\n", stderr.read().decode())

client.close()

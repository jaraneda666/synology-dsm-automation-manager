import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.1.100', 22, os.environ.get("ADMIN_USER", "admin"), os.environ.get("ADMIN_PASS", ""))
_, out, _ = c.exec_command("grep -E 'access_log|error_log' /etc/nginx/nginx.conf")
print(out.read().decode())
c.close()

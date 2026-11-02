import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.1.100', 22, os.environ.get("ADMIN_USER", "admin"), os.environ.get("ADMIN_PASS", ""))
_, out, _ = c.exec_command(f"echo '{os.environ.get('ADMIN_PASS', '')}' | sudo -S grep 'nginx_error' /var/log/messages | tail -n 15")
print(out.read().decode())
c.close()

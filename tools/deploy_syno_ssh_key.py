import paramiko
from pathlib import Path

key_path = Path.home() / ".ssh" / "id_ed25519.pub"
pub_key = key_path.read_text().strip()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.1.100', 22, os.environ.get("ADMIN_USER", "admin"), os.environ.get("ADMIN_PASS", ""))

setup_cmds = f"""
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo '{pub_key}' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
sort -u ~/.ssh/authorized_keys -o ~/.ssh/authorized_keys
cat ~/.ssh/authorized_keys
"""

stdin, stdout, stderr = client.exec_command(setup_cmds)
print("=== SETUP SSH KEY ===")
print(stdout.read().decode())
client.close()

# Test login using ONLY the key (no password)
client_key = paramiko.SSHClient()
client_key.set_missing_host_key_policy(paramiko.AutoAddPolicy())
priv_key_path = str(Path.home() / ".ssh" / "id_ed25519")
try:
    client_key.connect('192.168.1.100', 22, os.environ.get("ADMIN_USER", "admin"), key_filename=priv_key_path, allow_agent=False, look_for_keys=False)
    print("¡CONEXION SSH POR LLAVE Ed25519 EXITOSA!")
    stdin, stdout, stderr = client_key.exec_command('whoami && uname -a')
    print(stdout.read().decode())
except Exception as e:
    print(f"Error probando login por llave: {e}")
finally:
    client_key.close()

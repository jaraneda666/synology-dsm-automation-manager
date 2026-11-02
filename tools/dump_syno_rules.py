import paramiko
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.1.100', 22, os.environ.get("ADMIN_USER", "admin"), os.environ.get("ADMIN_PASS", ""), timeout=10)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(f'echo "$ADMIN_PASS" | sudo -S {cmd}')
    raw = stdout.read().decode('utf-8', errors='replace').strip()
    if raw.startswith('Password:'):
        raw = raw[len('Password:'):].strip()
    return raw

content = run('cat /usr/syno/etc/firewall.d/2.json')
data = json.loads(content)
rules = data.get('rules', [])
global_rules = data.get('rules', {}).get('global', [])
print(f"Total global rules: {len(global_rules)}")
for r in global_rules:
    idx = r.get('ruleIndex')
    en = r.get('enable')
    pol = r.get('policy')
    proto = r.get('protocol')
    ipGrp = r.get('ipGroup')
    ipList = r.get('ipList')
    portGrp = r.get('portGroup')
    ports = r.get('portList')
    print(f"idx:{idx:<2} en:{en} pol:{pol} proto:{proto} ipGrp:{ipGrp} ipList:{ipList} portGrp:{portGrp} ports:{ports}")
client.close()

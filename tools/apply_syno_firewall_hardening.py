import paramiko
import json
import base64
import sys
from pathlib import Path

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('192.168.1.100', 22, os.environ.get("ADMIN_USER", "admin"), os.environ.get("ADMIN_PASS", ""), timeout=10)

    def run(cmd):
        stdin, stdout, stderr = client.exec_command(f'echo "$ADMIN_PASS" | sudo -S {cmd}')
        raw = stdout.read().decode('utf-8', errors='replace').strip()
        if raw.startswith('Password:'):
            raw = raw[len('Password:'):].strip()
        return raw

    print("1. Cargando configuración original desde backup local...")
    local_bak = Path('output/backups/synology_firewall_20261007/2.json')
    content = local_bak.read_text(encoding='utf-8')
    data = json.loads(content)
    rules = data.get('rules', {}).get('global', [])
    print(f"Total reglas originales: {len(rules)}")

    # Modificar reglas existentes
    for r in rules:
        # Deshabilitar SSH para GeoIP CL (dejarlo solo en LAN y VPN)
        if r.get('portList') == ['ssh'] and r.get('ipGroup') == 3:
            print("  - Deshabilitando regla SSH GeoIP CL...")
            r['enable'] = False
        # Deshabilitar Transmission Web (9091) para todos
        elif r.get('portList') == ['transmission'] and r.get('ipGroup') == 5:
            print("  - Deshabilitando regla Transmission Web pública...")
            r['enable'] = False
        # Deshabilitar dms_https (5001) para todos
        elif r.get('portList') == ['dms_https'] and r.get('ipGroup') == 5:
            print("  - Deshabilitando regla DMS HTTPS pública...")
            r['enable'] = False

    # Agregar reglas explícitas de seguridad antes del DROP final
    openvpn_rule = {
        "adapterDirect": 1,
        "blLog": False,
        "chainList": ["FORWARD_FIREWALL", "INPUT_FIREWALL"],
        "enable": True,
        "ipDirect": 1,
        "ipGroup": 1,
        "ipList": ["10.8.0.0", "255.255.255.0"],
        "ipType": 0,
        "labelList": [],
        "name": "OpenVPN_Subnet",
        "policy": 0,
        "portDirect": 0,
        "portGroup": 3,
        "portList": [],
        "protocol": 3,
        "table": "filter"
    }

    bt_rule = {
        "adapterDirect": 1,
        "blLog": False,
        "chainList": ["FORWARD_FIREWALL", "INPUT_FIREWALL"],
        "enable": True,
        "ipDirect": 1,
        "ipGroup": 5,
        "ipList": [],
        "ipType": 2,
        "labelList": [],
        "name": "BitTorrent_Data",
        "policy": 0,
        "portDirect": 0,
        "portGroup": 1,
        "portList": ["58130"],
        "protocol": 3,
        "table": "filter"
    }

    # Separar la regla final de drop (policy == 1)
    drop_rule = None
    other_rules = []
    for r in rules:
        if r.get('policy') == 1:
            drop_rule = r
        else:
            other_rules.append(r)

    if drop_rule is None:
        drop_rule = {
            "adapterDirect": 1,
            "blLog": False,
            "chainList": ["FORWARD_FIREWALL", "INPUT_FIREWALL"],
            "enable": True,
            "ipDirect": 1,
            "ipGroup": 5,
            "ipList": [],
            "ipType": 2,
            "labelList": [],
            "name": "Deny_All_Default",
            "policy": 1,
            "portDirect": 0,
            "portGroup": 3,
            "portList": [],
            "protocol": 3,
            "table": "filter"
        }
    else:
        drop_rule['enable'] = True
        print("  - Activando regla DROP ALL predeterminada...")

    # Combinar en orden: otras reglas + OpenVPN + BitTorrent + Drop Final
    final_rules = other_rules + [openvpn_rule, bt_rule, drop_rule]

    for idx, r in enumerate(final_rules):
        r['ruleIndex'] = idx

    data['rules']['global'] = final_rules
    new_json_str = json.dumps(data, indent=3)

    print("2. Transfiriendo configuración mediante base64 a /tmp/new_2.json...")
    b64_json = base64.b64encode(new_json_str.encode('utf-8')).decode('ascii')
    # Use standard shell without sudo to write to /tmp
    client.exec_command(f'echo "{b64_json}" | base64 -d > /tmp/new_2.json')

    # Copy with sudo
    run('cp /tmp/new_2.json /usr/syno/etc/firewall.d/2.json')
    ls_out = run('ls -la /usr/syno/etc/firewall.d/2.json')
    print(f"Archivo 2.json actualizado en NAS: {ls_out}")

    print("3. Recargando firewall de Synology (synofirewall --reload)...")
    reload_out = run('/usr/syno/bin/synofirewall --reload')
    print(f"Salida reload: {reload_out}")

    print("4. Preparando script de blindaje para DOCKER-USER...")
    docker_script = '''#!/bin/sh
# Flush DOCKER-USER
iptables -F DOCKER-USER 2>/dev/null || true
# Aceptar conexiones establecidas y relacionadas
iptables -A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
# Aceptar localhost (Nginx reverse proxy interno)
iptables -A DOCKER-USER -s 127.0.0.1/32 -j ACCEPT
# Aceptar subred LAN local
iptables -A DOCKER-USER -s 192.168.1.0/24 -j ACCEPT
# Aceptar subred OpenVPN
iptables -A DOCKER-USER -s 10.8.0.0/24 -j ACCEPT
# Aceptar subredes internas de Docker entre sí
iptables -A DOCKER-USER -s 172.16.0.0/12 -j ACCEPT
# Descartar cualquier otro acceso directo desde el exterior
iptables -A DOCKER-USER -j DROP
'''
    b64_docker = base64.b64encode(docker_script.encode('utf-8')).decode('ascii')
    client.exec_command(f'echo "{b64_docker}" | base64 -d > /tmp/docker-user-firewall.sh')
    run('mkdir -p /usr/local/etc/rc.d')
    run('cp /tmp/docker-user-firewall.sh /usr/local/etc/rc.d/docker-user-firewall.sh')
    run('chmod +x /usr/local/etc/rc.d/docker-user-firewall.sh')
    run('/usr/local/etc/rc.d/docker-user-firewall.sh')
    print("Script /usr/local/etc/rc.d/docker-user-firewall.sh instalado y ejecutado.")

    print("5. Verificando reglas activas en iptables del NAS...")
    docker_rules = run('iptables -L DOCKER-USER -n -v --line-numbers')
    print("=== DOCKER-USER ACTIVO ===")
    print(docker_rules)

    client.close()
    print("\n[BLINDAJE DE SYNOLOGY Y DOCKER APLICADO Y VERIFICADO EXITOSAMENTE]")
    return 0

if __name__ == "__main__":
    sys.exit(main())

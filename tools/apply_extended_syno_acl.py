import datetime
import json
import os
from pathlib import Path
import paramiko

target = "192.168.1.100"
user = os.environ.get("ADMIN_USER", "admin")
pwd = os.environ.get("ADMIN_PASS", "")
acl_id = "daf80561-c4c6-4b03-8bcc-191d9e9fc374"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(target, 22, user, pwd, timeout=10)

def run_sudo(cmd):
    stdin, stdout, stderr = client.exec_command(f"echo {pwd} | sudo -S {cmd}")
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return code, out, err

def write_remote_file(remote_path, content_bytes):
    stdin, stdout, stderr = client.exec_command(f"cat > {remote_path}")
    stdin.write(content_bytes)
    stdin.channel.shutdown_write()
    code = stdout.channel.recv_exit_status()
    return code

try:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    local_bak_dir = Path("output") / "backups" / f"syno_rp_{timestamp}"
    local_bak_dir.mkdir(parents=True, exist_ok=True)

    print("=== PASO 1: RESPALDO DE SEGURIDAD LOCAL Y REMOTO ===")
    _, rp_orig, _ = run_sudo("cat /usr/syno/etc/www/ReverseProxy.json")
    (local_bak_dir / "ReverseProxy.json").write_text(rp_orig, encoding="utf-8")
    
    code, _, _ = run_sudo(f"cp -f /usr/syno/etc/www/ReverseProxy.json /usr/syno/etc/www/ReverseProxy.json.bak_{timestamp}")
    print(f"Respaldo remoto creado: /usr/syno/etc/www/ReverseProxy.json.bak_{timestamp} (code {code})")
    print(f"Respaldo local guardado en: {local_bak_dir / 'ReverseProxy.json'}")

    print("\n=== PASO 2: ASIGNAR ACL 'LAN_y_VPN' A SERVICIOS OBJETIVO ===")
    rp_data = json.loads(rp_orig)

    target_services = [
        "Obsidian",
        "n8n",
        "transmission",
        "ollama",
        "radarr",
        "sonarr",
        "prowlarr",
        "bazarr",
        "jacket",
        "Nas Synology",
        "alternatrr",
        "LabDash",
        "Speedtest"
    ]

    modified_count = 0
    for k, v in rp_data.items():
        if isinstance(v, dict):
            desc = v.get("description", "")
            fqdn = v.get("frontend", {}).get("fqdn", "")
            if desc in target_services:
                v["frontend"]["acl"] = acl_id
                modified_count += 1
                print(f"[+] ACL asignada a: {desc:15} -> {fqdn}")
            elif desc in ["Jellyfin", "Wizarr"]:
                print(f"[-] Omitido intencionalmente (Streaming/Invitaciones): {desc:15} -> {fqdn}")

    print(f"\nTotal servicios actualizados: {modified_count}")

    print("\n=== PASO 3: ESCRIBIR CONFIGURACION ACTUALIZADA ===")
    rp_bytes = json.dumps(rp_data, indent=4).encode('utf-8')
    write_remote_file("/tmp/ReverseProxy.json.new", rp_bytes)
    code, _, _ = run_sudo("cp /tmp/ReverseProxy.json.new /usr/syno/etc/www/ReverseProxy.json && chmod 644 /usr/syno/etc/www/ReverseProxy.json")
    print(f"Copia a /usr/syno/etc/www/ReverseProxy.json: exit code {code}")

    print("\n=== PASO 4: REGENERAR CONFIGURACION NGINX CON SYNOW3TOOL ===")
    code, out, err = run_sudo("/usr/syno/bin/synow3tool --gen-all")
    print(f"synow3tool gen-all: exit code {code}")

    print("\n=== PASO 5: VALIDAR SINTAXIS NGINX ===")
    code, out, err = run_sudo("nginx -t")
    print(f"nginx -t: exit code {code}")
    if err:
        print(f"nginx -t output: {err}")

    if code == 0:
        code_hup, out_hup, _ = run_sudo("/usr/syno/bin/synow3tool --deploy-hup")
        print(f"synow3tool deploy-hup: exit code {code_hup} (Configuración desplegada exitosamente)")
    else:
        print("[!] ERROR EN NGINX TEST! Restaurando respaldo inmediato...")
        run_sudo(f"cp -f /usr/syno/etc/www/ReverseProxy.json.bak_{timestamp} /usr/syno/etc/www/ReverseProxy.json")
        run_sudo("/usr/syno/bin/synow3tool --gen-all && /usr/syno/bin/synow3tool --deploy-hup")
        raise RuntimeError("Fallo en sintaxis Nginx, se restauró el respaldo.")

    print("\n=== PASO 6: VERIFICAR server.ReverseProxy.conf EN VIVO ===")
    code, out, _ = run_sudo("grep -E 'server_name|include.*acl' /etc/nginx/sites-enabled/server.ReverseProxy.conf")
    print(out)

finally:
    client.close()

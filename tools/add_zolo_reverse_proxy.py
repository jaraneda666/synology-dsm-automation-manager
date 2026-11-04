"""
# Tool: add_zolo_reverse_proxy.py

## Metadata
- Nombre: add_zolo_reverse_proxy.py
- Versión: 1.0
- Lenguaje: Python
- Creada en proyecto: Synology_Manager
- Fecha de creación: 2026-11-04
- Descripción: Agrega el proxy reverso para Anker Zolo Mojo Manager (puerto 8080) en Synology DSM 7 (192.168.50.2) bajo zolo.jaraneda.synology.me con SSL/TLS 443, HSTS y ACL LAN_y_VPN. Realiza respaldo preventivo y regenera Nginx con synow3tool y validación nginx -t.
- Parámetros: --host, --port, --user, --password
- Dependencias: paramiko

## Código
"""

import argparse
import datetime
import getpass
import json
import os
from pathlib import Path
import sys
import uuid

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


try:
    import paramiko
except ImportError:
    print("Error: Requiere la librería 'paramiko'. Ejecute: pip install paramiko")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Dar de alta proxy reverso para Zolo en Synology DSM")
    parser.add_argument("--host", default="192.168.50.2", help="IP del NAS Synology")
    parser.add_argument("--port", type=int, default=22, help="Puerto SSH")
    parser.add_argument("--user", default=os.environ.get("ADMIN_USER", "jaraneda"), help="Usuario SSH (jaraneda/admin)")
    parser.add_argument("--password", default=os.environ.get("SYNO_PASS", os.environ.get("ADMIN_PASS", None)), help="Contraseña")
    args = parser.parse_args()

    host = args.host
    port = args.port
    user = args.user
    pwd = args.password

    if not pwd:
        pwd = getpass.getpass(f"Ingrese la contraseña SSH/sudo para {user}@{host}: ")

    acl_id = "daf80561-c4c6-4b03-8bcc-191d9e9fc374"
    fqdn_target = "zolo.jaraneda.synology.me"
    service_desc = "Zolo Mojo Manager"
    backend_port = 8080

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"\n[+] Conectando a {user}@{host}:{port}...")
    try:
        client.connect(host, port=port, username=user, password=pwd, timeout=10)
    except Exception as e:
        print(f"[!] Error de conexión SSH: {e}")
        sys.exit(1)

    def run_sudo(cmd):
        stdin, stdout, stderr = client.exec_command(f"echo '{pwd}' | sudo -S {cmd}")
        code = stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        return code, out, err

    def write_remote_file(remote_path, content_bytes):
        stdin, stdout, stderr = client.exec_command(f"cat > {remote_path}")
        stdin.write(content_bytes)
        stdin.channel.shutdown_write()
        return stdout.channel.recv_exit_status()

    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        local_bak_dir = Path("output") / "backups" / f"syno_rp_{timestamp}"
        local_bak_dir.mkdir(parents=True, exist_ok=True)

        print("\n=== PASO 1: RESPALDO PREVENTIVO LOCAL Y REMOTO ===")
        code, rp_orig, err = run_sudo("cat /usr/syno/etc/www/ReverseProxy.json")
        if code != 0 or not rp_orig:
            raise RuntimeError(f"No se pudo leer /usr/syno/etc/www/ReverseProxy.json: {err}")

        (local_bak_dir / "ReverseProxy.json").write_text(rp_orig, encoding="utf-8")
        code_bak, _, _ = run_sudo(f"cp -f /usr/syno/etc/www/ReverseProxy.json /usr/syno/etc/www/ReverseProxy.json.bak_{timestamp}")
        print(f"[+] Respaldo remoto creado: /usr/syno/etc/www/ReverseProxy.json.bak_{timestamp}")
        print(f"[+] Respaldo local guardado en: {local_bak_dir / 'ReverseProxy.json'}")

        print("\n=== PASO 2: VERIFICAR Y AGREGAR ENTRADA PARA ZOLO ===")
        rp_data = json.loads(rp_orig)

        # Verificar si ya existe
        existing_key = None
        for k, v in rp_data.items():
            if isinstance(v, dict):
                if v.get("frontend", {}).get("fqdn") == fqdn_target:
                    existing_key = k
                    break

        entry_id = existing_key or str(uuid.uuid4())
        entry_key = rp_data[existing_key].get("_key", str(uuid.uuid4())) if existing_key else str(uuid.uuid4())

        new_entry = {
            "_key": entry_key,
            "backend": {
                "fqdn": "localhost",
                "port": backend_port,
                "protocol": 0
            },
            "customize_headers": [],
            "description": service_desc,
            "frontend": {
                "acl": acl_id,
                "fqdn": fqdn_target,
                "https": {
                    "hsts": True
                },
                "port": 443,
                "protocol": 1
            },
            "proxy_connect_timeout": 60,
            "proxy_http_version": 1,
            "proxy_intercept_errors": False,
            "proxy_read_timeout": 60,
            "proxy_send_timeout": 60
        }

        rp_data[entry_id] = new_entry
        action_verb = "Actualizada" if existing_key else "Creada"
        print(f"[+] {action_verb} entrada para '{service_desc}': {fqdn_target}:443 -> localhost:{backend_port} (ACL: {acl_id})")

        print("\n=== PASO 3: ESCRIBIR ReverseProxy.json EN DSM ===")
        rp_bytes = json.dumps(rp_data, indent=4).encode('utf-8')
        write_remote_file("/tmp/ReverseProxy.json.new", rp_bytes)
        code_cp, _, err_cp = run_sudo("sh -c 'cp /tmp/ReverseProxy.json.new /usr/syno/etc/www/ReverseProxy.json && chmod 644 /usr/syno/etc/www/ReverseProxy.json && rm -f /tmp/ReverseProxy.json.new'")
        if code_cp != 0:
            raise RuntimeError(f"Error copiando archivo de configuración: {err_cp}")
        print("[+] ReverseProxy.json actualizado con permisos 644")

        print("\n=== PASO 4: REGENERAR CONFIGURACION NGINX CON SYNOW3TOOL ===")
        code_gen, out_gen, err_gen = run_sudo("/usr/syno/bin/synow3tool --gen-all")
        print(f"[+] synow3tool gen-all: exit code {code_gen}")

        print("\n=== PASO 5: VALIDAR SINTAXIS NGINX ===")
        code_t, out_t, err_t = run_sudo("nginx -t")
        print(f"nginx -t: exit code {code_t}")

        if code_t == 0:
            print("\n=== PASO 6: DESPLEGAR Y RECARGAR NGINX (HUP) ===")
            code_hup, out_hup, _ = run_sudo("/usr/syno/bin/synow3tool --deploy-hup")
            run_sudo("nginx -s reload")
            print(f"[+] synow3tool deploy-hup y nginx reload: exit code {code_hup}")
            print("\n[EXITO] Proxy reverso para Zolo Mojo Manager desplegado y activo.")
        else:
            print(f"[!] ERROR EN SINTAXIS NGINX:\n{err_t}")
            print("[!] Restaurando respaldo previo...")
            run_sudo(f"sh -c 'cp -f /usr/syno/etc/www/ReverseProxy.json.bak_{timestamp} /usr/syno/etc/www/ReverseProxy.json && /usr/syno/bin/synow3tool --gen-all && /usr/syno/bin/synow3tool --deploy-hup'")
            raise RuntimeError("Fallo en sintaxis Nginx; se restauró el respaldo automáticamente.")

        print("\n=== PASO 7: VERIFICACION EN VIVO DE NGINX SITES ===")
        code_check, out_check, _ = run_sudo("grep -A 10 -B 2 'zolo.jaraneda.synology.me' /etc/nginx/sites-enabled/server.ReverseProxy.conf 2>/dev/null || grep -A 10 -B 2 'zolo.jaraneda.synology.me' /etc/nginx/app.d/server.ReverseProxy.conf 2>/dev/null")
        if out_check:
            print(out_check)
        else:
            print("Entrada generada en Nginx.")

    finally:
        client.close()


if __name__ == "__main__":
    main()


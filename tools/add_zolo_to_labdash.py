"""
# Tool: add_zolo_to_labdash.py

## Metadata
- Nombre: add_zolo_to_labdash.py
- Versión: 1.0
- Lenguaje: Python
- Creada en proyecto: Synology_Manager
- Fecha de creación: 2026-11-04
- Descripción: Agrega el acceso directo de Anker Zolo Mojo Manager (https://zolo.jaraneda.synology.me) al dashboard LabDash (/volume1/docker/lab-dash/config/config.json) en Synology DSM con respaldo previo y reinicio seguro del contenedor.
- Parámetros: --host, --user, --password
- Dependencias: paramiko

## Código
"""

import argparse
import datetime
import json
import os
from pathlib import Path
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    import paramiko
except ImportError:
    print("Error: Requiere la librería 'paramiko'.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Agregar Zolo Mojo a LabDash")
    parser.add_argument("--host", default="192.168.50.2", help="IP del Synology NAS")
    parser.add_argument("--user", default=os.environ.get("ADMIN_USER", "jaraneda"), help="Usuario SSH")
    parser.add_argument("--password", default=os.environ.get("SYNO_PASS", None), help="Contraseña")
    args = parser.parse_args()

    pwd = args.password
    if not pwd:
        import getpass
        pwd = getpass.getpass(f"Ingrese la contraseña SSH/sudo para {args.user}@{args.host}: ")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(args.host, 22, args.user, pwd, timeout=10)

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
        config_path = "/volume1/docker/lab-dash/config/config.json"
        local_bak_dir = Path("output") / "backups" / f"labdash_cfg_{timestamp}"
        local_bak_dir.mkdir(parents=True, exist_ok=True)

        print("=== PASO 1: RESPALDO DE CONFIGURACION LABDASH ===")
        code, orig_cfg, err = run_sudo(f"cat {config_path}")
        if code != 0 or not orig_cfg:
            raise RuntimeError(f"No se pudo leer {config_path}: {err}")

        (local_bak_dir / "config.json").write_text(orig_cfg, encoding="utf-8")
        run_sudo(f"cp -f {config_path} {config_path}.bak_{timestamp}")
        print(f"[+] Respaldo remoto: {config_path}.bak_{timestamp}")
        print(f"[+] Respaldo local: {local_bak_dir / 'config.json'}")

        print("\n=== PASO 2: AGREGAR ACCESO DIRECTO EN LABDASH ===")
        cfg_data = json.loads(orig_cfg)

        target_url = "https://zolo.jaraneda.synology.me"
        target_label = "Zolo Mojo"

        new_item = {
            "id": "item-zolo-mojo-manager",
            "label": target_label,
            "icon": {
                "path": "./assets/bluetooth.svg",
                "name": "Zolo Mojo Altavoz",
                "source": "Custom"
            },
            "url": target_url,
            "type": "app-shortcut",
            "showLabel": True,
            "adminOnly": True
        }

        # Actualizar desktop layout
        desktop_items = cfg_data.get("layout", {}).get("desktop", [])
        existing_d = [i for i in desktop_items if i.get("url") == target_url or i.get("id") == new_item["id"]]
        if not existing_d:
            desktop_items.append(new_item)
            print(f"[+] Agregado item a Desktop layout ({len(desktop_items)} items en total)")
        else:
            print("[*] Item ya existente en Desktop layout")

        # Actualizar mobile layout
        mobile_items = cfg_data.get("layout", {}).get("mobile", [])
        existing_m = [i for i in mobile_items if i.get("url") == target_url or i.get("id") == new_item["id"]]
        if not existing_m:
            mobile_items.append(new_item)
            print(f"[+] Agregado item a Mobile layout ({len(mobile_items)} items en total)")
        else:
            print("[*] Item ya existente en Mobile layout")

        print("\n=== PASO 3: ESCRIBIR NUEVA CONFIGURACION ===")
        updated_bytes = json.dumps(cfg_data, indent=2).encode('utf-8')
        write_remote_file("/tmp/config.json.new", updated_bytes)
        code_cp, _, err_cp = run_sudo(f"sh -c 'cp /tmp/config.json.new {config_path} && chmod 777 {config_path} && rm -f /tmp/config.json.new'")
        if code_cp != 0:
            raise RuntimeError(f"Error escribiendo {config_path}: {err_cp}")
        print("[+] config.json actualizado con éxito")

        print("\n=== PASO 4: REINICIAR CONTENEDOR LAB-DASH ===")
        code_restart, out_restart, err_restart = run_sudo("/var/packages/ContainerManager/target/usr/bin/docker restart Lab-Dash")
        print(f"[+] docker restart Lab-Dash: exit code {code_restart}")

        print("\n[EXITO] Zolo Mojo Manager integrado exitosamente en LabDash.")

    finally:
        client.close()


if __name__ == "__main__":
    main()

"""
# Tool: grant_temp_wifi_access.py

## Metadata
- Nombre: grant_temp_wifi_access.py
- Versión: 1.0
- Lenguaje: Python
- Creada en proyecto: Synology_Manager / OpenWrt
- Fecha de creación: 2026-11-04
- Descripción: Habilita salida a Internet temporal para notebook (MAC b0:05:94:fa:a5:99) en red Casa (VLAN 50) de OpenWrt. Crea asignación estática DHCP (192.168.50.99), whitelist en firewall WAN y programa auto-revocación a las 23:59 vía cron.
- Parámetros: --host, --mac, --ip
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
    parser = argparse.ArgumentParser(description="Habilitar acceso temporal a Internet en OpenWrt")
    parser.add_argument("--host", default="192.168.50.1", help="IP del router OpenWrt")
    parser.add_argument("--user", default="root", help="Usuario SSH")
    parser.add_argument("--key", default=str(Path.home() / ".ssh" / "id_ed25519"), help="Ruta de clave privada")
    parser.add_argument("--mac", default="b0:05:94:fa:a5:99", help="Dirección MAC del notebook")
    parser.add_argument("--ip", default="192.168.50.99", help="IP estática temporal a asignar")
    args = parser.parse_args()

    mac_target = args.mac.lower()
    ip_target = args.ip

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"[+] Conectando a {args.user}@{args.host}...")
    client.connect(args.host, 22, args.user, key_filename=args.key, timeout=10)

    def run_cmd(cmd):
        stdin, stdout, stderr = client.exec_command(cmd)
        code = stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        return code, out, err

    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        local_bak_dir = Path("output") / "backups" / f"openwrt_temp_access_{timestamp}"
        local_bak_dir.mkdir(parents=True, exist_ok=True)

        print("\n=== PASO 1: RESPALDO PREVENTIVO DE CONFIGURACIONES ===")
        _, dhcp_cfg, _ = run_cmd("cat /etc/config/dhcp")
        _, fw_cfg, _ = run_cmd("cat /etc/config/firewall")
        _, cron_cfg, _ = run_cmd("crontab -l 2>/dev/null")

        (local_bak_dir / "dhcp").write_text(dhcp_cfg, encoding="utf-8")
        (local_bak_dir / "firewall").write_text(fw_cfg, encoding="utf-8")
        (local_bak_dir / "crontab").write_text(cron_cfg, encoding="utf-8")
        print(f"[+] Respaldos guardados localmente en: {local_bak_dir}")

        print(f"\n=== PASO 2: ASIGNACION DHCP PARA NOTEBOOK ({mac_target} -> {ip_target}) ===")
        setup_dhcp = f"""
        uci -q delete dhcp.notebook_temp
        uci set dhcp.notebook_temp=host
        uci set dhcp.notebook_temp.name='notebook_temp'
        uci set dhcp.notebook_temp.mac='{mac_target}'
        uci set dhcp.notebook_temp.ip='{ip_target}'
        uci set dhcp.notebook_temp.leasetime='12h'
        uci commit dhcp
        /etc/init.d/dnsmasq restart
        """
        code_d, out_d, err_d = run_cmd(setup_dhcp)
        print(f"[+] Configuración DHCP aplicada (dnsmasq restarted, code {code_d})")

        print(f"\n=== PASO 3: WHITELIST EN FIREWALL LAN -> WAN ===")
        setup_fw = f"""
        uci -q del_list firewall.drop_unknown_mac.src_mac='!{mac_target}'
        uci add_list firewall.drop_unknown_mac.src_mac='!{mac_target}'
        uci commit firewall
        /etc/init.d/firewall reload
        """
        code_f, out_f, err_f = run_cmd(setup_fw)
        print(f"[+] Whitelist en firewall aplicada (firewall reloaded, code {code_f})")

        print(f"\n=== PASO 4: PROGRAMAR AUTO-REVOCACION A LAS 23:59 DE HOY ===")
        now = datetime.datetime.now()
        day = now.day
        month = now.month

        revoke_script = f"""#!/bin/sh
# Revocacion automatica de notebook temporal ({mac_target})
logger -t temp_access "Iniciando revocacion automatica de acceso para {mac_target}..."
uci -q delete dhcp.notebook_temp
uci commit dhcp
/etc/init.d/dnsmasq restart
uci -q del_list firewall.drop_unknown_mac.src_mac='!{mac_target}'
uci commit firewall
/etc/init.d/firewall reload
sed -i '/revoke_temp_notebook.sh/d' /etc/crontabs/root 2>/dev/null
/etc/init.d/cron reload
logger -t temp_access "Acceso temporal para {mac_target} revocado exitosamente."
"""
        stdin, stdout, stderr = client.exec_command("cat > /root/revoke_temp_notebook.sh")
        stdin.write(revoke_script.encode('utf-8'))
        stdin.channel.shutdown_write()
        stdout.channel.recv_exit_status()

        run_cmd("chmod +x /root/revoke_temp_notebook.sh")

        cron_entry = f"59 23 {day} {month} * /root/revoke_temp_notebook.sh"
        setup_cron = f"""
        sed -i '/revoke_temp_notebook.sh/d' /etc/crontabs/root 2>/dev/null
        echo '{cron_entry}' >> /etc/crontabs/root
        /etc/init.d/cron reload
        """
        run_cmd(setup_cron)
        print(f"[+] Cron programado para revocación automática a las 23:59 ({cron_entry})")

        print("\n=== PASO 5: VERIFICACION DE ESTADO ===")
        _, out_check_dhcp, _ = run_cmd("uci show dhcp.notebook_temp")
        print(out_check_dhcp)

        _, out_check_fw, _ = run_cmd(f"uci show firewall.drop_unknown_mac | grep '{mac_target}'")
        print(f"[+] Whitelist verificada: {out_check_fw}")

        print(f"\n[EXITO] Notebook ({mac_target}) ahora tiene IP {ip_target} y salida a Internet habilitada hasta las 23:59 de hoy.")

    finally:
        client.close()


if __name__ == "__main__":
    main()

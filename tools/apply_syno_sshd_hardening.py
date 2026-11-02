"""
# Tool: apply_syno_sshd_hardening.py

## Metadata
- Nombre: apply_syno_sshd_hardening.py
- Versión: 1.0
- Lenguaje: Python
- Creada en proyecto: OpenWrt_Manager
- Fecha de creación: 2026-10-08
- Descripción: Realiza respaldo integral (local y remoto) de /etc/ssh/sshd_config en Synology DSM (192.168.1.100), configura StrictModes no y PubkeyAuthentication yes, recarga el servicio sshd de forma segura y verifica la autenticación por clave pública Ed25519.
- Parámetros: --disable-passwords (opcional, solo tras verificar login por clave)
- Dependencias: paramiko

## Código
"""

import sys
import os
import re
import time
from datetime import datetime
from pathlib import Path
import paramiko

TARGET_IP = "192.168.1.100"
TARGET_PORT = 22
TARGET_USER = os.environ.get("ADMIN_USER", "admin")
TARGET_PWD = os.environ.get("ADMIN_PASS", "")
KEY_PATH = Path.home() / ".ssh" / "id_ed25519"

def sudo_exec(client, command, check_exit=True):
    stdin, stdout, stderr = client.exec_command(f"echo '{TARGET_PWD}' | sudo -S {command}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    code = stdout.channel.recv_exit_status()
    # Clean sudo password prompt from stderr if present
    err_clean = re.sub(r'\[sudo\] password for [^:]+:\s*', '', err).strip()
    if check_exit and code != 0:
        raise RuntimeError(f"Command failed (exit {code}): {command}\nError: {err_clean}\nOutput: {out}")
    return code, out, err_clean

def test_key_login():
    if not KEY_PATH.exists():
        raise FileNotFoundError(f"Clave privada no encontrada en: {KEY_PATH}")
    
    test_client = paramiko.SSHClient()
    test_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        test_client.connect(
            TARGET_IP,
            port=TARGET_PORT,
            username=TARGET_USER,
            key_filename=str(KEY_PATH),
            look_for_keys=False,
            allow_agent=False,
            timeout=10
        )
        _, stdout, _ = test_client.exec_command("whoami && uname -a")
        res = stdout.read().decode('utf-8', errors='replace').strip()
        test_client.close()
        return True, res
    except Exception as e:
        return False, str(e)

def main():
    disable_password = "--disable-passwords" in sys.argv
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(__file__).resolve().parent.parent / "output" / "backups" / f"synology_sshd_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    print("==================================================")
    print(f"HARDENING SSH EN SYNOLOGY DSM ({TARGET_IP})")
    print(f"Modo: {'DESACTIVAR CONTRASENAS' if disable_password else 'HABILITAR LLAVE ED25519 (StrictModes no)'}")
    print("==================================================")

    # 1. Conectar con usuario y credenciales actuales
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(TARGET_IP, port=TARGET_PORT, username=TARGET_USER, password=TARGET_PWD, timeout=10)
    print(f"[1] Conectado exitosamente a Synology como '{TARGET_USER}'.")

    # 2. Descargar y respaldar localmente /etc/ssh/sshd_config
    remote_backup_path = f"/etc/ssh/sshd_config.bak_{timestamp}"
    sudo_exec(client, f"cp -p /etc/ssh/sshd_config {remote_backup_path}")
    print(f"[2] Respaldo remoto creado en Synology: {remote_backup_path}")

    _, original_content, _ = sudo_exec(client, "cat /etc/ssh/sshd_config")
    local_backup_file = backup_dir / "sshd_config.orig"
    local_backup_file.write_text(original_content, encoding="utf-8")
    print(f"[3] Respaldo local guardado en: {local_backup_file}")

    # 3. Aplicar transformaciones al contenido
    content = original_content

    # StrictModes no
    if re.search(r"^\s*#?\s*StrictModes\s+", content, re.MULTILINE):
        content = re.sub(r"^\s*#?\s*StrictModes\s+.*$", "StrictModes no", content, flags=re.MULTILINE)
    else:
        content += "\nStrictModes no\n"

    # PubkeyAuthentication yes
    if re.search(r"^\s*#?\s*PubkeyAuthentication\s+", content, re.MULTILINE):
        content = re.sub(r"^\s*#?\s*PubkeyAuthentication\s+.*$", "PubkeyAuthentication yes", content, flags=re.MULTILINE)
    else:
        content += "\nPubkeyAuthentication yes\n"

    # AuthorizedKeysFile .ssh/authorized_keys
    if re.search(r"^\s*#?\s*AuthorizedKeysFile\s+", content, re.MULTILINE):
        content = re.sub(r"^\s*#?\s*AuthorizedKeysFile\s+.*$", "AuthorizedKeysFile .ssh/authorized_keys", content, flags=re.MULTILINE)
    else:
        content += "\nAuthorizedKeysFile .ssh/authorized_keys\n"

    # Manejo de PasswordAuthentication
    if disable_password:
        if re.search(r"^\s*#?\s*PasswordAuthentication\s+", content, re.MULTILINE):
            content = re.sub(r"^\s*#?\s*PasswordAuthentication\s+.*$", "PasswordAuthentication no", content, flags=re.MULTILINE)
        else:
            content += "\nPasswordAuthentication no\n"
        print("[4] Configurando 'PasswordAuthentication no'...")
    else:
        print("[4] Manteniendo 'PasswordAuthentication yes' activo como salvaguarda durante prueba...")

    # Guardar copia local de lo que se va a subir
    (backup_dir / "sshd_config.new").write_text(content, encoding="utf-8")

    # 4. Escribir a archivo temporal en Synology usando stdin pipe y reemplazar con sudo
    temp_remote = f"/tmp/sshd_config_{timestamp}.tmp"
    stdin, stdout, stderr = client.exec_command(f"cat > {temp_remote}")
    stdin.write(content)
    stdin.flush()
    stdin.channel.shutdown_write()
    _ = stdout.channel.recv_exit_status()

    sudo_exec(client, f"chmod 600 {temp_remote}")
    sudo_exec(client, f"cp {temp_remote} /etc/ssh/sshd_config")
    sudo_exec(client, f"rm -f {temp_remote}")
    print("[5] Archivo /etc/ssh/sshd_config actualizado con permisos 600.")

    # 5. Validar sintaxis con sshd -t
    test_code, test_out, test_err = sudo_exec(client, "/usr/sbin/sshd -t", check_exit=False)
    # Ignorar warning deprecado 'Deprecated option UsePrivilegeSeparation'
    fatal_errors = [line for line in test_err.splitlines() if "Deprecated option" not in line and "Password:" not in line and line.strip()]
    if fatal_errors:
        print(f"[!] ERROR de sintaxis detectado en sshd_config. Restaurando respaldo inmediato...")
        sudo_exec(client, f"cp {remote_backup_path} /etc/ssh/sshd_config")
        raise RuntimeError(f"Syntax validation failed:\n" + "\n".join(fatal_errors))

    print("[6] Sintaxis de configuracion verificada correctamente.")

    # 6. Recargar / reiniciar sshd
    print("[7] Recargando servicio sshd en Synology...")
    sudo_exec(client, "systemctl reload sshd || systemctl restart sshd")
    time.sleep(2)

    client.close()
    print("[8] Sesion previa cerrada limpiamente.")

    # 7. Probar autenticacion por llave Ed25519
    print("[9] Probando conexion autenticada EXCLUSIVAMENTE por llave Ed25519...")
    ok, details = test_key_login()
    if ok:
        print("\n==================================================")
        print(" [EXITO CONFIRMADO] Autenticacion por llave Ed25519 operativa!")
        print(f"Salida del host: {details}")
        print("==================================================")
        return 0
    else:
        print(f"\n[FALLO EN AUTENTICACION POR LLAVE]: {details}")
        # Restaurar automaticamente si fallo
        restore_client = paramiko.SSHClient()
        restore_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        restore_client.connect(TARGET_IP, port=TARGET_PORT, username=TARGET_USER, password=TARGET_PWD, timeout=10)
        sudo_exec(restore_client, f"cp {remote_backup_path} /etc/ssh/sshd_config")
        sudo_exec(restore_client, "systemctl reload sshd || systemctl restart sshd")
        restore_client.close()
        print(f"[!] Respaldo restaurado automaticamente por seguridad.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

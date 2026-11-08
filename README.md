# Synology DSM 7.2 Automation & Security Manager

Colección de herramientas de automatización para Synology DSM: administración de perfiles de control de acceso (ACL) en Nginx, reglas de cortafuegos perimetral, verificación de certificados SSL y monitoreo de procesos.

---

## Arquitectura y Componentes

- **Proxy Inverso:** Automatización de directivas Nginx y Access Control Profiles vía herramientas internas (`synow3tool`).
- **Auditoría:** Inspección de servicios en escucha, puertos abiertos y permisos de sistema de archivos.
- **Seguridad:** Hardening de configuración SSH con llaves Ed25519.

---

## Instrucciones de Uso

```bash
# Auditoría general de servicios y reglas en Synology NAS
python tools/audit_synology.py --host 192.168.1.50
```

---

## Consideraciones de Seguridad

- Este repositorio almacena código fuente, utilitarios de prueba y documentación técnica de ingeniería.
- Todas las credenciales, llaves privadas y variables de entorno deben suministrarse de forma local mediante archivos no versionados.
- Las herramientas de auditoría contenidas deben utilizarse exclusivamente en entornos autorizados y laboratorios de prueba.

---

**Autor:** Juan Carlos Araneda M.  
**Licencia:** MIT License (consulte [LICENSE](LICENSE))

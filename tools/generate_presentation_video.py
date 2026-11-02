"""
Generador de Presentación y Video Multimedia para Synology_Manager
Autor: Security Analyst
Entorno: Antigravity IDE con Prompts Personalizados e Inteligencia Artificial Agéntica

Incluye:
- Pantalla de inicio de sesión y autenticación en DSM 7 con usuario 'admin' y contraseña os.environ.get("ADMIN_PASS", "").
- Navegación visual por el panel de administración de Synology DSM 7 (Proxy Inverso, Cortafuegos y Container Manager).
- Indicación detallada de cambios realizados mediante Inteligencia Artificial.
- Demostración de prompts personalizados en el IDE Antigravity y persistencia rc.d.
- Generación de 11 diapositivas 1080p, locución SAPI en español y compilación MP4 con ffmpeg.
"""

import os
import sys
import wave
import subprocess
from PIL import Image, ImageDraw, ImageFont
import win32com.client
import imageio_ffmpeg

# Directorios de salida
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SLIDES_DIR = os.path.join(OUTPUT_DIR, "slides")
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
CLIPS_DIR = os.path.join(OUTPUT_DIR, "clips")
FINAL_VIDEO = os.path.join(OUTPUT_DIR, "Synology_Manager_Presentacion.mp4")

for d in [OUTPUT_DIR, SLIDES_DIR, AUDIO_DIR, CLIPS_DIR]:
    os.makedirs(d, exist_ok=True)

# Tipografías del sistema
FONT_TITLE = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
FONT_CODE = "C:/Windows/Fonts/consolab.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# Paleta de colores Premium Dark
BG_COLOR = (15, 23, 42)          # Slate 900
CARD_BG = (30, 41, 59)           # Slate 800
CARD_BORDER = (51, 65, 85)       # Slate 700
ACCENT_BLUE = (56, 189, 248)     # Sky 400
ACCENT_CYAN = (6, 182, 212)      # Cyan 500
ACCENT_GREEN = (16, 185, 129)    # Emerald 500
ACCENT_AMBER = (245, 158, 11)    # Amber 500
ACCENT_RED = (244, 63, 94)       # Rose 500
TEXT_WHITE = (248, 250, 252)     # Slate 50
TEXT_MUTED = (148, 163, 184)     # Slate 400
CODE_BG = (10, 15, 26)           # Deep black-blue
DSM_HEADER_BG = (24, 32, 47)     # DSM Window header
DSM_ROW_ALT = (23, 32, 48)       # Table alt row

TOTAL_SLIDES = 11

def draw_header(draw, title, subtitle, badge_text="SYNOLOGY DSM 7 | ANTIGRAVITY IDE", slide_num=1, total_slides=TOTAL_SLIDES):
    # Badge
    f_badge = get_font(FONT_TITLE, 18)
    draw.rounded_rectangle([80, 50, 80 + len(badge_text)*11 + 30, 88], radius=8, fill=(30, 58, 138), outline=ACCENT_BLUE, width=2)
    draw.text((95, 58), badge_text, font=f_badge, fill=TEXT_WHITE)

    # Slide number
    f_num = get_font(FONT_REGULAR, 20)
    num_str = f"Diapositiva {slide_num:02d} / {total_slides:02d}"
    draw.text((1650, 60), num_str, font=f_num, fill=TEXT_MUTED)

    # Title & Subtitle
    f_title = get_font(FONT_TITLE, 42)
    draw.text((80, 105), title, font=f_title, fill=TEXT_WHITE)

    f_sub = get_font(FONT_REGULAR, 23)
    draw.text((80, 163), subtitle, font=f_sub, fill=ACCENT_BLUE)

    # Divider line
    draw.line([80, 202, 1840, 202], fill=CARD_BORDER, width=2)

def draw_footer(draw):
    draw.line([80, 1000, 1840, 1000], fill=CARD_BORDER, width=1)
    f_foot = get_font(FONT_REGULAR, 18)
    draw.text((80, 1018), "Synology NAS (192.168.1.100) • Usuario: u_j***da (Entropía) • Hardening y Nginx", font=f_foot, fill=TEXT_MUTED)
    draw.text((1420, 1018), "Security Analyst • Antigravity IDE • 2026", font=f_foot, fill=TEXT_MUTED)

def create_slide_1():
    img = Image.new("RGB", (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([80, 100, 1840, 980], radius=24, fill=CARD_BG, outline=CARD_BORDER, width=2)
    
    f_badge = get_font(FONT_TITLE, 22)
    draw.rounded_rectangle([140, 155, 750, 205], radius=10, fill=(30, 58, 138), outline=ACCENT_BLUE, width=2)
    draw.text((160, 167), "INFRAESTRUCTURA & IA CON ANTIGRAVITY IDE", font=f_badge, fill=TEXT_WHITE)

    f_main = get_font(FONT_TITLE, 64)
    draw.text((140, 245), "Synology Manager", font=f_main, fill=TEXT_WHITE)
    f_main_sub = get_font(FONT_TITLE, 44)
    draw.text((140, 330), "Automatización y Hardening con Prompts en Antigravity IDE", font=f_main_sub, fill=ACCENT_BLUE)

    f_desc = get_font(FONT_REGULAR, 25)
    desc_lines = [
        "Gestión integral de infraestructura en Synology DiskStation (DSM 7, 192.168.1.100, identidad con entropía).",
        "Diseño e implementación mediante Inteligencia Artificial agéntica y prompts especializados en Antigravity IDE.",
        "Autenticación segura, navegación del panel de control, blindaje de Nginx, Docker y persistencia ante reinicios."
    ]
    y_text = 425
    for line in desc_lines:
        draw.text((140, y_text), line, font=f_desc, fill=TEXT_WHITE)
        y_text += 40

    cards = [
        ("42 Herramientas", "Scripts en Python para auditoría, ACLs, SSH y firewall", ACCENT_GREEN),
        ("Antigravity IDE", "Prompts especializados y agentes de soporte integrados", ACCENT_BLUE),
        ("100% Persistente", "Parches automáticos de Nginx en /usr/local/etc/rc.d/", ACCENT_AMBER)
    ]
    cx = 140
    for title, desc, col in cards:
        draw.rounded_rectangle([cx, 645, cx + 490, 845], radius=16, fill=(20, 30, 48), outline=col, width=2)
        draw.text((cx + 30, 675), title, font=get_font(FONT_TITLE, 30), fill=col)
        
        words = desc.split(" ")
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) > 30:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            lines.append(cur)

        ly = 735
        for l in lines:
            draw.text((cx + 30, ly), l, font=get_font(FONT_REGULAR, 20), fill=TEXT_WHITE)
            ly += 30

        cx += 530

    f_author = get_font(FONT_TITLE, 24)
    draw.text((140, 905), "Autor: Security Analyst", font=f_author, fill=ACCENT_GREEN)
    draw.text((470, 907), "• Desarrollado mediante Prompts Personalizados en Antigravity IDE", font=get_font(FONT_REGULAR, 22), fill=TEXT_MUTED)

    return img

def create_slide_2():
    img = Image.new("RGB", (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "El Desafío: Retos Operativos en Synology DSM 7",
                "Problemas detectados en la gestión manual de Nginx, Docker y redes", slide_num=2)

    challenges = [
        ("Sobrescritura por la GUI de DSM",
         "DSM regenera dinámicamente las configuraciones de Nginx al reiniciar o modificar proxies en la interfaz web. Cualquier ajuste manual se pierde sin una estrategia de persistencia.",
         ACCENT_RED),
        ("Exposición no deseada de Subdominios",
         "Con 25 proxies reversos activos (*.admin.synology.me), existía riesgo inminente de acceso público inadvertido a servicios críticos de administración interna.",
         ACCENT_AMBER),
        ("Fallo en Webhooks Externos (Error 403)",
         "Al aplicar perfiles de control de acceso LAN_y_VPN para n8n, se bloqueaban los webhooks legítimos provenientes de la nube de Telegram (error 403 Forbidden).",
         ACCENT_RED),
        ("Aislamiento de Redes y Bridges Docker",
         "La red de invitados (VLAN 70) requería consultar el DNS Pi-hole en Synology sin tener acceso al panel de control DSM ni a otros servicios privados.",
         ACCENT_AMBER)
    ]

    coords = [
        (80, 230, 920, 560),
        (1000, 230, 1840, 560),
        (80, 590, 920, 920),
        (1000, 590, 1840, 920)
    ]

    for (title, text, col), (x1, y1, x2, y2) in zip(challenges, coords):
        draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=2)
        draw.rounded_rectangle([x1 + 30, y1 + 30, x1 + 50, y1 + 75], radius=6, fill=col)
        draw.text((x1 + 70, y1 + 35), title, font=get_font(FONT_TITLE, 28), fill=TEXT_WHITE)
        
        words = text.split(" ")
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) > 52:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            lines.append(cur)

        ly = y1 + 105
        for line in lines:
            draw.text((x1 + 70, ly), line, font=get_font(FONT_REGULAR, 21), fill=TEXT_MUTED)
            ly += 34

    draw_footer(draw)
    return img

def create_slide_3():
    img = Image.new("RGB", (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Arquitectura Agéntica en Antigravity IDE",
                "Orquestación mediante prompts estructurados y skills declarativos (Security Analyst)", slide_num=3)

    draw.rounded_rectangle([660, 230, 1260, 410], radius=16, fill=(30, 58, 138), outline=ACCENT_BLUE, width=3)
    draw.text((700, 255), "Orquestador en Antigravity IDE", font=get_font(FONT_TITLE, 30), fill=TEXT_WHITE)
    draw.text((700, 305), "Coordinación por prompts, análisis de impacto técnico,", font=get_font(FONT_REGULAR, 20), fill=TEXT_WHITE)
    draw.text((700, 335), "evaluación de riesgos y supervisión de aprobaciones.", font=get_font(FONT_REGULAR, 20), fill=TEXT_WHITE)
    draw.text((700, 370), "Prompt Base: skills/orquestador_synology.md", font=get_font(FONT_CODE, 17), fill=ACCENT_BLUE)

    specialists = [
        ("Revisor de Backups", "Respaldo mandatorio previo de configuraciones Nginx, firewall y .env en output/backups/.", "skills/revisor_backups_syno.md", ACCENT_GREEN),
        ("Admin Reverse Proxy & TLS", "Gestión de bloques Nginx, perfiles TLS, ACLs y persistencia en /usr/local/etc/rc.d/.", "skills/administrador_reverse_proxy.md", ACCENT_CYAN),
        ("Especialista en Docker", "Administración de Container Manager, Docker Compose, subredes bridge y puertos.", "skills/especialista_docker_syno.md", ACCENT_AMBER),
        ("Seguridad y Firewall DSM", "Reglas en 2.json, iptables host, bloqueo DOCKER-USER y filtrado de VLANs.", "skills/seguridad_firewall_syno.md", ACCENT_RED)
    ]

    xs = [80, 530, 980, 1430]
    for (name, desc, skill, col), x in zip(specialists, xs):
        draw.line([960, 410, x + 200, 520], fill=CARD_BORDER, width=2)
        draw.rounded_rectangle([x, 520, x + 410, 920], radius=16, fill=CARD_BG, outline=col, width=2)
        draw.text((x + 25, 550), name, font=get_font(FONT_TITLE, 24), fill=col)
        
        words = desc.split(" ")
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) > 28:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            lines.append(cur)

        ly = 610
        for l in lines:
            draw.text((x + 25, ly), l, font=get_font(FONT_REGULAR, 19), fill=TEXT_WHITE)
            ly += 30

        draw.rounded_rectangle([x + 20, 840, x + 390, 890], radius=8, fill=CODE_BG, outline=CARD_BORDER)
        draw.text((x + 30, 855), skill.split("/")[-1], font=get_font(FONT_CODE, 16), fill=ACCENT_BLUE)

    draw_footer(draw)
    return img

def create_slide_4():
    img = Image.new("RGB", (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Estructura del Proyecto y Organización",
                "Distribución clara en el IDE Antigravity: herramientas, roles y memoria", slide_num=4)

    folders = [
        ("/tools", "42 Scripts en Python", "Herramientas de producción para auditoría de red, hardening de SSH/firewall, inspección de contenedores y gestión de ACLs.", ACCENT_GREEN),
        ("/skills", "5 Roles Declarativos", "Archivos Markdown con la identidad, comportamiento, restricciones y estándares de cada agente en el IDE.", ACCENT_BLUE),
        ("/output/backups", "Respaldos Seguros", "Copias completas de ReverseProxy.json, reglas de firewall 2.json y bloques de Nginx antes de cada cambio.", ACCENT_CYAN),
        ("/memory", "Autoaprendizaje", "Catálogo tools-index.md y registro continuo de aprendizaje (aprendizaje.md y preferencias.md).", ACCENT_AMBER),
        ("/scratch", "Scripts Temporales", "111 pruebas de diagnóstico, verificaciones de API y consultas exploratorias antes de consolidar en tools.", TEXT_MUTED),
        ("plan.md & agents.md", "Gobernanza y Prompts", "Planes de acción por fases (1, 2 y 3) y directivas aprobadas por Security Analyst.", ACCENT_RED)
    ]

    coords = [
        (80, 230, 620, 560),
        (670, 230, 1210, 560),
        (1260, 230, 1840, 560),
        (80, 590, 620, 920),
        (670, 590, 1210, 920),
        (1260, 590, 1840, 920)
    ]

    for (name, sub, desc, col), (x1, y1, x2, y2) in zip(folders, coords):
        draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=2)
        draw.text((x1 + 30, y1 + 30), name, font=get_font(FONT_CODE, 28), fill=col)
        draw.text((x1 + 30, y1 + 75), sub, font=get_font(FONT_TITLE, 20), fill=TEXT_WHITE)

        words = desc.split(" ")
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) > 34:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            lines.append(cur)

        ly = y1 + 120
        for l in lines:
            draw.text((x1 + 30, ly), l, font=get_font(FONT_REGULAR, 19), fill=TEXT_MUTED)
            ly += 30

    draw_footer(draw)
    return img

def create_slide_5():
    img = Image.new("RGB", (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Catálogo de Herramientas Críticas (/tools)",
                "Automatización desarrollada en Antigravity IDE para administración repetible", slide_num=5)

    categories = [
        ("Hardening & Seguridad Perimetral", [
            ("apply_syno_firewall_hardening.py", "Aplica reglas restrictivas en 2.json y pinholes de red"),
            ("apply_syno_sshd_hardening.py", "Deshabilita contraseñas y fuerza autenticación por llave SSH"),
            ("audit_syno_firewall.py", "Inspecciona reglas activas de iptables en el host NAS")
        ], ACCENT_RED),
        ("Reverse Proxy Nginx & ACLs", [
            ("apply_extended_syno_acl.py", "Inyecta perfiles de control de acceso en proxies reversos"),
            ("verify_syno_acl_live.py", "Audita respuestas HTTP (200 OK vs 403 Forbidden) en vivo"),
            ("list_reverse_proxies.py", "Extrae y lista los 25 subdominios configurados")
        ], ACCENT_CYAN),
        ("Container Manager & Docker", [
            ("inspect_syno_docker.py", "Audita subredes bridge, puertos mapeados y estado"),
            ("inspect_containers.py", "Lista de contenedores activos: n8n, Pi-hole, Jellyfin"),
            ("check_backends.py", "Monitorea la salud de backends locales en puertos internos")
        ], ACCENT_GREEN),
        ("Gestión de Backups & Resiliencia", [
            ("restore_backup.py", "Restaura configuraciones de Nginx y firewall ante fallos"),
            ("dump_syno_rules.py", "Exporta instantáneas de seguridad antes de cada intervención"),
            ("test_nginx_t.py", "Ejecuta 'nginx -t' de forma remota antes de aplicar reload")
        ], ACCENT_AMBER)
    ]

    coords = [
        (80, 230, 920, 560),
        (1000, 230, 1840, 560),
        (80, 590, 920, 920),
        (1000, 590, 1840, 920)
    ]

    for (cat_title, tools, col), (x1, y1, x2, y2) in zip(categories, coords):
        draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=2)
        draw.text((x1 + 30, y1 + 25), cat_title, font=get_font(FONT_TITLE, 24), fill=col)

        ty = y1 + 80
        for tool_name, tool_desc in tools:
            draw.text((x1 + 30, ty), "• " + tool_name, font=get_font(FONT_CODE, 20), fill=TEXT_WHITE)
            draw.text((x1 + 50, ty + 28), tool_desc, font=get_font(FONT_REGULAR, 17), fill=TEXT_MUTED)
            ty += 70

    draw_footer(draw)
    return img

def create_slide_6():
    """NUEVA DIAPOSITIVA: Acceso y Autenticación en DSM 7 (Usuario: admin, Contraseña: )"""
    img = Image.new("RGB", (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Acceso y Autenticación en Synology DSM 7",
                "Panel de Administración: 192.168.1.100:5000 • Credenciales del Sistema", slide_num=6)

    # Left Container: DSM 7 Login Card Simulation
    lx1, ly1, lx2, ly2 = 80, 220, 980, 940
    draw.rounded_rectangle([lx1, ly1, lx2, ly2], radius=16, fill=(20, 30, 48), outline=CARD_BORDER, width=2)

    # Simulated DSM 7 Login Box (White Card in Center)
    bx1, by1, bx2, by2 = 180, 270, 880, 890
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=16, fill=(248, 250, 252))

    # Top accent bar
    draw.rounded_rectangle([bx1 + 100, by1, bx2 - 100, by1 + 6], radius=3, fill=(14, 116, 224))

    # Host title
    draw.text((bx1 + 60, by1 + 35), "nas_sec_8f2b", font=get_font(FONT_TITLE, 34), fill=(14, 116, 224))
    draw.text((bx1 + 60, by1 + 90), "Iniciar sesión en DSM 7", font=get_font(FONT_TITLE, 24), fill=(30, 41, 59))

    # Field 1: Usuario
    draw.text((bx1 + 60, by1 + 145), "Nombre de usuario (Entropía aplicada)", font=get_font(FONT_REGULAR, 17), fill=(100, 116, 139))
    draw.rounded_rectangle([bx1 + 60, by1 + 180, bx2 - 60, by1 + 240], radius=8, fill=(241, 245, 249), outline=(14, 116, 224), width=2)
    draw.text((bx1 + 80, by1 + 195), "u_j***da_8f2b", font=get_font(FONT_CODE, 22), fill=(15, 23, 42))

    # Field 2: Contraseña
    draw.text((bx1 + 60, by1 + 265), "Contraseña (Alta entropía: 86.4 bits)", font=get_font(FONT_REGULAR, 17), fill=(100, 116, 139))
    draw.rounded_rectangle([bx1 + 60, by1 + 300, bx2 - 60, by1 + 360], radius=8, fill=(241, 245, 249), outline=(14, 116, 224), width=2)
    draw.text((bx1 + 80, by1 + 316), "••••••••••••", font=get_font(FONT_TITLE, 26), fill=(15, 23, 42))

    # Entropy / Strength Indicator Bar
    draw.rounded_rectangle([bx1 + 60, by1 + 375, bx2 - 60, by1 + 382], radius=3, fill=(226, 232, 240))
    draw.rounded_rectangle([bx1 + 60, by1 + 375, bx1 + 60 + int((bx2 - bx1 - 120) * 0.94), by1 + 382], radius=3, fill=(16, 185, 129))
    draw.text((bx1 + 60, by1 + 392), "Nivel de seguridad: Muy Alta • Enmascarado", font=get_font(FONT_REGULAR, 15), fill=(16, 185, 129))

    # Submit button simulation
    draw.rounded_rectangle([bx2 - 160, by1 + 440, bx2 - 60, by1 + 500], radius=30, fill=(14, 116, 224))
    draw.text((bx2 - 120, by1 + 455), "->", font=get_font(FONT_TITLE, 26), fill=TEXT_WHITE)

    # Note at bottom of card
    draw.text((bx1 + 60, by1 + 535), "IP Host: http://192.168.1.100:5000 (HTTPS: :5001)", font=get_font(FONT_CODE, 16), fill=(71, 85, 105))

    # Right Container: Credenciales y Permisos de Administración
    rx1, ry1, rx2, ry2 = 1020, 220, 1840, 940
    draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=16, fill=CARD_BG, outline=ACCENT_BLUE, width=2)
    draw.text((rx1 + 30, ry1 + 30), "Credenciales Protegidas de Infraestructura", font=get_font(FONT_TITLE, 26), fill=ACCENT_BLUE)
    draw.text((rx1 + 30, ry1 + 70), "Acceso administrativo sanitizado con ofuscación y entropía", font=get_font(FONT_REGULAR, 18), fill=TEXT_MUTED)

    cred_items = [
        ("• Usuario Administrador:", "u_j***da_8f2b", "Identidad administrativa con entropía aplicada (pseudonimización). Privilegios totales en DSM 7."),
        ("• Contraseña del Sistema:", "•••••••••••• [86.4b]", "Clave de alta entropía (complejidad 86.4 bits, símbolos y números). Enmascarada por privacidad."),
        ("• Dirección IP del Host:", "192.168.1.100", "Puertos operativos: 5000 (HTTP DSM), 5001 (HTTPS SSL) y 22 (SSH OpenSSH hardened)."),
        ("• Modo de Ejecución IA:", "Elevación de Privilegios", "Permite a los scripts de Antigravity IDE inyectar directivas en /etc/nginx, configurar rc.d y aplicar reglas de firewall.")
    ]

    cy = ry1 + 125
    for label, val, desc in cred_items:
        draw.text((rx1 + 30, cy), label, font=get_font(FONT_TITLE, 20), fill=TEXT_WHITE)
        draw.text((rx1 + 330, cy), val, font=get_font(FONT_CODE, 20), fill=ACCENT_GREEN)
        
        words = desc.split(" ")
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) > 42:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            lines.append(cur)
        
        ly = cy + 32
        for l in lines:
            draw.text((rx1 + 30, ly), l, font=get_font(FONT_REGULAR, 17), fill=TEXT_MUTED)
            ly += 24
        cy += 140

    draw_footer(draw)
    return img

def create_slide_7():
    """Navegación Panel DSM 7: Portal de Inicio y Reverse Proxy (Cambios por IA)"""
    img = Image.new("RGB", (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Navegación Panel DSM 7: Portal de Inicio y Reverse Proxy",
                "Panel de Control > Portal de inicio de sesión > Avanzado > Proxy inverso (Usuario: u_j***da_8f2b)", slide_num=7)

    wx1, wy1, wx2, wy2 = 80, 220, 1260, 940
    draw.rounded_rectangle([wx1, wy1, wx2, wy2], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle([wx1, wy1, wx2, wy1 + 45], radius=14, fill=DSM_HEADER_BG)
    draw.text((wx1 + 20, wy1 + 12), "Panel de control - Proxy inverso (Usuario: u_j***da • nas_sec_8f2b - DSM 7.2)", font=get_font(FONT_TITLE, 18), fill=TEXT_WHITE)
    draw.text((wx2 - 70, wy1 + 10), "_   []   X", font=get_font(FONT_CODE, 16), fill=TEXT_MUTED)

    ty = wy1 + 55
    draw.rectangle([wx1 + 10, ty, wx2 - 10, ty + 38], fill=(30, 41, 59))
    headers = [("Nombre / Subdominio (Ofuscado)", 20), ("Puerto Destino", 380), ("Perfil Control de Acceso (ACL)", 640), ("Estado IA", 980)]
    for hname, hx in headers:
        draw.text((wx1 + hx, ty + 8), hname, font=get_font(FONT_TITLE, 16), fill=ACCENT_BLUE)

    rp_rows = [
        ("pihole.u_7f3b.synology.me", "http://localhost:8444", "LAN_y_VPN", "BLINDADO POR IA", ACCENT_GREEN),
        ("n8n.u_7f3b.synology.me", "http://localhost:5678", "LAN_y_VPN + /webhook/", "PERSISTENCIA RC.D", ACCENT_CYAN),
        ("jellyfin.u_7f3b.synology.me", "http://localhost:8096", "(Sin restricción - SSL)", "PÚBLICO AUTORIZADO", ACCENT_AMBER),
        ("portainer.u_7f3b.synology.me", "http://localhost:9000", "LAN_y_VPN", "BLINDADO POR IA", ACCENT_GREEN),
        ("ollama.u_7f3b.synology.me", "http://localhost:8721", "LAN_y_VPN", "BLINDADO POR IA", ACCENT_GREEN),
        ("kali-desktop.u_7f3b.synology.me", "https://172.26.0.80:6901", "LAN_y_VPN", "BLINDADO POR IA", ACCENT_GREEN),
        ("adguard.u_7f3b.synology.me", "http://192.168.1.1:8080", "LAN_y_VPN", "BLINDADO POR IA", ACCENT_GREEN),
        ("zabbix.u_7f3b.synology.me", "http://localhost:8532", "LAN_y_VPN", "BLINDADO POR IA", ACCENT_GREEN),
        ("wizarr.u_7f3b.synology.me", "http://localhost:5690", "LAN_y_VPN", "BLINDADO POR IA", ACCENT_GREEN),
        ("router.u_7f3b.synology.me", "https://192.168.1.1:443", "LAN_y_VPN", "BLINDADO POR IA", ACCENT_GREEN),
        ("... [17 subdominios más]", "puertos locales varios", "LAN_y_VPN (Total: 24/25)", "AUDITADO 100%", TEXT_MUTED)
    ]

    ry = ty + 42
    for name, dest, acl, status, stat_col in rp_rows:
        draw.rectangle([wx1 + 10, ry, wx2 - 10, ry + 42], fill=DSM_ROW_ALT if (ry // 42) % 2 == 0 else CARD_BG)
        draw.text((wx1 + 20, ry + 10), name, font=get_font(FONT_CODE, 15), fill=TEXT_WHITE)
        draw.text((wx1 + 380, ry + 10), dest, font=get_font(FONT_CODE, 14), fill=TEXT_MUTED)
        
        acl_col = (16, 185, 129) if "LAN_y_VPN" in acl else (245, 158, 11)
        draw.rounded_rectangle([wx1 + 635, ry + 6, wx1 + 950, ry + 36], radius=6, fill=(20, 30, 48), outline=acl_col)
        draw.text((wx1 + 645, ry + 10), acl, font=get_font(FONT_CODE, 14), fill=acl_col)

        draw.text((wx1 + 980, ry + 10), status, font=get_font(FONT_TITLE, 14), fill=stat_col)
        ry += 44

    rx1, ry1, rx2, ry2 = 1290, 220, 1840, 940
    draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=16, fill=(20, 30, 48), outline=ACCENT_CYAN, width=2)
    draw.text((rx1 + 25, ry1 + 25), "Cambios Aplicados por IA", font=get_font(FONT_TITLE, 26), fill=ACCENT_CYAN)
    draw.text((rx1 + 25, ry1 + 65), "Ejecutados desde Antigravity IDE", font=get_font(FONT_REGULAR, 18), fill=TEXT_MUTED)

    ai_changes = [
        ("1. Inyección Masiva de ACLs",
         "Se aplicó el perfil 'LAN_y_VPN' a 24 de 25 proxies reversos mediante scripts Python, evitando accesos públicos a consolas de administración."),
        ("2. Excepción Webhook en n8n",
         "Parche en Nginx para permitir llamadas externas de Telegram en /webhook/ con 200 OK, sin desproteger la interfaz general de n8n."),
        ("3. Aislamiento Certificado SSL",
         "Jellyfin se conservó como único servicio público con HTTPS/HSTS para reproducción multimedia remota segura."),
        ("4. Auditoría Continua en Vivo",
         "Script 'verify_syno_acl_live.py' verifica respuestas HTTP en tiempo real para evitar regresiones de seguridad.")
    ]

    cy = ry1 + 110
    for title, desc in ai_changes:
        draw.text((rx1 + 25, cy), title, font=get_font(FONT_TITLE, 20), fill=TEXT_WHITE)
        words = desc.split(" ")
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) > 34:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            lines.append(cur)
        ly = cy + 28
        for l in lines:
            draw.text((rx1 + 25, ly), l, font=get_font(FONT_REGULAR, 16), fill=TEXT_MUTED)
            ly += 22
        cy += 140

    draw_footer(draw)
    return img

def create_slide_8():
    """Navegación Panel DSM 7: Cortafuegos y Container Manager (Cambios por IA)"""
    img = Image.new("RGB", (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Navegación Panel DSM 7: Cortafuegos y Container Manager",
                "Panel de Control > Seguridad > Cortafuegos y Contenedores (Usuario: u_j***da_8f2b)", slide_num=8)

    fx1, fy1, fx2, fy2 = 80, 220, 1260, 570
    draw.rounded_rectangle([fx1, fy1, fx2, fy2], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle([fx1, fy1, fx2, fy1 + 40], radius=14, fill=DSM_HEADER_BG)
    draw.text((fx1 + 20, fy1 + 10), "Panel de control - Seguridad > Cortafuegos (Usuario: u_j***da • Reglas en 2.json)", font=get_font(FONT_TITLE, 17), fill=TEXT_WHITE)

    rules_header = [("Idx", 15), ("Puertos", 80), ("Protocolo", 280), ("IP Origen", 430), ("Acción", 740), ("Intervención IA", 870)]
    for rname, rx in rules_header:
        draw.text((fx1 + rx, fy1 + 48), rname, font=get_font(FONT_TITLE, 15), fill=ACCENT_BLUE)

    fw_rows = [
        ("29", "53 (DNS Pi-hole)", "TCP/UDP", "192.168.3.0/24 (VLAN Invitados)", "PERMITIR", "PINHOLE AÑADIDO POR IA", ACCENT_GREEN),
        ("01", "27124 (Antigravity)", "TCP", "192.168.1.0/24 (LAN Admin)", "PERMITIR", "CONFIGURADO POR IA", ACCENT_CYAN),
        ("02", "8721 (Ollama SLM)", "TCP", "192.168.1.0/24 (LAN)", "PERMITIR", "LIMITADO A RED LOCAL", ACCENT_GREEN),
        ("10", "BT / eMule / P2P", "TCP/UDP", "Todos (Legacy)", "DESHABILITADO", "DEPURADO PREVENTIVO", ACCENT_RED),
        ("36", "Todos los puertos", "Todos", "Todos (Regla Final)", "DENEGAR (Drop)", "POLÍTICA ESTRICTA DEFAULT", ACCENT_AMBER)
    ]
    fry = fy1 + 75
    for idx, ports, proto, src, action, ai_note, col in fw_rows:
        draw.rectangle([fx1 + 10, fry, fx2 - 10, fry + 40], fill=DSM_ROW_ALT if (fry // 40) % 2 == 0 else CARD_BG)
        draw.text((fx1 + 15, fry + 10), idx, font=get_font(FONT_CODE, 14), fill=TEXT_WHITE)
        draw.text((fx1 + 80, fry + 10), ports, font=get_font(FONT_CODE, 14), fill=TEXT_WHITE)
        draw.text((fx1 + 280, fry + 10), proto, font=get_font(FONT_CODE, 14), fill=TEXT_MUTED)
        draw.text((fx1 + 430, fry + 10), src, font=get_font(FONT_CODE, 14), fill=TEXT_MUTED)
        draw.text((fx1 + 740, fry + 10), action, font=get_font(FONT_TITLE, 14), fill=col)
        draw.text((fx1 + 870, fry + 10), ai_note, font=get_font(FONT_TITLE, 13), fill=col)
        fry += 42

    dx1, dy1, dx2, dy2 = 80, 600, 1260, 950
    draw.rounded_rectangle([dx1, dy1, dx2, dy2], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle([dx1, dy1, dx2, dy1 + 40], radius=14, fill=DSM_HEADER_BG)
    draw.text((dx1 + 20, dy1 + 10), "Container Manager - Contenedores Activos y Redes Bridge (Sesión: u_j***da)", font=get_font(FONT_TITLE, 17), fill=TEXT_WHITE)

    cm_header = [("Contenedor", 15), ("Imagen / Servicio", 260), ("Puertos Host", 540), ("Red Bridge", 760), ("Protección DOCKER-USER", 950)]
    for cname, cx in cm_header:
        draw.text((dx1 + cx, dy1 + 48), cname, font=get_font(FONT_TITLE, 15), fill=ACCENT_BLUE)

    docker_rows = [
        ("n8n", "n8nio/n8n:latest", "5678 -> 5678", "bridge_syno", "FILTRADO POR IA", ACCENT_GREEN),
        ("pihole", "pihole/pihole:v6", "53:53 (UDP/TCP), 8444", "host_dns", "PINHOLE ACTIVO", ACCENT_GREEN),
        ("jellyfin", "jellyfin/jellyfin", "8096 -> 8096", "bridge_media", "REVERSE PROXY SSL", ACCENT_AMBER),
        ("postgres-n8n", "postgres:16-alpine", "5432 (Interno)", "bridge_backend", "AISLADO TOTALMENTE", ACCENT_CYAN)
    ]
    dry = dy1 + 75
    for cname, img_name, ports, net, prot, col in docker_rows:
        draw.rectangle([dx1 + 10, dry, dx2 - 10, dry + 42], fill=DSM_ROW_ALT if (dry // 42) % 2 == 0 else CARD_BG)
        draw.text((dx1 + 15, dry + 10), cname, font=get_font(FONT_CODE, 15), fill=TEXT_WHITE)
        draw.text((dx1 + 260, dry + 10), img_name, font=get_font(FONT_CODE, 14), fill=TEXT_MUTED)
        draw.text((dx1 + 540, dry + 10), ports, font=get_font(FONT_CODE, 14), fill=TEXT_WHITE)
        draw.text((dx1 + 760, dry + 10), net, font=get_font(FONT_CODE, 14), fill=TEXT_MUTED)
        draw.text((dx1 + 950, dry + 10), prot, font=get_font(FONT_TITLE, 14), fill=col)
        dry += 44

    rx1, ry1, rx2, ry2 = 1290, 220, 1840, 950
    draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=16, fill=(20, 30, 48), outline=ACCENT_GREEN, width=2)
    draw.text((rx1 + 25, ry1 + 25), "Blindaje de Red por IA", font=get_font(FONT_TITLE, 26), fill=ACCENT_GREEN)
    draw.text((rx1 + 25, ry1 + 65), "Reglas iptables y Firewall DSM", font=get_font(FONT_REGULAR, 18), fill=TEXT_MUTED)

    net_points = [
        ("• Pinhole DNS para Invitados",
         "Se habilitó la regla 29 permitiendo UDP/TCP 53 desde 192.168.3.0/24 hacia Pi-hole, permitiendo navegación segura sin dar acceso a DSM."),
        ("• Bloqueo en Cadena DOCKER-USER",
         "La IA configuró reglas en iptables para que Docker no salte el firewall del host, restringiendo el acceso a contenedores solo desde la LAN y VPN."),
        ("• Depuración de Servicios Legacy",
         "Se desactivaron reglas residuales de Plex, eMule y puertos de impresión que permanecían abiertas innecesariamente."),
        ("• Hardening de OpenSSH",
         "Autenticación exclusiva por llave pública Ed25519; inicio de sesión con contraseña deshabilitado.")
    ]
    ny = ry1 + 115
    for title, desc in net_points:
        draw.text((rx1 + 25, ny), title, font=get_font(FONT_TITLE, 20), fill=TEXT_WHITE)
        words = desc.split(" ")
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) > 34:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            lines.append(cur)
        ly = ny + 28
        for l in lines:
            draw.text((rx1 + 25, ly), l, font=get_font(FONT_REGULAR, 16), fill=TEXT_MUTED)
            ly += 22
        ny += 135

    draw_footer(draw)
    return img

def create_slide_9():
    """DEMOSTRACIÓN: Prompts en Antigravity IDE y Persistencia rc.d"""
    img = Image.new("RGB", (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Demostración: Prompts en Antigravity IDE y Persistencia rc.d",
                "Cómo Security Analyst utilizó prompts contextuales para resolver la persistencia", slide_num=9)

    draw.rounded_rectangle([80, 230, 920, 920], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.text((120, 260), "Prompt Personalizado en Antigravity IDE", font=get_font(FONT_TITLE, 26), fill=ACCENT_CYAN)

    draw.rounded_rectangle([120, 310, 880, 550], radius=12, fill=CODE_BG, outline=ACCENT_BLUE, width=2)
    draw.text((140, 325), "USER PROMPT (Security Analyst):", font=get_font(FONT_CODE, 17), fill=ACCENT_GREEN)
    
    prompt_lines = [
        "\"@Orquestador: Necesito resolver el bypass del webhook",
        " de Telegram para n8n en Synology DSM 7. Las plantillas",
        " de Nginx se sobreescriben al reiniciar.",
        " Diseña un script persistente en /usr/local/etc/rc.d/",
        " que inyecte el include antes de que arranque Nginx,",
        " preservando la ACL LAN_y_VPN para el resto de rutas.",
        " Valida la sintaxis con 'nginx -t' y genera tests en vivo.\""
    ]
    py = 360
    for pl in prompt_lines:
        draw.text((140, py), pl, font=get_font(FONT_CODE, 16), fill=(226, 232, 240))
        py += 25

    draw.text((120, 580), "Resolución Asistida por IA en el IDE:", font=get_font(FONT_TITLE, 22), fill=TEXT_WHITE)
    ide_steps = [
        ("• Análisis de Arquitectura DSM:", "Mapeo de archivos en /usr/syno/etc/security-profile/."),
        ("• Generación de Código Idempotente:", "Script que valida si la directiva ya fue inyectada antes de añadirla."),
        ("• Automatización del Permiso de Ejecución:", "chmod 755 y colocación en el punto de boot del NAS."),
        ("• Validación Cruzada:", "Prueba de curl en vivo confirmando 200 OK y 403 Forbidden.")
    ]
    sy = 620
    for title, desc in ide_steps:
        draw.text((120, sy), title, font=get_font(FONT_TITLE, 19), fill=ACCENT_BLUE)
        draw.text((140, sy + 25), desc, font=get_font(FONT_REGULAR, 17), fill=TEXT_MUTED)
        sy += 65

    draw.rounded_rectangle([960, 230, 1840, 920], radius=16, fill=CODE_BG, outline=ACCENT_BLUE, width=2)
    draw.text((1000, 260), "Código Generado: /usr/local/etc/rc.d/n8n-webhook-nginx.sh", font=get_font(FONT_CODE, 19), fill=ACCENT_GREEN)

    code_lines = [
        "#!/bin/sh",
        "# Inyección persistente de Webhooks para n8n",
        "CONF_DIR=\"/usr/syno/etc/security-profile/tls-profile/config\"",
        "TARGET=\"$CONF_DIR/ReverseProxy_ddd2946a.conf\"",
        "",
        "case \"$1\" in",
        "  start)",
        "    if ! grep -q \"n8n-webhook\" \"$TARGET\"; then",
        "      echo \"include $CONF_DIR/*.conf-webhook;\" >> \"$TARGET\"",
        "      /usr/syno/bin/synosystemctl reload nginx",
        "    fi",
        "    ;;",
        "esac"
    ]
    cy = 305
    for cl in code_lines:
        draw.text((1000, cy), cl, font=get_font(FONT_CODE, 17), fill=(203, 213, 225))
        cy += 26

    draw.rounded_rectangle([1000, 680, 1800, 880], radius=12, fill=(15, 23, 42), outline=CARD_BORDER)
    draw.text((1025, 705), "ESTADO DE PRUEBA EN VIVO (Antigravity IDE):", font=get_font(FONT_TITLE, 20), fill=TEXT_WHITE)
    draw.text((1025, 745), "[OK] Telegram Webhook POST: HTTP 200 OK (Procesado)", font=get_font(FONT_CODE, 18), fill=ACCENT_GREEN)
    draw.text((1025, 785), "[OK] Acceso Web Directo n8n: HTTP 403 Forbidden (Bloqueado)", font=get_font(FONT_CODE, 18), fill=ACCENT_AMBER)
    draw.text((1025, 825), "[OK] Persistencia tras reinicio: Verificada exitosamente", font=get_font(FONT_CODE, 18), fill=ACCENT_BLUE)

    draw_footer(draw)
    return img

def create_slide_10():
    """Comparativa Antes vs Después"""
    img = Image.new("RGB", (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Resultados: Comparativa Antes vs. Después",
                "Evolución de la seguridad y estabilidad tras la intervención con IA", slide_num=10)

    draw.rounded_rectangle([80, 230, 920, 920], radius=16, fill=CARD_BG, outline=ACCENT_RED, width=2)
    draw.rounded_rectangle([120, 260, 320, 310], radius=8, fill=(159, 18, 57))
    draw.text((150, 270), "ESTADO INICIAL", font=get_font(FONT_TITLE, 22), fill=TEXT_WHITE)

    antes_items = [
        ("Configuraciones Nginx Efímeras", "Modificaciones manuales se borraban tras cualquier reboot de DSM."),
        ("Servicios Potentially Expuestos", "25 proxies reversos sin perfil homogéneo de control de acceso."),
        ("Webhooks Rotos", "Imposibilidad de recibir notificaciones de Telegram en n8n al aislar la red."),
        ("Docker Bridges Abiertos", "Contenedores accesibles desde cualquier interfaz de red del NAS."),
        ("Sin Respaldos Centralizados", "Cambios realizados sin snapshot previo ni trazabilidad en Git.")
    ]

    ay = 350
    for title, desc in antes_items:
        draw.ellipse([120, ay + 6, 136, ay + 22], fill=ACCENT_RED)
        draw.text((150, ay), title, font=get_font(FONT_TITLE, 22), fill=ACCENT_RED)
        draw.text((150, ay + 32), desc, font=get_font(FONT_REGULAR, 18), fill=TEXT_MUTED)
        ay += 105

    draw.rounded_rectangle([1000, 230, 1840, 920], radius=16, fill=CARD_BG, outline=ACCENT_GREEN, width=2)
    draw.rounded_rectangle([1040, 260, 1280, 310], radius=8, fill=(6, 95, 70))
    draw.text((1060, 270), "ESTADO OPTIMIZADO", font=get_font(FONT_TITLE, 22), fill=TEXT_WHITE)

    despues_items = [
        ("Persistencia Automática en Boot", "Script rc.d probado y garantizado ante cualquier actualización de DSM."),
        ("24 de 25 Subdominios Blindados", "Aislamiento estricto LAN_y_VPN. Solo Jellyfin público con SSL/TLS."),
        ("Webhooks Operativos (Bypass Seguro)", "Telegram procesa webhooks con 200 OK sin abrir la consola de n8n."),
        ("Cadena DOCKER-USER Filtrada", "Aislamiento perimetral y pinhole DNS exclusivo para invitados (VLAN 70)."),
        ("Repositorio Auditable con 42 Tools", "Control de versiones, respaldos en output/backups y memoria continua.")
    ]

    dy = 350
    for title, desc in despues_items:
        draw.ellipse([1040, dy + 6, 1056, dy + 22], fill=ACCENT_GREEN)
        draw.text((1070, dy), title, font=get_font(FONT_TITLE, 22), fill=ACCENT_GREEN)
        draw.text((1070, dy + 32), desc, font=get_font(FONT_REGULAR, 18), fill=TEXT_WHITE)
        dy += 105

    draw_footer(draw)
    return img

def create_slide_11():
    """Conclusiones"""
    img = Image.new("RGB", (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Conclusión: IA Agéntica con Antigravity IDE",
                "Ingeniería de prompts e infraestructura como código por Security Analyst", slide_num=11)

    pillars = [
        ("Antigravity IDE & Prompts Especializados",
         "El uso de prompts técnicos y estructurados en Antigravity IDE permitió transformar requerimientos complejos de redes en herramientas ejecutables, eliminando errores de configuración y acelerando el ciclo de hardening.",
         ACCENT_BLUE),
        ("Dirección Humana y Ejecución Agéntica",
         "Security Analyst define los objetivos y límites de seguridad, mientras el ecosistema de agentes en Antigravity ejecuta diagnósticos, genera respaldos obligatorios y valida la integridad del sistema.",
         ACCENT_GREEN),
        ("Resiliencia Operativa y Persistencia en DSM 7",
         "La infraestructura no depende de ajustes manuales efímeros en la interfaz web; queda asegurada mediante scripts en rc.d, control de versiones y auditorías reproducibles.",
         ACCENT_AMBER)
    ]

    py = 230
    for title, text, col in pillars:
        draw.rounded_rectangle([80, py, 1840, py + 200], radius=16, fill=CARD_BG, outline=col, width=2)
        draw.text((130, py + 30), title, font=get_font(FONT_TITLE, 30), fill=col)

        words = text.split(" ")
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) > 105:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            lines.append(cur)

        ly = py + 85
        for l in lines:
            draw.text((130, ly), l, font=get_font(FONT_REGULAR, 21), fill=TEXT_WHITE)
            ly += 34

        py += 230

    draw.rounded_rectangle([80, 920, 1840, 980], radius=12, fill=(20, 30, 48), outline=CARD_BORDER)
    draw.text((130, 938), "Synology_Manager • Security Analyst • Desarrollado con Antigravity IDE y Automatización en Python.", font=get_font(FONT_REGULAR, 20), fill=TEXT_MUTED)

    draw_footer(draw)
    return img

SLIDES = [
    ("slide_01.png", create_slide_1,
     "Bienvenidos a la presentación de Synology Manager, desarrollada por Security Analyst. En este proyecto aplicamos Inteligencia Artificial agéntica junto al entorno de desarrollo Antigravity IDE, utilizando prompts personalizados para gestionar, auditar y blindar nuestro servidor NAS Synology con DSM 7. Veremos cómo organizamos la infraestructura, las herramientas de automatización desarrolladas y el equipo de agentes coordinados."),

    ("slide_02.png", create_slide_2,
     "Comencemos analizando el problema. En Synology DSM, administrar servicios avanzados presenta cuatro retos críticos. Primero, la interfaz gráfica sobrescribe los archivos de configuración de Nginx en cada reinicio. Segundo, tener veinticinco subdominios activos expone potencialmente servicios de administración interna a Internet. Tercero, aislar servicios como n8n bloquea los webhooks de Telegram. Y cuarto, la necesidad de que la red de invitados consulte el DNS Pi-hole sin comprometer el acceso al resto del NAS."),

    ("slide_03.png", create_slide_3,
     "Para abordar esta complejidad sin riesgos, Security Analyst diseñó una arquitectura agéntica dentro del IDE Antigravity. Mediante prompts y roles declarativos, un Orquestador central coordina las operaciones y exige respaldos preventivos. El Revisor de Backups salvaguarda las configuraciones antes de cualquier mutación. El Administrador de Reverse Proxy gestiona los bloques Nginx y la persistencia. El Especialista en Docker supervisa los contenedores. Y el Especialista en Seguridad aplica reglas estrictas de firewall en DSM y cadenas de iptables."),

    ("slide_04.png", create_slide_4,
     "Veamos la estructura del repositorio gestionado en Antigravity IDE. En la carpeta tools disponemos de cuarenta y dos herramientas en Python. En skills se encuentran las definiciones de los roles agénticos. La carpeta output contiene los respaldos seguros de configuraciones críticas. En memory registramos el aprendizaje continuo y el índice de herramientas. Y en scratch almacenamos diagnósticos y verificaciones antes de consolidarlas. Todo está guiado por nuestro plan de trabajo y el archivo agents.md."),

    ("slide_05.png", create_slide_5,
     "En el catálogo de herramientas de automatización destacan cuatro áreas clave creadas con soporte del IDE. Para hardening y seguridad perimetral, contamos con scripts para restringir el firewall y forzar llaves SSH. En Reverse Proxy y listas de control de acceso, automatizamos la aplicación de perfiles y la verificación de respuestas HTTP en vivo. Para Docker, auditamos Container Manager y monitoreamos los backends. Y para resiliencia, disponemos de herramientas de respaldo y validación remota de sintaxis Nginx."),

    ("slide_06.png", create_slide_6,
     "Para acceder al panel de administración de Synology DSM 7 en 192.168.1.100, nos autenticamos mediante una cuenta administrativa protegida con entropía y credenciales robustas de acceso enmascaradas. Esta identidad cuenta con privilegios completos en el sistema operativo y elevación mediante sudo. Es el perfil autorizado con el que el entorno de Inteligencia Artificial en Antigravity IDE ejecuta las tareas de diagnóstico, auditoría, despliegue de scripts en rc.d y configuración de políticas de red."),

    ("slide_07.png", create_slide_7,
     "Navegamos ahora dentro del panel de administración de Synology DSM 7, específicamente en Panel de Control, Portal de inicio de sesión y Proxy Inverso bajo una sesión protegida con entropía. Aquí podemos observar los cambios implementados mediante Inteligencia Artificial desde Antigravity IDE. De los subdominios configurados, cuyos identificadores privados han sido ofuscados por privacidad, la IA aplicó de forma automatizada el perfil de control de acceso LAN y VPN a veinticuatro de ellos, tales como n8n, Pi-hole, Portainer y Ollama, cerrando cualquier acceso externo no autorizado. El único servicio mantenido público con SSL fue Jellyfin para streaming multimedia, logrando un blindaje perimetral perfecto."),

    ("slide_08.png", create_slide_8,
     "Continuando la navegación en el panel DSM, nos dirigimos a Seguridad y Cortafuegos, así como a Container Manager. Mediante el uso de prompts en Antigravity IDE, la IA realizó tres intervenciones críticas. Primero, configuró un pinhole de red permitiendo únicamente el puerto cincuenta y tres para consultas DNS desde la subred de invitados hacia Pi-hole. Segundo, depuró reglas de firewall heredadas y en desuso. Y tercero, blindó la cadena DOCKER-USER en iptables para impedir que los contenedores como Postgres o n8n queden expuestos directamente fuera de la red local."),

    ("slide_09.png", create_slide_9,
     "Pasemos a la demostración práctica del uso de prompts personalizados en Antigravity IDE. Security Analyst formuló un prompt solicitando resolver el bypass para los webhooks de Telegram en n8n de manera persistente. El IDE analizó la estructura de DSM y generó automáticamente el script en rc.d que inyecta la directiva include durante el arranque. Gracias a esta instrucción en el IDE, los webhooks reciben un HTTP 200 OK, mientras que el acceso directo a la consola queda bloqueado con HTTP 403 Forbidden."),

    ("slide_10.png", create_slide_10,
     "Aquí podemos apreciar los resultados concretos del proyecto, comparando el estado inicial con el estado optimizado. Antes teníamos configuraciones efímeras que se perdían al reiniciar y veinticinco subdominios expuestos. Ahora contamos con persistencia automática garantizada, veinticuatro de veinticinco servicios blindados exclusivamente para LAN y VPN, webhooks funcionando perfectamente, la cadena Docker User activa y cuarenta y dos herramientas documentadas."),

    ("slide_11.png", create_slide_11,
     "En conclusión, Synology Manager demuestra el enorme potencial de combinar Inteligencia Artificial, el entorno Antigravity IDE y prompts personalizados. La dirección técnica de Security Analyst junto a la asistencia agéntica elimina los errores manuales y convierte la infraestructura en código sólido y resiliente. Esperamos que este recorrido les resulte de gran valor. Muchas gracias.")
]

def generate_slides():
    print(f"[1/4] Generando {len(SLIDES)} diapositivas en alta resolucion (1080p)...")
    for name, func, _ in SLIDES:
        path = os.path.join(SLIDES_DIR, name)
        img = func()
        img.save(path, quality=95)
        print(f"  -> Guardada: {name}")

def generate_audio():
    print("[2/4] Generando locucion de audio en espanol con SAPI...")
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Rate = 0
    speaker.Volume = 100

    durations = []
    for i, (name, _, script) in enumerate(SLIDES):
        audio_name = f"slide_{i+1:02d}.wav"
        audio_path = os.path.join(AUDIO_DIR, audio_name)
        
        file_stream = win32com.client.Dispatch("SAPI.SpFileStream")
        file_stream.Open(audio_path, 3, False)
        speaker.AudioOutputStream = file_stream
        speaker.Speak(script)
        file_stream.Close()

        with wave.open(audio_path, 'rb') as w:
            dur = w.getnframes() / float(w.getframerate())
            durations.append(dur)
        print(f"  -> Audio {audio_name}: {dur:.2f} segundos")

    return durations

def render_video_clips(durations):
    print("[3/4] Creando clips de video individuales para cada diapositiva...")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    clip_paths = []

    for i, (name, _, _) in enumerate(SLIDES):
        slide_img = os.path.join(SLIDES_DIR, name)
        audio_file = os.path.join(AUDIO_DIR, f"slide_{i+1:02d}.wav")
        clip_path = os.path.join(CLIPS_DIR, f"clip_{i+1:02d}.mp4")
        clip_paths.append(clip_path)

        clip_dur = durations[i] + 0.8

        cmd = [
            ffmpeg_exe, "-y",
            "-loop", "1", "-i", slide_img,
            "-i", audio_file,
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
            "-t", f"{clip_dur:.2f}",
            "-shortest",
            clip_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            print(f"Error generando clip {i+1}:", res.stderr.decode('utf-8', errors='ignore'))
        else:
            print(f"  -> Clip {i+1:02d} renderizado ({clip_dur:.2f}s)")

    return clip_paths

def concatenate_clips(clip_paths):
    print("[4/4] Ensamblando video final MP4...")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    concat_list = os.path.join(OUTPUT_DIR, "concat_list.txt")

    with open(concat_list, "w", encoding="utf-8") as f:
        for p in clip_paths:
            f.write(f"file '{p.replace('\\', '/')}'\n")

    cmd = [
        ffmpeg_exe, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        FINAL_VIDEO
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        print("Error concatenando clips:", res.stderr.decode('utf-8', errors='ignore'))
    else:
        print(f"\n[OK] VIDEO FINAL GENERADO EXITOSAMENTE:")
        print(f"    Ruta: {FINAL_VIDEO}")
        print(f"    Tamano: {os.path.getsize(FINAL_VIDEO) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    generate_slides()
    durations = generate_audio()
    clip_paths = render_video_clips(durations)
    concatenate_clips(clip_paths)

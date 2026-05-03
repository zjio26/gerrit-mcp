<div align="center">

# Gerrit MCP

Desarrollado con [Forge](https://github.com/zjio26/forge)

Un servidor [Model Context Protocol](https://modelcontextprotocol.io/) que conecta asistentes de IA con sistemas de revisión de código [Gerrit](https://www.gerritcodereview.com/).

**Consultar cambios · Revisar código · Gestionar proyectos — todo mediante lenguaje natural.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

[English](README.md) · [中文](README.zh-CN.md) · [日本語](README.ja.md)

</div>

---

## Características

- **Gestión de cambios** — Consultar, revisar, enviar, abandonar, restaurar y hacer rebase de cambios
- **Navegación de proyectos** — Listar proyectos, ramas y etiquetas
- **Búsqueda de cuentas** — Consultar perfiles de usuario y el usuario autenticado
- **Flujo de revisores** — Agregar y listar revisores en cambios
- **Acceso a comentarios** — Leer comentarios en línea en cualquier cambio
- **Modo de solo lectura** — Despliegue seguro que bloquea todas las operaciones de escritura
- **Multi-transporte** — stdio, SSE y Streamable HTTP listos para usar

## Inicio rápido

### Ejecutar con uvx (sin clonar)

```bash
# Instalar uv (si aún no lo tienes)
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Ejecutar directamente desde GitHub — sin necesidad de clonar o instalar
GERRIT_URL=https://gerrit.example.com \
GERRIT_USERNAME=your-username \
GERRIT_PASSWORD=your-http-password \
MCP_TRANSPORT=stdio \
uvx --from git+https://github.com/zjio26/gerrit-mcp.git gerrit-mcp
```

### Instalar localmente

```bash
# Clonar e instalar con uv (recomendado)
git clone https://github.com/zjio26/gerrit-mcp.git
cd gerrit-mcp
uv pip install -e .

# O usando pip
pip install -e .
```

### Configurar

Crea un archivo `.env` con tus credenciales de Gerrit:

```bash
GERRIT_URL=https://gerrit.example.com
GERRIT_USERNAME=your-username
GERRIT_PASSWORD=your-http-password
```

> Genera una contraseña HTTP en Gerrit → Settings → HTTP Password.

### Ejecutar

```bash
# Predeterminado: Streamable HTTP en http://0.0.0.0:8000
python -m gerrit_mcp

# Transporte stdio (para Claude Desktop, etc.)
MCP_TRANSPORT=stdio python -m gerrit_mcp

# Transporte SSE
MCP_TRANSPORT=sse python -m gerrit_mcp
```

### Docker

```bash
docker build -t gerrit-mcp .
docker run --env-file .env -p 8000:8000 gerrit-mcp

# O con un transporte diferente
docker run --env-file .env -e MCP_TRANSPORT=stdio gerrit-mcp
```

## Herramientas MCP

### Cambios

| Herramienta | Descripción | Escritura |
|-------------|-------------|:---------:|
| `gerrit_query_changes` | Buscar cambios con sintaxis de consulta Gerrit | |
| `gerrit_get_change` | Obtener información detallada de un cambio | |
| `gerrit_get_change_detail` | Obtener detalle del cambio con toda la información de revisión | |
| `gerrit_get_change_comments` | Listar comentarios en un cambio | |
| `gerrit_review_change` | Revisar un cambio (puntuación + mensaje) | **W** |
| `gerrit_submit_change` | Enviar un cambio para fusión | **W** |
| `gerrit_abandon_change` | Abandonar un cambio | **W** |
| `gerrit_restore_change` | Restaurar un cambio abandonado | **W** |
| `gerrit_rebase_change` | Hacer rebase de un cambio | **W** |
| `gerrit_set_topic` | Establecer tema en un cambio | **W** |
| `gerrit_add_reviewer` | Agregar revisor a un cambio | **W** |
| `gerrit_list_reviewers` | Listar revisores de un cambio | |

### Proyectos

| Herramienta | Descripción | Escritura |
|-------------|-------------|:---------:|
| `gerrit_list_projects` | Listar proyectos visibles | |
| `gerrit_get_project` | Obtener descripción del proyecto | |
| `gerrit_list_branches` | Listar ramas de un proyecto | |
| `gerrit_list_tags` | Listar etiquetas de un proyecto | |

### Cuentas

| Herramienta | Descripción | Escritura |
|-------------|-------------|:---------:|
| `gerrit_get_self_account` | Obtener información de la cuenta autenticada | |
| `gerrit_get_account` | Obtener cuenta por nombre, email o ID | |

Las herramientas marcadas con **W** se bloquean cuando `MCP_READONLY=true`.

## Configuración

| Variable | Descripción | Predeterminado |
|----------|-------------|----------------|
| `GERRIT_URL` | URL base del servidor Gerrit | *obligatorio* |
| `GERRIT_USERNAME` | Nombre de usuario de la contraseña HTTP | *obligatorio* |
| `GERRIT_PASSWORD` | Contraseña HTTP | *obligatorio* |
| `MCP_TRANSPORT` | Modo de transporte: `stdio`, `sse` o `streamable-http` | `streamable-http` |
| `HOST` | Host de enlace del servidor (solo transportes HTTP) | `0.0.0.0` |
| `PORT` | Puerto de enlace del servidor (solo transportes HTTP) | `8000` |
| `MCP_READONLY` | Bloquear todas las operaciones de escritura | `false` |
| `GERRIT_VERIFY_SSL` | Verificar certificados SSL | `true` |
| `GERRIT_TIMEOUT` | Tiempo de espera de solicitudes en segundos | `30` |

## Integración con clientes

### Claude Desktop

Agregar a tu `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gerrit": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/zjio26/gerrit-mcp.git", "gerrit-mcp"],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "GERRIT_URL": "https://gerrit.example.com",
        "GERRIT_USERNAME": "your-username",
        "GERRIT_PASSWORD": "your-http-password"
      }
    }
  }
}
```

### Pasarela MCP (Streamable HTTP)

El transporte `streamable-http` predeterminado está diseñado para escalabilidad horizontal detrás de pasarelas MCP. Usa `stateless_http=True` y `json_response=True` para compatibilidad con proxies.

```bash
# Iniciar el servidor
python -m gerrit_mcp
# Endpoint MCP: http://localhost:8000/mcp
```

### Cliente SSE

```bash
MCP_TRANSPORT=sse python -m gerrit_mcp
# Endpoint SSE: http://localhost:8000/sse
```

## Desarrollo

```bash
# Instalar con dependencias de desarrollo
uv pip install -e ".[dev]"

# Ejecutar pruebas
pytest

# Salida detallada
pytest -v
```

## Arquitectura

```
src/gerrit_mcp/
├── __init__.py
├── __main__.py          # Punto de entrada：python -m gerrit_mcp
├── server.py            # Aplicación FastMCP, configuración de transporte, ciclo de vida
├── config.py            # pydantic-settings, variables de entorno
├── gerrit_client.py     # Cliente asíncrono Gerrit REST API (httpx)
├── models.py            # Modelos Pydantic de solicitud/respuesta
└── tools/
    ├── __init__.py      # Helpers compartidos：_format_result, _handle_error, _require_writable
    ├── changes.py       # Herramientas MCP de cambios
    ├── projects.py      # Herramientas MCP de proyectos
    └── accounts.py      # Herramientas MCP de cuentas
```

## Licencia

MIT

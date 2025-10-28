# MCP Finance IA

Servidor MCP (Model Context Protocol) para consultas financieras objetivas con IA Grok. Elimina el sentimiento del mercado y proporciona análisis basado únicamente en datos cuantitativos.

## Características

- ✅ **Análisis objetivo**: Elimina sesgos emocionales y especulación
- ✅ **Datos en tiempo real**: Precios de acciones, divisas y índices
- ✅ **IA Grok integrada**: Análisis inteligente basado en datos
- ✅ **Conversión de divisas**: Tasas de cambio actualizadas
- ✅ **Comparaciones**: Análisis objetivo entre múltiples activos
- ✅ **Visión general del mercado**: Resumen cuantitativo del mercado

## Instalación

### Prerrequisitos

- Python 3.14+
- API Key de Grok (xAI)

## Inicio rápido

```bash
# Configurar API key
cp .env.example .env
# Editar .env con tu GROK_API_KEY

# Ejecutar script de inicio (instala dependencias, ejecuta pruebas y inicia servidor)
./start.sh
```

### Instalación con uv

```bash
# Clonar el repositorio
git clone <repository-url>
cd mcp-finance-ia

# Instalar dependencias
uv sync

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu GROK_API_KEY
```

### Instalación manual

```bash
# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -e .
```

## Configuración

1. Obtén una API Key de [xAI/Grok](https://x.ai/)
2. Crea un archivo `.env` en la raíz del proyecto:
   ```
   GROK_API_KEY=tu_api_key_aqui
   ```

## Uso

### Como servidor MCP

El servidor se puede integrar con cualquier cliente MCP compatible.

### Ejecutar directamente

```bash
# Con uv
uv run mcp-finance-ia

# O directamente
python -m mcp_finance_ia.main
```

## Herramientas disponibles

### get_stock_price
Obtiene el precio actual y métricas básicas de una acción.

**Parámetros:**
- `symbol`: Símbolo de la acción (ej: "AAPL", "TSLA")

### analyze_stock
Analiza una acción con datos objetivos y consulta a Grok.

**Parámetros:**
- `symbol`: Símbolo de la acción
- `timeframe`: Periodo de análisis (opcional, default: "3mo")

### convert_currency
Convierte entre divisas usando datos objetivos.

**Parámetros:**
- `base`: Moneda base (ej: "USD")
- `target`: Moneda objetivo (ej: "EUR")
- `amount`: Cantidad a convertir (opcional, default: 1.0)

### compare_stocks
Compara múltiples acciones de manera objetiva.

**Parámetros:**
- `symbols`: Lista de símbolos a comparar
- `timeframe`: Periodo de análisis (opcional, default: "3mo")

### get_market_overview
Proporciona una visión general objetiva del mercado.

## Arquitectura

- **FastMCP**: Framework para servidores MCP
- **Grok API**: IA para análisis objetivo
- **yfinance**: Datos financieros en tiempo real
- **Pandas/Numpy**: Procesamiento de datos
- **Pydantic**: Validación de datos

## Filosofía

Este servidor está diseñado para eliminar el "ruido emocional" del análisis financiero. En lugar de depender de sentimientos, opiniones o especulación, proporciona:

- **Datos cuantitativos puros**
- **Métricas objetivas** (rendimientos, volatilidad, ratios)
- **Análisis basado en evidencia**
- **Transparencia total** en las fuentes de datos

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para soporte o preguntas, abre un issue en el repositorio.

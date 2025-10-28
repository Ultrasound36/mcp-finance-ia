# Ejemplos de uso del MCP Finance IA

Este archivo muestra cómo usar las diferentes herramientas disponibles en el servidor MCP.

## Configuración inicial

Antes de usar las herramientas, asegúrate de:

1. Tener configurada tu `GROK_API_KEY` en el archivo `.env`
2. El servidor MCP esté ejecutándose

## Herramientas disponibles

### 1. Obtener precio de acción

```json
{
  "tool": "get_stock_price",
  "arguments": {
    "symbol": "AAPL"
  }
}
```plaintext

**Respuesta esperada:**

Precio actual de AAPL: $150.25
Rendimiento diario: +2.34%
Volatilidad anual: 28.45%
Volumen promedio: 45,678,901
Máximo 52 semanas: $198.23
Mínimo 52 semanas: $124.17
```

### 2. Analizar acción con IA

```json
{
  "tool": "analyze_stock",
  "arguments": {
    "symbol": "TSLA",
    "timeframe": "3mo"
  }
}
```

**Respuesta esperada:**

ANÁLISIS OBJETIVO DE TSLA (3mo)

DATOS CUANTITATIVOS:

- Precio actual: $238.45
- Rendimiento diario: -1.23%
- Volatilidad anual: 45.67%
- Máximo 52S: $299.29
- Mínimo 52S: $138.80

ANÁLISIS DE GROK:
[Análisis objetivo basado únicamente en datos cuantitativos...]

### 3. Convertir divisas

```json
{
  "tool": "convert_currency",
  "arguments": {
    "base": "USD",
    "target": "EUR",
    "amount": 1000
  }
}
```

**Respuesta esperada:**

CONVERSIÓN DE DIVISA
1000 USD = 857.80 EUR
Tipo de cambio: 1 USD = 0.8578 EUR
Última actualización: 2025-10-27 15:30:00

### 4. Comparar acciones

```json
{
  "tool": "compare_stocks",
  "arguments": {
    "symbols": ["AAPL", "GOOGL", "MSFT"],
    "timeframe": "1mo"
  }
}
```

**Respuesta esperada:**

```

COMPARACIÓN OBJETIVA DE ACCIONES (1mo)

Símbolo    Precio      Ret.Diario  Volatilidad
---------- ----------- ----------- -----------
AAPL       $150.25     +2.34%      28.45%
GOOGL      $2,845.00   +1.87%      22.31%
MSFT       $305.50     +0.95%      19.87%

ANÁLISIS DE GROK:
[Comparación objetiva basada en métricas cuantitativas...]
```

### 5. Visión general del mercado

```json
{
  "tool": "get_market_overview",
  "arguments": {}
}
```

**Respuesta esperada:**

```
VISIÓN GENERAL OBJETIVA DEL MERCADO

ÍNDICES PRINCIPALES:
S&P 500: $4,185.50 (+1.23%)
NASDAQ: $12,987.00 (+1.45%)
DOW JONES: $33,274.15 (+0.98%)
VIX: $18.45 (-2.34%)

DIVISAS MAYORES:
EUR/USD: 1.0854
GBP/USD: 1.2678
USD/JPY: 149.23

ANÁLISIS DE GROK:
[Análisis objetivo del estado del mercado...]
```

## Notas importantes

- **Sin sesgos emocionales**: Todas las respuestas están diseñadas para eliminar sentimientos del mercado, opiniones especulativas y análisis subjetivo.

- **Datos cuantitativos**: El enfoque está en métricas objetivas como rendimientos, volatilidad, volumen y ratios matemáticos.

- **Transparencia**: Todas las fuentes de datos y metodologías de cálculo están claramente documentadas.

- **Actualización en tiempo real**: Los datos se obtienen de fuentes confiables y se actualizan en tiempo real.

## Integración con clientes MCP

Este servidor puede integrarse con cualquier cliente compatible con MCP, incluyendo:

- VS Code con extensiones MCP
- Aplicaciones de IA conversacional
- Herramientas de desarrollo
- Sistemas de automatización

Para más información sobre MCP, visita: <https://modelcontextprotocol.io/>

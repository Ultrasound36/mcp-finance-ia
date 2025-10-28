#!/usr/bin/env python3
"""
MCP Server para consultas financieras y divisas con IA Grok
Elimina el sentimiento y proporciona análisis objetivo basado en datos.
"""

import asyncio
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import httpx
import yfinance as yf
import pandas as pd
import numpy as np
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_BASE_URL = "https://api.x.ai/v1"

# Inicializar FastMCP
app = FastMCP("MCP Finance IA")

class FinancialQuery(BaseModel):
    """Modelo para consultas financieras"""
    symbol: str = Field(..., description="Símbolo del activo (ej: AAPL, EURUSD=X)")
    query_type: str = Field(..., description="Tipo de consulta: price, analysis, forecast, comparison")
    timeframe: Optional[str] = Field("1mo", description="Periodo de tiempo: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")

class CurrencyQuery(BaseModel):
    """Modelo para consultas de divisas"""
    base_currency: str = Field(..., description="Moneda base (ej: USD, EUR)")
    target_currency: str = Field(..., description="Moneda objetivo (ej: CLP, MXN)")
    amount: Optional[float] = Field(1.0, description="Cantidad a convertir")

class GrokClient:
    """Cliente para interactuar con la API de Grok"""

    def __init__(self):
        self.api_key = GROK_API_KEY
        self.base_url = GROK_BASE_URL
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )

    async def analyze_financial_data(self, data: Dict[str, Any], query: str) -> str:
        """Analiza datos financieros con Grok eliminando sesgos emocionales"""

        # Preparar el prompt para análisis objetivo
        prompt = f"""
        Analiza los siguientes datos financieros de manera OBJETIVA y CUANTITATIVA.
        ELIMINA cualquier sesgo emocional, sentimiento o especulación.
        Proporciona solo hechos basados en datos matemáticos y estadísticos.

        DATOS FINANCIEROS:
        {json.dumps(data, indent=2, default=str)}

        CONSULTA DEL USUARIO:
        {query}

        INSTRUCCIONES:
        1. Analiza únicamente datos cuantitativos
        2. Evita cualquier mención a "sentimiento del mercado"
        3. Proporciona métricas objetivas: rendimientos, volatilidad, ratios
        4. Si no hay datos suficientes, indica claramente las limitaciones
        5. Mantén el análisis neutral y basado en evidencia

        ANÁLISIS OBJETIVO:
        """

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": "grok-beta",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Eres un analista financiero objetivo que solo proporciona análisis basado en datos cuantitativos. Eliminas cualquier sesgo emocional o especulación."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1,  # Baja temperatura para mayor objetividad
                    "max_tokens": 1000
                }
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Error en la consulta a Grok: {response.status_code} - {response.text}"

        except Exception as e:
            return f"Error de conexión con Grok: {str(e)}"

class FinancialDataProvider:
    """Proveedor de datos financieros"""

    @staticmethod
    def get_stock_data(symbol: str, timeframe: str = "1mo") -> Dict[str, Any]:
        """Obtiene datos históricos de acciones"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=timeframe)

            if hist.empty:
                return {"error": f"No se encontraron datos para {symbol}"}

            # Calcular métricas objetivas
            current_price = hist['Close'].iloc[-1]
            previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price

            # Rendimiento
            daily_return = (current_price - previous_price) / previous_price * 100

            # Volatilidad (desviación estándar de retornos)
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) * 100  # Anualizada

            # Estadísticas básicas
            stats = {
                "current_price": round(current_price, 2),
                "daily_return_pct": round(daily_return, 2),
                "volatility_pct": round(volatility, 2),
                "volume_avg": int(hist['Volume'].mean()),
                "high_52w": round(hist['High'].max(), 2),
                "low_52w": round(hist['Low'].min(), 2),
                "data_points": len(hist)
            }

            return stats

        except Exception as e:
            return {"error": f"Error obteniendo datos de {symbol}: {str(e)}"}

    @staticmethod
    def get_currency_data(base: str, target: str, amount: float = 1.0) -> Dict[str, Any]:
        """Obtiene datos de conversión de divisas"""
        try:
            symbol = f"{base}{target}=X"
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")

            if data.empty:
                return {"error": f"No se encontraron datos para {base}/{target}"}

            rate = data['Close'].iloc[-1]

            return {
                "base_currency": base,
                "target_currency": target,
                "exchange_rate": round(rate, 4),
                "converted_amount": round(amount * rate, 2),
                "timestamp": data.index[-1].strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            return {"error": f"Error obteniendo datos de divisa {base}/{target}: {str(e)}"}

# Instancias globales
grok_client = GrokClient()
financial_provider = FinancialDataProvider()

# Funciones MCP
@app.tool()
async def get_stock_price(symbol: str) -> str:
    """Obtiene el precio actual y métricas básicas de una acción"""
    data = financial_provider.get_stock_data(symbol, "1d")

    if "error" in data:
        return f"Error: {data['error']}"

    return f"""
Precio actual de {symbol}: ${data['current_price']}
Rendimiento diario: {data['daily_return_pct']}%
Volatilidad anual: {data['volatility_pct']}%
Volumen promedio: {data['volume_avg']:,}
Máximo 52 semanas: ${data['high_52w']}
Mínimo 52 semanas: ${data['low_52w']}
"""

@app.tool()
async def analyze_stock(symbol: str, timeframe: str = "3mo") -> str:
    """Analiza una acción con datos objetivos y consulta a Grok"""
    data = financial_provider.get_stock_data(symbol, timeframe)

    if "error" in data:
        return f"Error: {data['error']}"

    query = f"Analiza objetivamente los datos financieros de {symbol} en el período {timeframe}"
    grok_analysis = await grok_client.analyze_financial_data(data, query)

    return f"""
ANÁLISIS OBJETIVO DE {symbol.upper()} ({timeframe})

DATOS CUANTITATIVOS:
- Precio actual: ${data['current_price']}
- Rendimiento diario: {data['daily_return_pct']}%
- Volatilidad anual: {data['volatility_pct']}%
- Máximo 52S: ${data['high_52w']}
- Mínimo 52S: ${data['low_52w']}

ANÁLISIS DE GROK:
{grok_analysis}
"""

@app.tool()
async def convert_currency(base: str, target: str, amount: float = 1.0) -> str:
    """Convierte entre divisas usando datos objetivos"""
    data = financial_provider.get_currency_data(base.upper(), target.upper(), amount)

    if "error" in data:
        return f"Error: {data['error']}"

    return f"""
CONVERSIÓN DE DIVISA
{amount} {data['base_currency']} = {data['converted_amount']} {data['target_currency']}
Tipo de cambio: 1 {data['base_currency']} = {data['exchange_rate']} {data['target_currency']}
Última actualización: {data['timestamp']}
"""

@app.tool()
async def compare_stocks(symbols: List[str], timeframe: str = "3mo") -> str:
    """Compara múltiples acciones de manera objetiva"""
    results = []
    for symbol in symbols:
        data = financial_provider.get_stock_data(symbol, timeframe)
        if "error" not in data:
            results.append({
                "symbol": symbol.upper(),
                "price": data['current_price'],
                "daily_return": data['daily_return_pct'],
                "volatility": data['volatility_pct']
            })

    if not results:
        return "Error: No se pudieron obtener datos para ninguna de las acciones especificadas"

    # Crear tabla de comparación
    comparison_data = {
        "symbols": [r["symbol"] for r in results],
        "prices": [r["price"] for r in results],
        "daily_returns": [r["daily_return"] for r in results],
        "volatilities": [r["volatility"] for r in results]
    }

    query = f"Compara objetivamente estas acciones: {', '.join([r['symbol'] for r in results])}"
    grok_analysis = await grok_client.analyze_financial_data(comparison_data, query)

    table = "\n".join([
        f"{r['symbol']:<10} ${r['price']:<10.2f} {r['daily_return']:<8.2f}% {r['volatility']:<8.2f}%"
        for r in results
    ])

    return f"""
COMPARACIÓN OBJETIVA DE ACCIONES ({timeframe})

{'Símbolo':<10} {'Precio':<10} {'Ret.Diario':<8} {'Volatilidad':<8}
{'-'*50}
{table}

ANÁLISIS DE GROK:
{grok_analysis}
"""

@app.tool()
async def get_market_overview() -> str:
    """Proporciona una visión general objetiva del mercado"""
    major_indices = ["^GSPC", "^IXIC", "^DJI", "^VIX"]
    currencies = ["EURUSD=X", "GBPUSD=X", "USDJPY=X"]

    index_data = []
    currency_data = []

    for symbol in major_indices:
        data = financial_provider.get_stock_data(symbol, "1d")
        if "error" not in data:
            index_data.append({
                "symbol": symbol.replace("^", ""),
                "price": data['current_price'],
                "daily_return": data['daily_return_pct']
            })

    for symbol in currencies:
        base, target = symbol.split("=")[0][:3], symbol.split("=")[0][3:]
        data = financial_provider.get_currency_data(base, target)
        if "error" not in data:
            currency_data.append({
                "pair": f"{base}/{target}",
                "rate": data['exchange_rate']
            })

    overview_data = {
        "indices": index_data,
        "currencies": currency_data
    }

    grok_analysis = await grok_client.analyze_financial_data(
        overview_data,
        "Proporciona un análisis objetivo del estado actual del mercado basado únicamente en datos cuantitativos"
    )

    return f"""
VISIÓN GENERAL OBJETIVA DEL MERCADO

ÍNDICES PRINCIPALES:
{"".join([f"{idx['symbol']}: ${idx['price']:,.0f} ({idx['daily_return']:+.2f}%)\n" for idx in index_data])}

DIVISAS MAYORES:
{"".join([f"{curr['pair']}: {curr['rate']:.4f}\n" for curr in currency_data])}

ANÁLISIS DE GROK:
{grok_analysis}
"""

def main():
    """Función principal para ejecutar el servidor MCP"""
    if not GROK_API_KEY:
        print("Error: GROK_API_KEY no está configurada en las variables de entorno")
        print("Crea un archivo .env con: GROK_API_KEY=tu_api_key_aqui")
        return

    print("🚀 Iniciando MCP Finance IA Server...")
    print("📊 Servidor listo para consultas financieras objetivas con Grok")

    # Ejecutar el servidor FastMCP
    app.run()

if __name__ == "__main__":
    main()
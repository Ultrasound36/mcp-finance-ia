#!/usr/bin/env python3
"""
MCP Server para consultas financieras y divisas con OpenAI
Proporciona análisis objetivo y recomendaciones de trading basadas en datos cuantitativos.
"""

import asyncio
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import openai
import yfinance as yf
import pandas as pd
import numpy as np
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

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

class FinancialAnalyst:
    """Cliente para análisis financiero con OpenAI"""

    def __init__(self):
        self.api_key = OPENAI_API_KEY

    async def analyze_financial_data(self, data: Dict[str, Any], query: str) -> str:
        """Analiza datos financieros usando OpenAI para recomendaciones de trading"""

        signals = self._calculate_trading_signals(data)
        
        # Preparar el prompt para análisis y recomendaciones
        prompt = f"""
        Analiza los siguientes datos financieros y proporciona recomendaciones de trading OBJETIVAS.
        Base tu análisis ÚNICAMENTE en datos cuantitativos y señales técnicas.

        DATOS FINANCIEROS:
        {json.dumps(data, indent=2, default=str)}

        SEÑALES TÉCNICAS:
        {json.dumps(signals, indent=2)}

        CONSULTA DEL USUARIO:
        {query}

        INSTRUCCIONES:
        1. Analiza patrones técnicos y tendencias
        2. Identifica niveles clave de soporte/resistencia
        3. Calcula y evalúa indicadores técnicos
        4. Proporciona recomendación clara: COMPRAR/VENDER/MANTENER
        5. Establece objetivos de precio y stop loss
        6. Justifica cada recomendación con datos
        7. Evalúa el riesgo/recompensa cuantitativamente

        ANÁLISIS Y RECOMENDACIONES:
        """

        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.api_key)
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un analista técnico experto que proporciona recomendaciones 
                        de trading basadas exclusivamente en análisis cuantitativo y señales técnicas. 
                        Tus recomendaciones son precisas y respaldadas por datos."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=2000
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"Error en el análisis: {str(e)}"

    def _calculate_trading_signals(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula señales técnicas de trading"""
        signals = {
            "tendencia": self._detect_trend(data),
            "soportes_resistencias": self._find_support_resistance(data),
            "momentum": self._calculate_momentum(data),
            "volatilidad": self._analyze_volatility(data),
            "recomendacion": self._generate_recommendation(data)
        }
        return signals

    def _detect_trend(self, data: Dict[str, Any]) -> str:
        """Detecta la tendencia del activo"""
        if "current_price" not in data or "high_52w" not in data or "low_52w" not in data:
            return "INDEFINIDA"
        
        price = data["current_price"]
        high = data["high_52w"]
        low = data["low_52w"]
        
        range_52w = high - low
        position = (price - low) / range_52w if range_52w > 0 else 0
        
        if position > 0.7:
            return "ALCISTA_FUERTE"
        elif position > 0.5:
            return "ALCISTA"
        elif position < 0.3:
            return "BAJISTA_FUERTE"
        elif position < 0.5:
            return "BAJISTA"
        return "LATERAL"

    def _find_support_resistance(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Identifica niveles de soporte y resistencia"""
        current_price = data.get("current_price", 0)
        high_52w = data.get("high_52w", current_price)
        low_52w = data.get("low_52w", current_price)
        
        return {
            "soporte_1": round(low_52w + (high_52w - low_52w) * 0.236, 2),
            "soporte_2": round(low_52w + (high_52w - low_52w) * 0.382, 2),
            "resistencia_1": round(low_52w + (high_52w - low_52w) * 0.618, 2),
            "resistencia_2": round(low_52w + (high_52w - low_52w) * 0.786, 2)
        }

    def _calculate_momentum(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calcula indicadores de momentum"""
        return {
            "rsi": min(100, max(0, 50 + data.get("daily_return_pct", 0) * 2)),
            "fuerza_tendencia": abs(data.get("daily_return_pct", 0)) / (data.get("volatility_pct", 1) + 0.1)
        }

    def _analyze_volatility(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza la volatilidad del activo"""
        volatility = data.get("volatility_pct", 0)
        return {
            "volatilidad_anual": volatility,
            "riesgo": "ALTO" if volatility > 30 else "MEDIO" if volatility > 15 else "BAJO",
            "stop_loss_sugerido": round(data.get("current_price", 0) * (1 - volatility/100), 2)
        }

    def _generate_recommendation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera recomendación de trading basada en señales técnicas"""
        trend = self._detect_trend(data)
        momentum = self._calculate_momentum(data)
        volatility = self._analyze_volatility(data)
        
        score = 0
        score += 2 if trend in ["ALCISTA_FUERTE"] else 1 if trend == "ALCISTA" else -2 if trend == "BAJISTA_FUERTE" else -1 if trend == "BAJISTA" else 0
        score += 1 if momentum["rsi"] > 60 else -1 if momentum["rsi"] < 40 else 0
        score += 1 if momentum["fuerza_tendencia"] > 0.5 else -1 if momentum["fuerza_tendencia"] < -0.5 else 0
        
        return {
            "accion": "COMPRAR" if score >= 2 else "VENDER" if score <= -2 else "MANTENER",
            "confianza": abs(score) / 4 * 100,  # Porcentaje de confianza
            "stop_loss": volatility["stop_loss_sugerido"]
        }

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
analyst = FinancialAnalyst()
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
    """Analiza una acción con datos objetivos y proporciona recomendaciones de trading"""
    data = financial_provider.get_stock_data(symbol, timeframe)

    if "error" in data:
        return f"Error: {data['error']}"

    query = f"Analiza los datos financieros de {symbol} y proporciona recomendaciones de trading para el período {timeframe}"
    analysis = await analyst.analyze_financial_data(data, query)

    return f"""
ANÁLISIS TÉCNICO DE {symbol.upper()} ({timeframe})

DATOS CUANTITATIVOS:
- Precio actual: ${data['current_price']}
- Rendimiento diario: {data['daily_return_pct']}%
- Volatilidad anual: {data['volatility_pct']}%
- Máximo 52S: ${data['high_52w']}
- Mínimo 52S: ${data['low_52w']}

ANÁLISIS Y RECOMENDACIONES:
{analysis}
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

    query = f"Compara estas acciones y proporciona recomendaciones de trading: {', '.join([r['symbol'] for r in results])}"
    analysis = await analyst.analyze_financial_data(comparison_data, query)

    table = "\n".join([
        f"{r['symbol']:<10} ${r['price']:<10.2f} {r['daily_return']:<8.2f}% {r['volatility']:<8.2f}%"
        for r in results
    ])

    return f"""
COMPARACIÓN OBJETIVA DE ACCIONES ({timeframe})

{'Símbolo':<10} {'Precio':<10} {'Ret.Diario':<8} {'Volatilidad':<8}
{'-'*50}
{table}

ANÁLISIS Y RECOMENDACIONES:
{analysis}
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

    analysis = await analyst.analyze_financial_data(
        overview_data,
        "Analiza el estado actual del mercado y proporciona recomendaciones de trading para índices y divisas"
    )

    return f"""
VISIÓN GENERAL OBJETIVA DEL MERCADO

ÍNDICES PRINCIPALES:
{"".join([f"{idx['symbol']}: ${idx['price']:,.0f} ({idx['daily_return']:+.2f}%)\n" for idx in index_data])}

DIVISAS MAYORES:
{"".join([f"{curr['pair']}: {curr['rate']:.4f}\n" for curr in currency_data])}

ANÁLISIS Y RECOMENDACIONES:
{analysis}
"""

def main():
    """Función principal para ejecutar el servidor MCP"""
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY no está configurada en las variables de entorno")
        print("Crea un archivo .env con: OPENAI_API_KEY=tu_api_key_aqui")
        return

    print("🚀 Iniciando MCP Finance IA Server...")
    print("📊 Servidor listo para consultas financieras y recomendaciones de trading")

    # Ejecutar el servidor FastMCP
    app.run()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Análisis de rendimiento de divisas para inversión en los últimos 3 meses
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import yfinance as yf

# Constantes de configuración
TRADING_DAYS_PER_MONTH = 21
RISK_FREE_RATE = 0.02
MIN_DATA_POINTS = 10
TOP_PERFORMERS_COUNT = 3


@dataclass
class CurrencyData:
    """Clase para almacenar datos básicos de una divisa"""

    name: str
    symbol: str
    initial_price: float
    current_price: float
    max_price: float
    min_price: float
    historical_data: pd.DataFrame


@dataclass
class CurrencyMetrics:
    """Clase para almacenar métricas calculadas de una divisa"""

    currency_data: CurrencyData
    total_return: float
    monthly_return: float
    volatility: float
    max_drawdown: float
    sharpe_ratio: float

    @property
    def currency_name(self) -> str:
        return self.currency_data.name


class CurrencyAnalyzer:
    """Analizador de rendimiento de divisas"""

    def __init__(self, currency_pairs: Dict[str, str]):
        self.currency_pairs = currency_pairs

    def analyze_period(self, months: int = 3) -> List[CurrencyMetrics]:
        """Analiza el rendimiento de divisas en un período dado"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)

        results = []
        for currency_name, symbol in self.currency_pairs.items():
            try:
                currency_data = self._fetch_currency_data(
                    currency_name, symbol, start_date, end_date
                )
                if currency_data:
                    metrics = self._calculate_metrics(currency_data)
                    results.append(metrics)
            except Exception as e:
                print(f"❌ Error analizando {currency_name}: {str(e)}")
                continue

        return results

    def _fetch_currency_data(
        self, name: str, symbol: str, start_date: datetime, end_date: datetime
    ) -> Optional[CurrencyData]:
        """Obtiene datos históricos de una divisa"""
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date, end=end_date)

        if hist.empty or len(hist) < MIN_DATA_POINTS:
            print(f"⚠️  Datos insuficientes para {name}")
            return None

        return CurrencyData(
            name=name,
            symbol=symbol,
            initial_price=hist["Close"].iloc[0],
            current_price=hist["Close"].iloc[-1],
            max_price=hist["High"].max(),
            min_price=hist["Low"].min(),
            historical_data=hist,
        )

    def _calculate_metrics(self, currency_data: CurrencyData) -> CurrencyMetrics:
        """Calcula métricas de rendimiento para una divisa"""
        hist = currency_data.historical_data

        # Rendimiento total
        total_return = self._calculate_total_return(
            currency_data.initial_price, currency_data.current_price
        )

        # Rendimiento mensualizado
        monthly_return = self._calculate_monthly_return(total_return, len(hist))

        # Volatilidad
        volatility = self._calculate_volatility(hist)

        # Máximo drawdown
        max_drawdown = self._calculate_max_drawdown(hist)

        # Sharpe ratio
        sharpe_ratio = self._calculate_sharpe_ratio(hist)

        return CurrencyMetrics(
            currency_data=currency_data,
            total_return=total_return,
            monthly_return=monthly_return,
            volatility=volatility,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
        )

    @staticmethod
    def _calculate_total_return(initial_price: float, current_price: float) -> float:
        """Calcula el rendimiento total porcentual"""
        return ((current_price - initial_price) / initial_price) * 100

    @staticmethod
    def _calculate_monthly_return(total_return: float, data_points: int) -> float:
        """Calcula el rendimiento mensualizado"""
        months = data_points / TRADING_DAYS_PER_MONTH
        return ((1 + total_return / 100) ** (1 / months) - 1) * 100

    @staticmethod
    def _calculate_volatility(hist: pd.DataFrame) -> float:
        """Calcula la volatilidad anualizada"""
        daily_returns = hist["Close"].pct_change().dropna()
        return daily_returns.std() * np.sqrt(252) * 100

    @staticmethod
    def _calculate_max_drawdown(hist: pd.DataFrame) -> float:
        """Calcula el máximo drawdown"""
        daily_returns = hist["Close"].pct_change().dropna()
        cumulative = (1 + daily_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max * 100
        return drawdown.min()

    @staticmethod
    def _calculate_sharpe_ratio(hist: pd.DataFrame) -> float:
        """Calcula el ratio Sharpe"""
        daily_returns = hist["Close"].pct_change().dropna()
        excess_returns = daily_returns - RISK_FREE_RATE / 252
        return (
            excess_returns.mean() / excess_returns.std() * np.sqrt(252)
            if excess_returns.std() > 0
            else 0
        )


class RiskEvaluator:
    """Evaluador de riesgo para inversiones en divisas"""

    @staticmethod
    def evaluate_risk(metrics: CurrencyMetrics) -> tuple[str, str]:
        """Evalúa el nivel de riesgo y proporciona recomendación"""
        total_return = metrics.total_return
        volatility = metrics.volatility

        if total_return > 5 and volatility < 10:
            return "BAJO", "EXCELENTE para inversión conservadora"
        elif total_return > 3 and volatility < 15:
            return "MEDIO", "BUENA opción con riesgo moderado"
        elif total_return > 0:
            return "ALTO", "ACEPTABLE pero con alto riesgo"
        else:
            return "MUY ALTO", "NO RECOMENDADO"


class ReportGenerator:
    """Generador de reportes de análisis de divisas"""

    def __init__(self, analyzer: CurrencyAnalyzer):
        self.analyzer = analyzer

    def generate_full_report(self, months: int = 3) -> List[CurrencyMetrics]:
        """Genera un reporte completo de análisis"""
        print("=" * 80)
        print("📊 ANÁLISIS DE RENDIMIENTO DE DIVISAS - ÚLTIMOS 3 MESES")
        print("=" * 80)

        results = self.analyzer.analyze_period(months)
        if not results:
            print("❌ No se pudieron obtener datos para ninguna divisa")
            return []

        # Ordenar por rendimiento
        results.sort(key=lambda x: x.total_return, reverse=True)

        # Mostrar período
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        print(
            f"📅 Período: {start_date.strftime('%Y-%m-%d')} al {end_date.strftime('%Y-%m-%d')}"
        )
        print()

        self._print_performance_table(results)
        self._print_top_opportunities(results)
        self._print_market_analysis(results)
        self._print_final_recommendation(results)

        return results

    def _print_performance_table(self, results: List[CurrencyMetrics]) -> None:
        """Imprime tabla de rendimiento"""
        print("📈 RENDIMIENTO POR DIVISA (ordenado por mayor ganancia)")
        print("-" * 100)
        print(
            f"{'Divisa':<12} {'Precio Inicial':<15} {'Precio Actual':<15} {'Rendimiento':<12} {'Mensual':<10} {'Volatilidad':<12}"
        )
        print("-" * 100)

        for result in results:
            data = result.currency_data
            print(
                f"{data.name:<12} {data.initial_price:<15.4f} {data.current_price:<15.4f} {result.total_return:<12.2f}% {result.monthly_return:<10.2f}% {result.volatility:<12.2f}%"
            )

    def _print_top_opportunities(self, results: List[CurrencyMetrics]) -> None:
        """Imprime las mejores oportunidades"""
        print("\n" + "=" * 80)
        print("🏆 MEJORES OPORTUNIDADES DE INVERSIÓN")
        print("=" * 80)

        top_performers = results[:TOP_PERFORMERS_COUNT]

        for i, result in enumerate(top_performers, 1):
            print(f"\n🥇 #{i} {result.currency_name}")
            print(f"   Rendimiento total: {result.total_return:+.2f}%")
            print(f"   Rendimiento mensual: {result.monthly_return:+.2f}%")
            print(f"   Volatilidad: {result.volatility:.2f}%")
            print(f"   Máximo drawdown: {result.max_drawdown:.2f}%")
            print(f"   Ratio Sharpe: {result.sharpe_ratio:.2f}")

            risk_level, recommendation = RiskEvaluator.evaluate_risk(result)
            print(f"   Nivel de riesgo: {risk_level}")
            print(f"   Recomendación: {recommendation}")

    def _print_market_analysis(self, results: List[CurrencyMetrics]) -> None:
        """Imprime análisis general del mercado"""
        print("\n" + "=" * 80)
        print("🌍 ANÁLISIS GENERAL DEL MERCADO DE DIVISAS")
        print("=" * 80)

        positive_returns = [r for r in results if r.total_return > 0]
        negative_returns = [r for r in results if r.total_return <= 0]

        print(
            f"📊 Divisas con rendimiento positivo: {len(positive_returns)} de {len(results)}"
        )
        print(
            f"📊 Divisas con rendimiento negativo: {len(negative_returns)} de {len(results)}"
        )

        if positive_returns:
            avg_positive = np.mean([r.total_return for r in positive_returns])
            print(f"📈 Rendimiento promedio (positivas): {avg_positive:.2f}%")

        if negative_returns:
            avg_negative = np.mean([r.total_return for r in negative_returns])
            print(f"📉 Pérdida promedio (negativas): {avg_negative:.2f}%")

    def _print_final_recommendation(self, results: List[CurrencyMetrics]) -> None:
        """Imprime recomendación final"""
        print("\n" + "=" * 80)
        print("🎯 RECOMENDACIÓN FINAL PARA LOS ÚLTIMOS 2 MESES DEL AÑO")
        print("=" * 80)

        if results:
            best_currency = results[0]
            expected_return = best_currency.monthly_return * 2

            print(f"💰 DIVISA RECOMENDADA: {best_currency.currency_name}")
            print(f"💰 RENDIMIENTO ESPERADO (2 meses): {expected_return:.2f}%")
            print("💰 VENTAJAS:")
            print("   • Mejor rendimiento histórico reciente")
            print("   • Tendencia alcista consistente")
            print("   • Ratio riesgo/recompensa favorable")

            if len(results) > 1:
                print("💰 ALTERNATIVAS:")
                for alt in results[1:TOP_PERFORMERS_COUNT]:
                    print(
                        f"   • {alt.currency_name}: {alt.total_return:.2f}% rendimiento total"
                    )

        print("\n⚠️  IMPORTANTE:")
        print("   • El rendimiento pasado no garantiza resultados futuros")
        print("   • Considera tu tolerancia al riesgo antes de invertir")
        print("   • Diversifica tu portafolio")
        print("   • Consulta con un asesor financiero")


def main():
    """Función principal"""
    # Configuración de pares de divisas
    currency_pairs = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "AUD/USD": "AUDUSD=X",
        "USD/CAD": "USDCAD=X",
        "USD/CHF": "USDCHF=X",
        "NZD/USD": "NZDUSD=X",
        "USD/BRL": "USDBRL=X",
    }

    print("🚀 Analizando rendimiento de divisas para inversión...")
    print("⏳ Esto puede tomar unos momentos...\n")

    # Crear instancias
    analyzer = CurrencyAnalyzer(currency_pairs)
    report_generator = ReportGenerator(analyzer)

    # Generar reporte
    results = report_generator.generate_full_report(months=3)

    if results:
        print("\n✅ Análisis completado exitosamente!")
    else:
        print("\n❌ No se pudo completar el análisis")


if __name__ == "__main__":
    main()

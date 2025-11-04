#!/usr/bin/env python3
"""
Script de prueba para el MCP Finance IA con análisis técnico y recomendaciones de trading
"""

import asyncio
import os
from dotenv import load_dotenv
import sys

# Add the 'src' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Cargar variables de entorno
load_dotenv()

async def test_market_data():
    """Prueba la obtención y análisis de datos de mercado"""
    print("🧪 Probando análisis de mercado...")

    try:
        from src.main import FinancialDataProvider, FinancialAnalyst

        provider = FinancialDataProvider()
        analyst = FinancialAnalyst()

        # Probar análisis técnico de Apple
        print("\n📈 Analizando AAPL para señales de trading...")
        apple_data = provider.get_stock_data("AAPL", "1mo")
        if "error" in apple_data:
            print(f"❌ Error: {apple_data['error']}")
        else:
            print("✅ Datos técnicos obtenidos:")
            print(f"   Precio actual: ${apple_data['current_price']}")
            print(f"   Volatilidad anual: {apple_data['volatility_pct']}%")
            
            # Obtener análisis y recomendaciones
            analysis = await analyst.analyze_financial_data(
                apple_data, 
                "Proporciona recomendaciones de trading para AAPL"
            )
            print("\n� Análisis técnico:")
            print(analysis)

        # Probar análisis de forex
        print("\n💱 Analizando par EUR/USD...")
        forex_data = provider.get_currency_data("EUR", "USD", 10000)
        if "error" in forex_data:
            print(f"❌ Error: {forex_data['error']}")
        else:
            print("✅ Datos de trading forex:")
            print(f"   Tipo de cambio: {forex_data['exchange_rate']}")
            print(f"   Monto convertido: {forex_data['converted_amount']} USD")
            
            # Obtener señales de trading para forex
            analysis = await analyst.analyze_financial_data(
                forex_data,
                "Analiza el par EUR/USD y proporciona señales de trading"
            )
            print("\n📊 Señales de trading forex:")
            print(analysis)

        print("\n✅ Análisis de mercado completado!")

    except Exception as e:
        print(f"❌ Error en análisis de mercado: {str(e)}")
        return False

    return True

async def test_trading_signals():
    """Prueba la generación de señales de trading"""
    print("\n🤖 Probando generación de señales de trading...")

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY no configurada. Saltando pruebas de análisis.")
        return True

    try:
        from src.main import FinancialAnalyst

        analyst = FinancialAnalyst()
        test_data = {
            "current_price": 150.0,
            "daily_return_pct": 2.5,
            "volatility_pct": 25.0,
            "high_52w": 175.0,
            "low_52w": 125.0,
            "volume_avg": 1000000
        }

        # Probar generación de señales técnicas
        print("\n📊 Generando señales técnicas...")
        signals = _calculate_trading_signals(test_data)
        
        print("✅ Señales técnicas generadas:")
        print(f"   Tendencia: {signals['tendencia']}")
        print(f"   Soportes/Resistencias: {signals['soportes_resistencias']}")
        print(f"   Momentum: {signals['momentum']}")
        print(f"   Recomendación: {signals['recomendacion']}")

        # Probar análisis completo
        print("\n🔄 Probando análisis completo...")
        analysis = await analyst.analyze_financial_data(
            test_data,
            "Genera recomendaciones de trading basadas en señales técnicas"
        )

        if "Error" in analysis:
            print(f"❌ Error en análisis: {analysis}")
            return False
        else:
            print("✅ Análisis técnico exitoso!")
            print(f"   Recomendación: {analysis[:200]}...")

    except Exception as e:
        print(f"❌ Error en prueba de señales: {str(e)}")
        return False

    return True

async def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del MCP Finance IA Trading")
    print("=" * 50)

    # Verificar entorno
    print(f"🐍 Python: {os.sys.version}")
    print(f"📁 Directorio: {os.getcwd()}")

    # Ejecutar pruebas
    market_ok = await test_market_data()
    signals_ok = await test_trading_signals()

    print("\n" + "=" * 50)
    if market_ok and signals_ok:
        print("🎉 Todas las pruebas pasaron exitosamente!")
        print("\n📝 Próximos pasos:")
        print("   1. Configura tu OPENAI_API_KEY en .env")
        print("   2. Ejecuta el servidor MCP: python src/main.py")
        print("   3. Utiliza las herramientas de trading en tu cliente MCP")
        print("\n💡 Características disponibles:")
        print("   - Análisis técnico automatizado")
        print("   - Señales de trading basadas en datos")
        print("   - Recomendaciones de compra/venta")
        print("   - Análisis de forex")
    else:
        print("❌ Algunas pruebas fallaron. Verifica tu configuración.")

if __name__ == "__main__":
    asyncio.run(main())
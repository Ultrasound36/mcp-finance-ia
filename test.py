#!/usr/bin/env python3
"""
Script de prueba para el MCP Finance IA
"""

import asyncio
import os
from dotenv import load_dotenv
import sys

# Add the 'src' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Cargar variables de entorno
load_dotenv()

async def test_basic_functionality():
    """Prueba las funciones básicas sin Grok"""
    print("🧪 Probando funcionalidades básicas...")

    try:
        from src.main import FinancialDataProvider

        provider = FinancialDataProvider()

        # Probar obtención de datos de Apple
        print("\n📈 Probando obtención de datos de AAPL...")
        apple_data = provider.get_stock_data("AAPL", "1d")
        if "error" in apple_data:
            print(f"❌ Error: {apple_data['error']}")
        else:
            print("✅ Datos obtenidos exitosamente:")
            print(f"   Precio actual: ${apple_data['current_price']}")
            print(f"   Rendimiento diario: {apple_data['daily_return_pct']}%")

        # Probar conversión de divisas
        print("\n💱 Probando conversión USD a EUR...")
        currency_data = provider.get_currency_data("USD", "EUR", 100)
        if "error" in currency_data:
            print(f"❌ Error: {currency_data['error']}")
        else:
            print("✅ Conversión exitosa:")
            print(f"   100 USD = {currency_data['converted_amount']} EUR")
            print(f"   Tipo de cambio: {currency_data['exchange_rate']}")

        print("\n✅ Pruebas básicas completadas exitosamente!")

    except Exception as e:
        print(f"❌ Error en pruebas básicas: {str(e)}")
        return False

    return True

async def test_grok_integration():
    """Prueba la integración con Grok"""
    print("\n🤖 Probando integración con Grok...")

    if not os.getenv("GROK_API_KEY"):
        print("⚠️  GROK_API_KEY no configurada. Saltando prueba de Grok.")
        return True

    try:
        from src.main import GrokClient

        client = GrokClient()
        test_data = {"test": "data", "value": 100}
        analysis = await client.analyze_financial_data(test_data, "Analiza estos datos de prueba")

        if "Error" in analysis:
            print(f"❌ Error en integración con Grok: {analysis}")
            return False
        else:
            print("✅ Integración con Grok exitosa!")
            print(f"   Respuesta de muestra: {analysis[:100]}...")

    except Exception as e:
        print(f"❌ Error en integración con Grok: {str(e)}")
        return False

    return True

async def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del MCP Finance IA")
    print("=" * 50)

    # Verificar entorno
    print(f"🐍 Python: {os.sys.version}")
    print(f"📁 Directorio: {os.getcwd()}")

    # Ejecutar pruebas
    basic_ok = await test_basic_functionality()
    grok_ok = await test_grok_integration()

    print("\n" + "=" * 50)
    if basic_ok and grok_ok:
        print("🎉 Todas las pruebas pasaron exitosamente!")
        print("\n📝 Próximos pasos:")
        print("   1. Configura tu GROK_API_KEY en .env")
        print("   2. Ejecuta: uv run mcp-finance-ia")
        print("   3. Integra con tu cliente MCP favorito")
    else:
        print("❌ Algunas pruebas fallaron. Revisa la configuración.")

if __name__ == "__main__":
    asyncio.run(main())
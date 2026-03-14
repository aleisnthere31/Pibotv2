"""
Test script to verify all dependencies are installed correctly.

Run this to ensure your local environment is properly configured.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🔍 Verificando dependencias instaladas...\n")

# Test core dependencies
dependencies = {
    "aiogram": "aiogram 3.22.0 (Framework principal)",
    "telegram": "python-telegram-bot 22.5",
    "aiofiles": "aiofiles 24.1.0 (Operaciones async en archivos)",
    "aiohttp": "aiohttp 3.12.15 (Cliente HTTP async)",
    "pydantic": "pydantic 2.11.10 (Validación de datos)",
    "dotenv": "python-dotenv 1.0.0 (Variables de entorno)",
    "apscheduler": "APScheduler 3.10.4 (Tareas programadas)",
    "requests": "requests 2.32.5 (Cliente HTTP sync)",
}

failed = []
successful = []

for module_name, display_name in dependencies.items():
    try:
        __import__(module_name)
        print(f"✅ {display_name}")
        successful.append(module_name)
    except ImportError as e:
        print(f"❌ {display_name} - ERROR: {e}")
        failed.append(module_name)

print("\n" + "="*60)
print(f"\n✅ Instaladas: {len(successful)}/{len(dependencies)}")

if failed:
    print(f"❌ Faltantes: {len(failed)}")
    print("\nPara instalar las faltantes, ejecuta:")
    print(f"  pip install {' '.join(failed)}")
    sys.exit(1)
else:
    print("\n🎉 ¡Todas las dependencias están instaladas correctamente!")
    print("\nPuedes proceder con las pruebas locales:")
    print("  1. Asegúrate de tener un .env con BOT_TOKEN válido")
    print("  2. Ejecuta: python main.py")
    print("  3. El bot iniciará en modo polling")
    sys.exit(0)

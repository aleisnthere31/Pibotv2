"""
Quick import test to verify the codebase is properly structured.

This script checks that all modules can be imported without errors.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🧪 Ejecutando pruebas de importación...\n")

test_results = []

# Test configuration imports
try:
    from src.config import (
        BOT_TOKEN, COMUNIDADES, ADMINS, DOMS,
        obtener_temas_por_comunidad, obtener_admins_comunidad
    )
    print("✅ Importación: src.config")
    test_results.append(("Config", True))
except Exception as e:
    print(f"❌ Importación: src.config - {e}")
    test_results.append(("Config", False))

# Test database imports
try:
    from src.database import (
        create_database, create_tables,
        insert_user, get_campo_usuario,
        dar_puntos, quitar_puntos
    )
    print("✅ Importación: src.database")
    test_results.append(("Database", True))
except Exception as e:
    print(f"❌ Importación: src.database - {e}")
    test_results.append(("Database", False))

# Test utils imports
try:
    from src.utils import obtener_gif_aleatorio, get_image_path
    print("✅ Importación: src.utils")
    test_results.append(("Utils", True))
except Exception as e:
    print(f"❌ Importación: src.utils - {e}")
    test_results.append(("Utils", False))

# Test handlers imports (non-critical, some may have issues)
try:
    from handlers.general import ver, dar, regalar
    print("✅ Importación: handlers.general")
    test_results.append(("Handlers", True))
except Exception as e:
    print(f"⚠️  Importación: handlers.general - {e}")
    test_results.append(("Handlers", False))

print("\n" + "="*60 + "\n")

passed = sum(1 for _, result in test_results if result)
total = len(test_results)

if passed == total:
    print(f"✅ {passed}/{total} módulos importados correctamente\n")
    print("🎉 ¡El proyecto está listo para pruebas locales!\n")
    print("Próximos pasos:")
    print("  1. Edita .env.local con tu BOT_TOKEN real")
    print("  2. Ejecuta: python main.py")
    print("  3. El bot iniciará en modo polling")
    print("  4. Envía /start al bot en privado para probar")
else:
    print(f"⚠️  {passed}/{total} módulos importados\n")
    print("Algunos módulos tienen errores. Revisa arriba.")

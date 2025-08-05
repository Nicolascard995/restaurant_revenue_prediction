#!/usr/bin/env python3
"""
Script final para ejecutar todos los tests y preparar el despliegue
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """Ejecutar un comando y mostrar el resultado"""
    print(f"\n🔄 {description}...")
    print("=" * 60)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} exitoso")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} falló")
            if result.stderr:
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando {description}: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando proceso de testing y preparación para despliegue...")
    print("=" * 80)
    
    # Lista de tests a ejecutar
    tests = [
        ("python3 test_simple.py", "Test básico de funcionalidades"),
        ("python3 test_projection.py", "Test de proyecciones financieras"),
        ("python3 test_cache_system.py", "Test del sistema de caché de PDFs"),
        ("python3 test_country_system.py", "Test del sistema de países específicos")
    ]
    
    all_passed = True
    
    # Ejecutar todos los tests
    for command, description in tests:
        if not run_command(command, description):
            all_passed = False
            break
    
    if all_passed:
        print("\n" + "=" * 80)
        print("🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
        print("✅ La aplicación está lista para subir a GitHub y desplegar en Render")
        print("=" * 80)
        
        # Verificar archivos de configuración para despliegue
        print("\n📋 Verificando archivos de configuración para despliegue...")
        
        required_files = [
            "app.py",
            "requirements.txt", 
            "README.md",
            "render.yaml",
            "Procfile",
            "runtime.txt"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Archivos faltantes: {missing_files}")
            return False
        else:
            print("✅ Todos los archivos de configuración están presentes")
        
        # Verificar directorios necesarios
        required_dirs = ["uploads", "templates", "static"]
        missing_dirs = []
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            print(f"❌ Directorios faltantes: {missing_dirs}")
            return False
        else:
            print("✅ Todos los directorios necesarios están presentes")
        
        print("\n🎯 RESUMEN FINAL:")
        print("✅ Tests de funcionalidad: PASARON")
        print("✅ Tests de proyecciones: PASARON") 
        print("✅ Archivos de configuración: COMPLETOS")
        print("✅ Estructura de directorios: CORRECTA")
        print("\n🚀 La aplicación está lista para:")
        print("   1. Subir a GitHub")
        print("   2. Desplegar en Render")
        print("   3. Configurar variables de entorno en Render")
        
        return True
        
    else:
        print("\n" + "=" * 80)
        print("❌ ALGUNOS TESTS FALLARON")
        print("🔧 Revisa los errores antes de subir a GitHub")
        print("=" * 80)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
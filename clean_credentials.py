#!/usr/bin/env python3
"""
Script para limpiar credenciales expuestas en el repositorio n8n-samart888
"""

import os
import re
import glob
from pathlib import Path

def find_credentials_in_file(file_path):
    """Buscar credenciales en un archivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        credentials_found = []
        
        # Patrones de credenciales
        patterns = [
            # Contraseñas hardcodeadas
            (r'password["\s]*[:=]["\s]*([^"\s]+)', 'password'),
            (r'passwd["\s]*[:=]["\s]*([^"\s]+)', 'passwd'),
            (r'pwd["\s]*[:=]["\s]*([^"\s]+)', 'pwd'),
            
            # Tokens y claves
            (r'token["\s]*[:=]["\s]*([^"\s]+)', 'token'),
            (r'api_key["\s]*[:=]["\s]*([^"\s]+)', 'api_key'),
            (r'apikey["\s]*[:=]["\s]*([^"\s]+)', 'apikey'),
            (r'secret["\s]*[:=]["\s]*([^"\s]+)', 'secret'),
            (r'key["\s]*[:=]["\s]*([^"\s]+)', 'key'),
            
            # URLs de base de datos
            (r'postgresql://([^@]+)@([^/\s]+)', 'postgresql'),
            (r'mysql://([^@]+)@([^/\s]+)', 'mysql'),
            (r'mongodb://([^@]+)@([^/\s]+)', 'mongodb'),
            (r'redis://([^@]+)@([^/\s]+)', 'redis'),
            
            # Credenciales específicas encontradas
            (r'28ZwnPHQRC', '28ZwnPHQRC'),
            (r'npg_I6sKUNeof9qb', 'npg_I6sKUNeof9qb'),
            (r'neondb_owner', 'neondb_owner'),
            (r'ep-long-wave-adza01b9', 'ep-long-wave-adza01b9'),
        ]
        
        for pattern, cred_type in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                credentials_found.append({
                    'type': cred_type,
                    'match': match.group(0),
                    'line': line_num,
                    'file': str(file_path)
                })
        
        return credentials_found
        
    except Exception as e:
        print(f"Error leyendo {file_path}: {e}")
        return []

def clean_credentials_in_file(file_path, credentials):
    """Limpiar credenciales en un archivo"""
    if not credentials:
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Reemplazar credenciales con placeholders
        for cred in credentials:
            if cred['type'] in ['password', 'passwd', 'pwd', 'token', 'api_key', 'apikey', 'secret', 'key']:
                # Reemplazar valores de credenciales
                content = re.sub(
                    rf'({cred["type"]}["\s]*[:=]["\s]*)([^"\s]+)',
                    r'\1***CREDENCIAL_OCULTA***',
                    content,
                    flags=re.IGNORECASE
                )
            elif cred['type'] in ['postgresql', 'mysql', 'mongodb', 'redis']:
                # Reemplazar URLs de base de datos
                content = re.sub(
                    rf'({cred["type"]}://)([^@]+)@([^/\s]+)',
                    r'\1***USUARIO_OCULTO***:***CONTRASEÑA_OCULTA***@***HOST_OCULTO***',
                    content,
                    flags=re.IGNORECASE
                )
            else:
                # Reemplazar credenciales específicas
                content = content.replace(cred['match'], '***CREDENCIAL_OCULTA***')
        
        # Si el contenido cambió, escribir el archivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error limpiando {file_path}: {e}")
        return False

def scan_repository():
    """Escanear todo el repositorio en busca de credenciales"""
    print("🔍 Escaneando repositorio n8n-samart888 en busca de credenciales...")
    
    # Extensiones de archivos a revisar
    extensions = [
        '*.py', '*.js', '*.ts', '*.json', '*.yaml', '*.yml', 
        '*.env', '*.config', '*.conf', '*.ini', '*.md', '*.txt'
    ]
    
    all_credentials = []
    cleaned_files = []
    
    for ext in extensions:
        files = glob.glob(f"**/{ext}", recursive=True)
        
        for file_path in files:
            # Saltar directorios de node_modules y .git
            if 'node_modules' in file_path or '.git' in file_path:
                continue
            
            print(f"   📄 Revisando: {file_path}")
            credentials = find_credentials_in_file(file_path)
            
            if credentials:
                print(f"      🚨 Encontradas {len(credentials)} credenciales")
                all_credentials.extend(credentials)
                
                # Limpiar credenciales en el archivo
                if clean_credentials_in_file(file_path, credentials):
                    cleaned_files.append(file_path)
                    print(f"      ✅ Credenciales limpiadas")
    
    return all_credentials, cleaned_files

def main():
    print("🚀 Iniciando limpieza de credenciales en n8n-samart888")
    print("=" * 60)
    
    credentials, cleaned_files = scan_repository()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE LIMPIEZA")
    print("=" * 60)
    
    if credentials:
        print(f"🚨 Se encontraron {len(credentials)} credenciales expuestas")
        print(f"🧹 Se limpiaron {len(cleaned_files)} archivos")
        
        print("\n📄 Archivos limpiados:")
        for file in cleaned_files:
            print(f"   ✅ {file}")
        
        print("\n🔍 Credenciales encontradas por tipo:")
        cred_types = {}
        for cred in credentials:
            cred_type = cred['type']
            if cred_type not in cred_types:
                cred_types[cred_type] = 0
            cred_types[cred_type] += 1
        
        for cred_type, count in cred_types.items():
            print(f"   📊 {cred_type}: {count}")
        
        print("\n🔧 PRÓXIMOS PASOS:")
        print("1. Revisar los cambios realizados")
        print("2. Hacer commit de los cambios")
        print("3. Push al repositorio")
        print("4. Verificar que no se rompió funcionalidad")
        
    else:
        print("✅ ¡Excelente! No se encontraron credenciales expuestas")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 
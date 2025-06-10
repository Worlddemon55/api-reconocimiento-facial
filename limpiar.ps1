# Este script limpiará el repositorio de Git de forma definitiva.

# Mensaje de inicio
Write-Host "--- INICIANDO LIMPIEZA DEFINITIVA DE GIT ---" -ForegroundColor Yellow

# 1. Asegurarse de que .gitignore sea perfecto
Write-Host "1. Creando archivo .gitignore..."
Set-Content -Path .gitignore -Value "venv/`n__pycache__/"
Write-Host ".gitignore creado/actualizado."

# 2. Añadir el .gitignore al área de preparación de Git
Write-Host "2. Preparando .gitignore para guardarlo (git add)..."
git add .gitignore
Write-Host ".gitignore listo para ser guardado."

# 3. Guardar el cambio del .gitignore con un commit
Write-Host "3. Guardando .gitignore en el historial (git commit)..."
git commit -m "Asegurar que .gitignore existe y es correcto"
Write-Host "Commit de .gitignore creado."

# 4. Eliminar todo del caché de Git
Write-Host "4. Limpiando el caché de Git (git rm -r --cached .)..."
git rm -r --cached .
Write-Host "Caché limpiado."

# 5. Re-añadir todo, ahora respetando 100% el .gitignore
Write-Host "5. Re-agregando archivos limpios al seguimiento (git add .)..."
git add .
Write-Host "Archivos limpios agregados."

# 6. Guardar los cambios de limpieza con un nuevo commit
Write-Host "6. Creando el commit de limpieza final..."
git commit -m "Limpieza final y forzada del repositorio"
Write-Host "Commit de limpieza creado."

# 7. Forzar la subida de la versión limpia a GitHub
Write-Host "7. Subiendo la versión limpia a GitHub (git push --force)..."
git push --force origin main

Write-Host "--- ¡PROCESO COMPLETADO! ---" -ForegroundColor Green
Write-Host "Por favor, revisa tu página de GitHub ahora. Refresca con Ctrl + F5."
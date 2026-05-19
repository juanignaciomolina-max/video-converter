#!/bin/bash
# Instalador de Video Converter
# Descarga ffmpeg automáticamente según la arquitectura

DIR="$(cd "$(dirname "$0")" && pwd)"
FFMPEG_PATH="$DIR/ffmpeg"

echo "═══════════════════════════════════════"
echo "  Video Converter – Instalador"
echo "═══════════════════════════════════════"
echo ""

# Detectar arquitectura
ARCH=$(uname -m)
echo "🔍 Arquitectura: $ARCH"

# Verificar si ya está instalado
if [ -x "$FFMPEG_PATH" ]; then
    echo "✅ ffmpeg ya instalado en la carpeta"
    "$FFMPEG_PATH" -version 2>&1 | head -1
    echo ""
    echo "Para actualizar, borralo y ejecutá de nuevo:"
    echo "  rm \"$FFMPEG_PATH\" && bash setup.sh"
    exit 0
fi

echo "📥 Descargando ffmpeg..."

# Determinar URL según arquitectura
if [ "$ARCH" = "arm64" ]; then
    URL="https://evermeet.cx/ffmpeg/ffmpeg-7.1-arm64.zip"
else
    URL="https://evermeet.cx/ffmpeg/ffmpeg-7.1.zip"
fi

echo "   $URL"
curl -L -o /tmp/ffmpeg_install.zip "$URL"

if [ $? -ne 0 ]; then
    echo "❌ Error de descarga. Verificá tu conexión a internet."
    exit 1
fi

echo "   Extrayendo..."
cd /tmp
unzip -o ffmpeg_install.zip 2>/dev/null

if [ -f /tmp/ffmpeg ]; then
    cp /tmp/ffmpeg "$FFMPEG_PATH"
    chmod +x "$FFMPEG_PATH"
    rm -f /tmp/ffmpeg /tmp/ffmpeg_install.zip
    echo "✅ ffmpeg instalado correctamente ($(du -h "$FFMPEG_PATH" | cut -f1))"
else
    echo "❌ Error al extraer el archivo"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════"
echo "  Instalación completada."
echo "  Arrastrá cualquier video sobre"
echo "  Convertir Video.app"
echo "═══════════════════════════════════════"
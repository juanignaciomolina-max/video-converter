#!/bin/bash
# Instalador de Video Converter
# Detecta la arquitectura y descarga ffmpeg automáticamente

DIR="$(cd "$(dirname "$0")" && pwd)"
FFMPEG_PATH="$DIR/ffmpeg"
FFPROBE_PATH="$DIR/ffprobe"

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

# Verificar Homebrew
HAVE_BREW=false
if command -v brew &>/dev/null; then
    HAVE_BREW=true
fi

echo ""
echo "Opciones de instalación:"
echo "  1) Descargar ffmpeg estático (auto, recomendado)"
echo "  2) Instalar con Homebrew (si está disponible)"
echo "  3) Salir"
echo ""

read -p "Elegí una opción [1-3]: " OPTION

case $OPTION in
    1)
        echo ""
        echo "📥 Descargando ffmpeg..."
        
        # Determinar URL según arquitectura
        if [ "$ARCH" = "arm64" ]; then
            URL="https://evermeet.cx/ffmpeg/ffmpeg-7.1-arm64.zip"
        else
            URL="https://evermeet.cx/ffmpeg/ffmpeg-7.1.zip"
        fi
        
        echo "   Descargando desde: $URL"
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
            
            # También intentar ffprobe (viene con ffmpeg)
            if [ -f /tmp/ffprobe ]; then
                cp /tmp/ffprobe "$FFPROBE_PATH"
                chmod +x "$FFPROBE_PATH"
            fi
            
            rm -f /tmp/ffmpeg /tmp/ffprobe /tmp/ffmpeg_install.zip
            
            echo "✅ ffmpeg instalado correctamente"
            echo "   $(du -h "$FFMPEG_PATH" | cut -f1)"
        else
            echo "❌ Error al extraer el archivo"
            exit 1
        fi
        ;;
    2)
        if [ "$HAVE_BREW" = true ]; then
            echo ""
            echo "🍺 Instalando ffmpeg con Homebrew..."
            brew install ffmpeg
            
            # Crear symlinks en la carpeta
            BREW_FFMPEG=$(command -v ffmpeg)
            BREW_FFPROBE=$(command -v ffprobe)
            
            if [ -n "$BREW_FFMPEG" ]; then
                ln -sf "$BREW_FFMPEG" "$FFMPEG_PATH"
                echo "   Symlink creado: $FFMPEG_PATH"
            fi
            if [ -n "$BREW_FFPROBE" ]; then
                ln -sf "$BREW_FFPROBE" "$FFPROBE_PATH"
                echo "   Symlink creado: $FFPROBE_PATH"
            fi
        else
            echo "❌ Homebrew no está instalado."
            echo "   Instalalo con:"
            echo '     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            echo "   O elegí la opción 1 para descargar ffmpeg directamente."
            exit 1
        fi
        ;;
    3)
        echo "Saliendo."
        exit 0
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "═══════════════════════════════════════"
echo "  Instalación completada.              "
echo "  Arrastrá videos a Convertir Video.app"
echo "  o usá el acceso directo en el Dock.  "
echo "═══════════════════════════════════════"
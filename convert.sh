#!/bin/bash
# Video Converter – arrastrá uno o más archivos de video sobre este script
# Convierte a H.264 con calidad óptima para Pro Tools

CRF=22
PRESET=medium

# Buscar ffmpeg: primero en la misma carpeta, luego en PATH
DIR="$(cd "$(dirname "$0")" && pwd)"
FFMPEG="$DIR/ffmpeg"
if [ ! -x "$FFMPEG" ]; then
    FFMPEG=$(command -v ffmpeg 2>/dev/null)
fi
if [ -z "$FFMPEG" ] || [ ! -x "$FFMPEG" ]; then
    echo "❌ ffmpeg no encontrado. Corré el instalador: bash setup.sh"
    exit 1
fi

for input in "$@"; do
    if [ ! -f "$input" ]; then
        echo "❌ No existe: $input"
        continue
    fi

    name="${input%.*}"
    output="${name}_h264.mp4"

    echo "🎬 Convirtiendo: $(basename "$input") → $(basename "$output")"

    "$FFMPEG" -y -i "$input" \
        -c:v libx264 -preset "$PRESET" -crf "$CRF" \
        -pix_fmt yuv420p -movflags +faststart \
        -c:a aac -b:a 192k \
        "$output"

    if [ $? -eq 0 ]; then
        orig=$(stat -f%z "$input" 2>/dev/null || stat --format=%s "$input" 2>/dev/null)
        new=$(stat -f%z "$output" 2>/dev/null || stat --format=%s "$output" 2>/dev/null)
        if [ -n "$orig" ] && [ -n "$new" ] && [ "$orig" -gt 0 ]; then
            pct=$(( (100 * (orig - new) / orig) ))
            echo "✅ OK: $(echo "scale=1; $orig/1048576" | bc)MB → $(echo "scale=1; $new/1048576" | bc)MB (${pct}% reducido)"
        else
            echo "✅ OK: $output"
        fi
    else
        echo "❌ Error convirtiendo: $input"
    fi
done

echo ""
echo "═══════════════════════════════════"
echo "  Hecho. Cerrá esta ventana.       "
echo "═══════════════════════════════════"

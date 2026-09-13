import argparse
import os
import re
import sys
import unicodedata

from mutagen.id3 import ID3NoHeaderError, TIT2
from mutagen.mp3 import MP3

TOKENS_LIMPIABLES = {"video", "oficial", "official", "audio", "lyric", "lyrics", "hd"}
GANCHO = {"oficial", "official", "audio", "lyric", "lyrics", "hd"}

SEGMENTO_FINAL_RE = re.compile(r"(.*?)\s*[\(\[]\s*([^)\]]+?)\s*[\)\]]\s*$")


def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode()
    return texto.lower()


def _es_segmento_removible(texto):
    norm = _normalizar(texto)
    tokens = [t for t in re.split(r"[^a-z]+", norm) if t]
    if not tokens:
        return False
    return all(t in TOKENS_LIMPIABLES for t in tokens) and bool(GANCHO & set(tokens))


def limpiar_titulo(titulo):
    base = titulo
    while True:
        m = SEGMENTO_FINAL_RE.search(base)
        if m and _es_segmento_removible(m.group(2)):
            base = m.group(1).rstrip()
        else:
            break
    return base.rstrip() or titulo


def limpiar_archivo(ruta):
    directorio, nombre = os.path.split(ruta)
    base, ext = os.path.splitext(nombre)
    nuevo_base = limpiar_titulo(base)
    if nuevo_base == base:
        return False

    nuevo_nombre = nuevo_base + ext
    nuevo_ruta = os.path.join(directorio, nuevo_nombre)
    if nuevo_ruta != ruta:
        os.rename(ruta, nuevo_ruta)

    _actualizar_titulo_id3(nuevo_ruta, nuevo_base)
    return True


def _actualizar_titulo_id3(ruta, titulo):
    audio = MP3(ruta)
    if audio.tags is None:
        try:
            audio.add_tags()
        except Exception:
            pass
    if audio.tags is not None:
        audio.tags.add(TIT2(encoding=3, text=[titulo]))
        audio.save()


def procesar(directorio="mp3", vista_previa=False):
    if not os.path.isdir(directorio):
        return []

    cambios = []
    for nombre in sorted(os.listdir(directorio)):
        if not nombre.lower().endswith(".mp3"):
            continue
        ruta = os.path.join(directorio, nombre)
        base, ext = os.path.splitext(nombre)
        nuevo_base = limpiar_titulo(base)
        if nuevo_base == base:
            continue
        if not vista_previa:
            limpiar_archivo(ruta)
        cambios.append((nombre, nuevo_base + ext))
    return cambios


def _configurar_consola():
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream.encoding and "utf" not in stream.encoding.lower():
                stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


def main(argv=None):
    _configurar_consola()
    parser = argparse.ArgumentParser(
        description="Limpia títulos de los MP3: elimina partes finales como "
                    "'(Video Oficial)', '(Lyric Video)', '[Official Audio]', '(Official HD Video)'")
    parser.add_argument("--ruta", default="mp3", help="Directorio con los MP3 (default: mp3)")
    parser.add_argument("--vista-previa", action="store_true", help="Solo mostrar cambios, sin aplicarlos")
    args = parser.parse_args(argv)

    cambios = procesar(args.ruta, vista_previa=args.vista_previa)

    if not cambios:
        print("No hay títulos que limpiar.")
        return 0

    modo = "se limpiaría" if args.vista_previa else "limpiado"
    print(f"{len(cambios)} archivo(s) {modo}:")
    for antes, despues in cambios:
        print(f"  {antes}  ->  {despues}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
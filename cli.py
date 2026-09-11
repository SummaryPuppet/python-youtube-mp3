import argparse
import os
import sys

from youtube import YouTubeDownloader


def configurar_consola():
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream.encoding and "utf" not in stream.encoding.lower():
                stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


def construir_parser():
    parser = argparse.ArgumentParser(description="Descarga y convierte videos de YouTube a MP3")
    parser.add_argument("url", nargs="?", help="URL del video a descargar")
    parser.add_argument("--file", "-f", help="Archivo .txt con una lista de URLs (una por línea)")
    parser.add_argument("--ui", action="store_true", help="Abrir interfaz gráfica")
    return parser


def leer_urls(archivo):
    urls = []
    with open(archivo, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea and not linea.startswith("#"):
                urls.append(linea)
    return urls


def procesar(urls):
    os.makedirs("mp3", exist_ok=True)
    correctas = 0
    fallidas = []
    pendientes = []

    try:
        for i, url in enumerate(urls):
            print(f"\nProcesando: {url}")
            try:
                descargador = YouTubeDownloader(url)
                info = descargador.download()
                print(descargador.describir(info))
                correctas += 1
            except Exception as e:
                print(f"Error procesando {url}: {e}")
                fallidas.append(url)
        pendientes = []
    except KeyboardInterrupt:
        print("\nCancelado por el usuario (Ctrl+C).")
        pendientes = urls[i + 1:]

    print("\n" + "=" * 40)
    print(f"Conversiones exitosas: {correctas}")
    print(f"Fallidas: {len(fallidas)}")
    for url in fallidas:
        print(f"  - {url}")
    if pendientes:
        print(f"Pendientes (no procesadas): {len(pendientes)}")
        for url in pendientes:
            print(f"  - {url}")


def main(argv=None):
    configurar_consola()
    parser = construir_parser()
    args = parser.parse_args(argv)

    if args.ui:
        from gui import run
        try:
            run()
        except KeyboardInterrupt:
            print("\nInterfaz cerrada (Ctrl+C).", file=sys.stderr)
            return 130
        return 0

    if args.file and args.url:
        parser.error("Indica --file o una URL, no ambos")

    try:
        if args.file:
            try:
                urls = leer_urls(args.file)
            except OSError as e:
                print(f"No se pudo leer el archivo: {e}", file=sys.stderr)
                return 1
            if not urls:
                print("El archivo no contiene URLs válidas", file=sys.stderr)
                return 1
            procesar(urls)
        elif args.url:
            procesar([args.url])
        else:
            parser.error("Indica --file/-f <archivo.txt> o una URL")
    except KeyboardInterrupt:
        print("\nOperación interrumpida.", file=sys.stderr)
        return 130

    return 0
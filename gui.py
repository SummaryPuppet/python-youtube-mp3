import os
import queue
import threading
import tkinter as tk

import customtkinter as ctk

from youtube import YouTubeDownloader

FAMILIA_FUENTE = "Segoe UI"


class VentanaDescarga(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube → MP3")
        self.geometry("620x720")
        self.minsize(520, 600)
        self.urls = []
        self.msg_queue = queue.Queue()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._construir_cabecera()
        self._construir_entrada()
        self._construir_lista()
        self._construir_progreso()
        self._construir_pie()

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.after(100, self.drenar_cola)

    def _construir_cabecera(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 6))
        ctk.CTkLabel(
            header,
            text="\U0001F3B5  YouTube \u2192 MP3",
            font=ctk.CTkFont(family=FAMILIA_FUENTE, size=26, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Descarga el audio y convierte a MP3 con metadatos y carátula incrustados",
            font=ctk.CTkFont(family=FAMILIA_FUENTE, size=13),
            text_color=("gray40", "gray60"),
        ).pack(anchor="w", pady=(2, 0))

    def _construir_entrada(self):
        marco = ctk.CTkFrame(self, fg_color="transparent")
        marco.grid(row=1, column=0, sticky="ew", padx=20, pady=6)
        marco.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(
            marco,
            placeholder_text="https://www.youtube.com/watch?v=\u2026",
            font=ctk.CTkFont(family=FAMILIA_FUENTE, size=14),
            height=38,
        )
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", lambda e: self.agregar())

        self.btn_agregar = ctk.CTkButton(
            marco,
            text="Agregar",
            width=90,
            height=38,
            font=ctk.CTkFont(family=FAMILIA_FUENTE, size=14, weight="bold"),
            command=self.agregar,
        )
        self.btn_agregar.grid(row=0, column=1, padx=(8, 0))

        ctk.CTkButton(
            marco,
            text="Pegar de portapapeles",
            width=170,
            height=34,
            font=ctk.CTkFont(family=FAMILIA_FUENTE, size=13),
            fg_color="transparent",
            border_width=1,
            command=self.pegar_portapapeles,
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

    def _construir_lista(self):
        marco = ctk.CTkFrame(self, corner_radius=10)
        marco.grid(row=2, column=0, sticky="nsew", padx=20, pady=8)
        marco.grid_columnconfigure(0, weight=1)
        marco.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(
            marco,
            text="URLs a descargar",
            font=ctk.CTkFont(family=FAMILIA_FUENTE, size=13, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 6))

        self.filas = ctk.CTkScrollableFrame(marco, corner_radius=0, fg_color="transparent")
        self.filas.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.filas.grid_columnconfigure(0, weight=1)

        self.lbl_vacio = ctk.CTkLabel(
            self.filas,
            text="Aún no hay URLs en la lista\u2026",
            font=ctk.CTkFont(family=FAMILIA_FUENTE, size=13),
            text_color=("gray40", "gray55"),
        )
        self._refrescar_lista()

    def _construir_progreso(self):
        marco = ctk.CTkFrame(self, fg_color="transparent")
        marco.grid(row=3, column=0, sticky="nsew", padx=20, pady=6)
        marco.grid_columnconfigure(0, weight=1)
        marco.grid_rowconfigure(1, weight=1)

        self.lbl_progreso = ctk.CTkLabel(
            marco,
            text="",
            font=ctk.CTkFont(family=FAMILIA_FUENTE, size=12),
            text_color=("gray40", "gray60"),
            anchor="w",
        )
        self.lbl_progreso.grid(row=0, column=0, sticky="ew")

        self.barra = ctk.CTkProgressBar(marco, height=10, corner_radius=5)
        self.barra.grid(row=1, column=0, sticky="ew", pady=(4, 8))
        self.barra.set(0)

        self.log = ctk.CTkTextbox(marco, corner_radius=10, font=ctk.CTkFont(family="Consolas", size=12))
        self.log.grid(row=2, column=0, sticky="nsew")
        self.log.configure(state="disabled")

    def _construir_pie(self):
        marco = ctk.CTkFrame(self, fg_color="transparent")
        marco.grid(row=4, column=0, sticky="ew", padx=20, pady=(2, 16))
        marco.grid_columnconfigure(0, weight=1)

        self.btn_iniciar = ctk.CTkButton(
            marco,
            text="Iniciar descarga",
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(family=FAMILIA_FUENTE, size=15, weight="bold"),
            command=self.iniciar,
        )
        self.btn_iniciar.grid(row=0, column=0, columnspan=2, sticky="ew")

        ctk.CTkLabel(
            marco,
            text="Salida: mp3/",
            font=ctk.CTkFont(family=FAMILIA_FUENTE, size=12),
            text_color=("gray40", "gray60"),
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

    def _refrescar_lista(self):
        for widget in self.filas.winfo_children():
            if widget is not self.lbl_vacio:
                widget.destroy()

        if not self.urls:
            self.lbl_vacio.pack(anchor="w", padx=8, pady=14)
            return

        self.lbl_vacio.pack_forget()
        for i, url in enumerate(self.urls):
            fila = ctk.CTkFrame(self.filas, corner_radius=8)
            fila.grid(row=i, column=0, sticky="ew", pady=3)
            fila.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                fila,
                text=url,
                font=ctk.CTkFont(family=FAMILIA_FUENTE, size=13),
                anchor="w",
                wraplength=430,
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=6)

            ctk.CTkButton(
                fila,
                text="\u2715",
                width=28,
                height=28,
                corner_radius=6,
                fg_color="transparent",
                hover_color=("gray80", "gray25"),
                font=ctk.CTkFont(family=FAMILIA_FUENTE, size=13),
                command=lambda idx=i: self.quitar(idx),
            ).grid(row=0, column=1, padx=(4, 8))

    def agregar(self):
        url = self.entry.get().strip()
        if url and url not in self.urls:
            self.urls.append(url)
            self._refrescar_lista()
        self.entry.delete(0, "end")

    def quitar(self, indice):
        del self.urls[indice]
        self._refrescar_lista()

    def pegar_portapapeles(self):
        try:
            texto = self.clipboard_get()
        except tk.TclError:
            self.escribir_log("No se pudo leer el portapapeles.\n")
            return
        agregadas = 0
        for linea in texto.splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and linea not in self.urls:
                self.urls.append(linea)
                agregadas += 1
        self._refrescar_lista()
        if agregadas:
            self.escribir_log(f"{agregadas} URL(s) pegadas desde el portapapeles.\n")

    def iniciar(self):
        if not self.urls:
            tk.messagebox.showwarning("Sin URLs", "Agrega al menos una URL a la lista.")
            return
        self.btn_iniciar.configure(state="disabled")
        self.btn_agregar.configure(state="disabled")
        self.barra.set(0)
        self.lbl_progreso.configure(text="Comenzando\u2026")
        threading.Thread(target=self.procesar, daemon=True).start()

    def procesar(self):
        os.makedirs("mp3", exist_ok=True)
        urls = list(self.urls)
        total = len(urls)
        correctas = 0
        for i, url in enumerate(urls, start=1):
            self.msg_queue.put(("log", f"Procesando ({i}/{total}): {url}\n"))
            try:
                descargador = YouTubeDownloader(url)
                info = descargador.download()
                self.msg_queue.put(("log", f"\u2713 {descargador.describir(info)}\n"))
                correctas += 1
            except Exception as e:
                self.msg_queue.put(("log", f"\u2717 ERROR en {url}: {e}\n"))
            self.msg_queue.put(("avance", (correctas, i, total)))
        self.msg_queue.put(("fin", (correctas, total - correctas)))

    def drenar_cola(self):
        try:
            while True:
                tipo, dato = self.msg_queue.get_nowait()
                if tipo == "log":
                    self.escribir_log(dato)
                elif tipo == "avance":
                    correctas, hechas, total = dato
                    self.barra.set(hechas / total)
                    self.lbl_progreso.configure(text=f"{correctas} correctas · {hechas}/{total}")
                else:
                    correctas, fallidas = dato
                    color = ("green4", "green3") if fallidas == 0 else ("darkred", "red3")
                    self.escribir_log(
                        f"\n{'=' * 40}\nFinalizado: {correctas} correctas, {fallidas} fallidas\n",
                        color,
                    )
                    self.barra.set(1)
                    self.lbl_progreso.configure(text="Finalizado")
                    self.btn_iniciar.configure(state="normal")
                    self.btn_agregar.configure(state="normal")
        except queue.Empty:
            pass
        self.after(100, self.drenar_cola)

    def escribir_log(self, texto, color=None):
        if isinstance(color, (tuple, list)):
            color = color[0] if ctk.get_appearance_mode().lower() == "dark" else color[1]
        self.log.configure(state="normal")
        inicio = self.log.index("end-1c")
        self.log.insert("end", texto)
        self.log.see("end")
        if color:
            nombre = "color_" + str(hash(color) & 0xFFFFFF)
            self.log.tag_add(nombre, inicio, "end")
            self.log.tag_config(nombre, foreground=color)
        self.log.configure(state="disabled")


def run():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    app = VentanaDescarga()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.destroy()
        raise
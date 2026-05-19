#!/usr/bin/env python3
import os, sys, subprocess, threading, json
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

VERSION = "1.2"

try:
    from tkinterdnd2 import TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def find_bin(name):
    local = os.path.join(SCRIPT_DIR, name)
    if os.path.isfile(local) and os.access(local, os.X_OK):
        return local
    which = subprocess.run(["which", name], capture_output=True, text=True)
    return which.stdout.strip() if which.returncode == 0 else None


FFMPEG = find_bin("ffmpeg")
FFPROBE = find_bin("ffprobe")


def get_video_info(path):
    if not FFPROBE:
        return None
    try:
        r = subprocess.run([FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path],
                           capture_output=True, text=True, timeout=30)
        data = json.loads(r.stdout)
        for s in data.get("streams", []):
            if s.get("codec_type") == "video":
                f = s.get("width", "?"), s.get("height", "?"), s.get("codec_name", "?")
                try:
                    num, den = s.get("r_frame_rate", "0/1").split("/")
                    fps = float(num) / float(den)
                except:
                    fps = 0
                return {"w": f[0], "h": f[1], "codec": f[2], "fps": fps}
    except:
        pass
    return None


def convert_video(inp, out, crf, preset, progress):
    if not FFMPEG:
        return False
    dur = None
    if FFPROBE:
        try:
            r = subprocess.run([FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", inp],
                               capture_output=True, text=True, timeout=30)
            dur = float(json.loads(r.stdout)["format"].get("duration", 0))
        except:
            pass

    cmd = [FFMPEG, "-y", "-i", inp, "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k",
           "-progress", "pipe:1", out]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    for line in proc.stdout:
        if line.startswith("out_time="):
            try:
                h, m, s = line.strip().split("=", 1)[1].split(":")
                cur = int(h) * 3600 + int(m) * 60 + float(s)
                if dur and dur > 0:
                    progress(min(cur / dur * 100, 99))
            except:
                pass
    proc.wait()
    if dur and dur > 0:
        progress(100)
    return proc.returncode == 0


class App:
    def __init__(self):
        if HAS_DND:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
        self.root.title("Video Converter – H.264")
        self.root.geometry("540x400")
        self.root.resizable(False, False)

        self.path = tk.StringVar()
        self.crf = tk.IntVar(value=22)
        self.preset = tk.StringVar(value="medium")

        self._build()
        if HAS_DND:
            self._setup_dnd()
        self.root.mainloop()

    def _build(self):
        m = ttk.Frame(self.root, padding=16)
        m.pack(fill="both", expand=True)

        ttk.Label(m, text="Video Converter", font=("Helvetica", 16, "bold")).pack(anchor="w")
        ttk.Label(m, text="Convertí videos a H.264 para reducir peso", foreground="#666").pack(anchor="w", pady=(0, 12))

        # File
        f = ttk.LabelFrame(m, text="Archivo", padding=8)
        f.pack(fill="x", pady=(0, 8))
        r1 = ttk.Frame(f)
        r1.pack(fill="x")
        ttk.Entry(r1, textvariable=self.path, state="readonly").pack(side="left", fill="x", expand=True)
        ttk.Button(r1, text="Seleccionar", command=self._pick).pack(side="right", padx=(8, 0))
        self.info = ttk.Label(f, text="", foreground="#555")
        self.info.pack(anchor="w", pady=(4, 0))

        # Settings
        s = ttk.LabelFrame(m, text="Ajustes", padding=8)
        s.pack(fill="x", pady=(0, 8))

        r2 = ttk.Frame(s)
        r2.pack(fill="x")
        ttk.Label(r2, text="Calidad:").pack(side="left")
        ttk.Label(r2, textvariable=self.crf, width=3).pack(side="left", padx=(4, 0))
        ttk.Scale(r2, from_=18, to=30, variable=self.crf, orient="horizontal", length=180).pack(side="left", padx=(4, 0))
        ttk.Label(r2, text="↓ calidad  compresión →", foreground="#999", font=("", 8)).pack(side="left", padx=(8, 0))

        r3 = ttk.Frame(s)
        r3.pack(fill="x", pady=(4, 0))
        ttk.Label(r3, text="Velocidad:").pack(side="left")
        c = ttk.Combobox(r3, textvariable=self.preset,
                         values=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"],
                         state="readonly", width=12)
        c.pack(side="left", padx=(4, 0))
        ttk.Label(r3, text="más lento = mejor compresión", foreground="#999", font=("", 8)).pack(side="left", padx=(8, 0))

        # Presets quick
        rp = ttk.Frame(s)
        rp.pack(fill="x", pady=(4, 0))
        ttk.Label(rp, text="Presets:").pack(side="left")
        ttk.Button(rp, text="Máxima calidad", command=lambda: (self.crf.set(18), self.preset.set("slow"))).pack(side="left", padx=(4, 0))
        ttk.Button(rp, text="Balanceado", command=lambda: (self.crf.set(22), self.preset.set("medium"))).pack(side="left", padx=(4, 0))
        ttk.Button(rp, text="Máxima compresión", command=lambda: (self.crf.set(28), self.preset.set("fast"))).pack(side="left", padx=(4, 0))

        # Progress
        p = ttk.LabelFrame(m, text="Progreso", padding=8)
        p.pack(fill="x", pady=(0, 8))
        self.progress = ttk.Progressbar(p, mode="determinate")
        self.progress.pack(fill="x")
        self.status = ttk.Label(p, text="Listo", foreground="#666")
        self.status.pack(anchor="w", pady=(4, 0))

        self.btn = ttk.Button(m, text="Convertir a H.264", command=self._convert)
        self.btn.pack(pady=(0, 4))

        ttk.Label(m, text=f"v{VERSION}  •  ffmpeg  •  arrastrá videos a la ventana", foreground="#aaa", font=("", 8)).pack()

    def _setup_dnd(self):
        self.root.drop_target_register("*")
        self.root.dnd_bind("<<Drop>>", self._on_drop)

    def _on_drop(self, e):
        files = self.root.tk.splitlist(e.data)
        for f in files:
            if os.path.isfile(f):
                self._set_file(f)
                break

    def _pick(self):
        p = filedialog.askopenfilename(title="Seleccionar video", filetypes=[("Video", "*.mp4 *.mov *.avi *.mkv *.webm *.mxf *.m4v"), ("Todos", "*.*")])
        if p:
            self._set_file(p)

    def _set_file(self, p):
        self.path.set(p)
        info = get_video_info(p)
        if info:
            sz = os.path.getsize(p) / 1048576
            self.info.config(text=f"{info['w']}×{info['h']}  •  {info['codec']}  •  {info['fps']:.1f} fps  •  {sz:.1f} MB")
        else:
            self.info.config(text="No se pudo leer info del video")

    def _convert(self):
        if not self.path.get():
            messagebox.showwarning("Sin archivo", "Seleccioná un archivo primero.")
            return
        if not FFMPEG:
            messagebox.showerror("ffmpeg no encontrado",
                                 "No se encuentra ffmpeg.\n\n"
                                 "Ejecutá el instalador:\n"
                                 "   Terminal: bash setup.sh\n\n"
                                 "O descargalo de: https://evermeet.cx/ffmpeg/")
            return
        inp = self.path.get()
        out = os.path.splitext(inp)[0] + "_h264.mp4"
        if os.path.exists(out) and not messagebox.askyesno("Sobrescribir", f"¿Sobrescribir?\n{out}"):
            return
        self.btn.config(state="disabled")
        self.status.config(text="Procesando…")
        self.progress["value"] = 0

        def cb(pct):
            self.root.after(0, lambda: self.progress.config(value=pct))
            self.root.after(0, lambda: self.status.config(text=f"Procesando… {pct:.0f}%"))

        def run():
            ok = convert_video(inp, out, self.crf.get(), self.preset.get(), cb)
            self.root.after(0, self._done, ok, out)

        threading.Thread(target=run, daemon=True).start()

    def _done(self, ok, out):
        self.btn.config(state="normal")
        if ok:
            orig = os.path.getsize(self.path.get())
            new = os.path.getsize(out)
            ratio = (1 - new / orig) * 100
            self.status.config(text=f"✅ {orig/1048576:.1f}MB → {new/1048576:.1f}MB ({ratio:.0f}% reducción)")
            self.progress["value"] = 100
            messagebox.showinfo("Completado", f"Video convertido:\n{out}\n\nReducción: {ratio:.0f}%")
        else:
            self.status.config(text="❌ Error durante la conversión")
            messagebox.showerror("Error", "Ocurrió un error al convertir.")


if __name__ == "__main__":
    App()

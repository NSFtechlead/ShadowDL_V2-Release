import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import sv_ttk
except ImportError:
    sv_ttk = None

from shadowdl import APP_NAME
from shadowdl.command import DownloadOptions, build_ytdlp_command, format_command
from shadowdl.config import BROWSERS, MODES, load_config, save_config
from shadowdl.paths import ytdlp_cmd_base
from shadowdl.process import hidden_startup_options, terminate_process_tree


class YtDlpGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("780x560")
        self.minsize(680, 460)

        if sv_ttk is not None:
            try:
                sv_ttk.set_theme("dark")
            except tk.TclError:
                pass

        self.config_data = load_config()
        self.proc = None
        self.proc_lock = threading.Lock()
        self.running = False

        self.url_var = tk.StringVar()
        self.outdir_var = tk.StringVar(value=self.config_data["outdir"])
        self.mode_var = tk.StringVar(value=self.config_data["mode"])
        self.playlist_var = tk.BooleanVar(value=self.config_data["playlist"])
        self.use_browser_cookies = tk.BooleanVar(value=self.config_data["use_browser_cookies"])
        self.browser_var = tk.StringVar(value=self.config_data["browser"])
        self.safe_mode_var = tk.BooleanVar(value=self.config_data["safe_mode"])
        self.status_var = tk.StringVar(value="Prêt.")

        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Return>", lambda _event: self.start_download())
        self.bind("<Escape>", lambda _event: self.cancel_download())

    def build_ui(self):
        main = ttk.Frame(self, padding=12)
        main.grid(row=0, column=0, sticky="nsew")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(7, weight=1)

        ttk.Label(main, text="URL :").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=6)
        ttk.Entry(main, textvariable=self.url_var).grid(
            row=0, column=1, columnspan=3, sticky="ew", pady=6
        )

        ttk.Label(main, text="Destination :").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=6)
        ttk.Entry(main, textvariable=self.outdir_var).grid(
            row=1, column=1, columnspan=2, sticky="ew", pady=6
        )
        ttk.Button(main, text="Parcourir…", command=self.browse_dir).grid(
            row=1, column=3, sticky="ew", padx=(8, 0), pady=6
        )

        ttk.Label(main, text="Mode :").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=6)
        ttk.Combobox(main, textvariable=self.mode_var, state="readonly", values=MODES).grid(
            row=2, column=1, sticky="ew", pady=6
        )
        ttk.Checkbutton(
            main,
            text="Playlist",
            variable=self.playlist_var,
            command=self.persist_config,
        ).grid(row=2, column=2, sticky="w", padx=(12, 0), pady=6)

        ttk.Checkbutton(
            main,
            text="Cookies navigateur",
            variable=self.use_browser_cookies,
            command=self.persist_config,
        ).grid(row=3, column=0, sticky="w", pady=6)
        ttk.Combobox(main, textvariable=self.browser_var, state="readonly", values=BROWSERS).grid(
            row=3, column=1, sticky="ew", pady=6
        )
        ttk.Checkbutton(
            main,
            text="Mode safe",
            variable=self.safe_mode_var,
            command=self.persist_config,
        ).grid(row=3, column=2, sticky="w", padx=(12, 0), pady=6)

        actions = ttk.Frame(main)
        actions.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(8, 4))
        actions.columnconfigure(0, weight=1)

        self.update_btn = ttk.Button(actions, text="Mettre à jour yt-dlp", command=self.start_ytdlp_update)
        self.update_btn.grid(row=0, column=0, sticky="w")
        self.start_btn = ttk.Button(actions, text="Télécharger", command=self.start_download)
        self.start_btn.grid(row=0, column=1, padx=(8, 0))
        self.cancel_btn = ttk.Button(actions, text="Annuler", command=self.cancel_download, state="disabled")
        self.cancel_btn.grid(row=0, column=2, padx=(8, 0))

        ttk.Label(main, textvariable=self.status_var).grid(row=5, column=0, columnspan=4, sticky="w", pady=(4, 8))
        ttk.Label(main, text="Journal :").grid(row=6, column=0, sticky="w", pady=(0, 4))

        self.log = tk.Text(main, height=18, wrap="word")
        self.log.grid(row=7, column=0, columnspan=3, sticky="nsew")
        self.scroll = ttk.Scrollbar(main, command=self.log.yview)
        self.scroll.grid(row=7, column=3, sticky="ns", padx=(8, 0))
        self.log.configure(yscrollcommand=self.scroll.set)

    def persist_config(self):
        self.config_data["outdir"] = self.outdir_var.get().strip()
        self.config_data["mode"] = self.mode_var.get()
        self.config_data["playlist"] = self.playlist_var.get()
        self.config_data["safe_mode"] = self.safe_mode_var.get()
        self.config_data["browser"] = self.browser_var.get()
        self.config_data["use_browser_cookies"] = self.use_browser_cookies.get()
        save_config(self.config_data)

    def browse_dir(self):
        initial = self.outdir_var.get().strip()
        if not os.path.isdir(initial):
            initial = None
        path = filedialog.askdirectory(initialdir=initial)
        if path:
            self.outdir_var.set(path)
            self.persist_config()

    def append_log(self, text):
        self.log.insert(tk.END, text)
        self.log.see(tk.END)

    def queue_log(self, text):
        try:
            self.after(0, self.append_log, text)
        except tk.TclError:
            pass

    def set_running(self, running, can_cancel=True):
        self.running = running
        self.start_btn.configure(state="disabled" if running else "normal")
        self.update_btn.configure(state="disabled" if running else "normal")
        self.cancel_btn.configure(state="normal" if running and can_cancel else "disabled")
        self.status_var.set("Traitement en cours…" if running else "Prêt.")

    def build_download_command(self, url, outdir, mode, allow_playlist):
        return build_ytdlp_command(
            DownloadOptions(
                url=url,
                outdir=outdir,
                mode=mode,
                allow_playlist=allow_playlist,
                use_browser_cookies=self.use_browser_cookies.get(),
                browser=self.browser_var.get(),
                safe_mode=self.safe_mode_var.get(),
            )
        )

    def start_download(self):
        if self.running:
            return

        url = self.url_var.get().strip()
        outdir = self.outdir_var.get().strip()
        mode = self.mode_var.get()

        if not url:
            messagebox.showerror("Erreur", "Merci de coller une URL.")
            return
        if not outdir:
            messagebox.showerror("Erreur", "Merci de choisir un dossier de destination.")
            return

        try:
            os.makedirs(outdir, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("Destination invalide", str(exc))
            return

        self.persist_config()

        try:
            cmd = self.build_download_command(url, outdir, mode, self.playlist_var.get())
        except FileNotFoundError as exc:
            messagebox.showerror("yt-dlp manquant", str(exc))
            return

        self.log.delete("1.0", tk.END)
        self.append_log("Commande : " + format_command(cmd) + "\n\n")
        self.set_running(True)
        threading.Thread(target=self.run_proc, args=(cmd,), daemon=True).start()

    def start_ytdlp_update(self):
        if self.running:
            return

        try:
            cmd = ytdlp_cmd_base() + ["-U"]
        except FileNotFoundError as exc:
            messagebox.showerror("yt-dlp manquant", str(exc))
            return

        self.log.delete("1.0", tk.END)
        self.append_log("Commande : " + format_command(cmd) + "\n\n")
        self.set_running(True, can_cancel=False)
        threading.Thread(target=self.run_proc, args=(cmd,), daemon=True).start()

    def cancel_download(self):
        with self.proc_lock:
            proc = self.proc

        if proc and proc.poll() is None:
            self.append_log("\nAnnulation en cours…\n")
            try:
                terminate_process_tree(proc)
            except Exception as exc:
                self.append_log(f"\nErreur à l’annulation : {exc}\n")

        self.set_running(False)

    def run_proc(self, cmd):
        try:
            startupinfo, creationflags = hidden_startup_options()
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                startupinfo=startupinfo,
                creationflags=creationflags,
            )
            with self.proc_lock:
                self.proc = proc

            if proc.stdout is not None:
                with proc.stdout:
                    for line in iter(proc.stdout.readline, ""):
                        if not line:
                            break
                        self.queue_log(line)

            rc = proc.wait()
            if rc == 0:
                self.queue_log("\nTerminé.\n")
            else:
                self.queue_log(f"\nTerminé avec un code d’erreur {rc}.\n")

        except FileNotFoundError:
            self.queue_log(
                "\nyt-dlp introuvable. Place 'yt-dlp.exe' à côté de l'exécutable "
                "ou installe-le avec : py -m pip install -U \"yt-dlp[default]\"\n"
            )
        except Exception as exc:
            self.queue_log(f"\nErreur : {exc}\n")
        finally:
            with self.proc_lock:
                self.proc = None
            try:
                self.after(0, self.set_running, False)
            except tk.TclError:
                pass

    def on_close(self):
        if self.running:
            if not messagebox.askyesno("Quitter", "Un traitement est en cours. Voulez-vous l’annuler et quitter ?"):
                return
            self.cancel_download()
        self.persist_config()
        self.destroy()


def main():
    app = YtDlpGUI()
    app.mainloop()

# Développement de ShadowDL

## Structure

- `src/shadowdl/` : application principale
- `tests/` : tests unitaires
- `scripts/prepare-runtime.ps1` : télécharge et vérifie les dépendances binaires officielles
- `scripts/build.ps1` : construit l'application Windows avec PyInstaller
- `scripts/test.ps1` : lance les tests

## Prérequis

- Windows
- Python 3.11+
- `uv`

## Commandes utiles

### Lancer l'application en mode développement

```powershell
uv run python .\main.py
```

### Lancer les tests

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

### Construire le binaire Windows

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Clean
```

## Confiance sur les binaires

Le script `prepare-runtime.ps1` :

- télécharge `yt-dlp.exe` depuis la release officielle GitHub
- télécharge l'archive FFmpeg officielle depuis gyan.dev
- vérifie les checksums avant empaquetage
- n'intègre que les fichiers nécessaires (`yt-dlp.exe`, `ffmpeg.exe`, `ffprobe.exe`)

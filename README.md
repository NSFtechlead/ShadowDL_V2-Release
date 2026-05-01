# ShadowDL

ShadowDL est une application Windows simple pour télécharger de la vidéo ou de l'audio avec `yt-dlp` et `FFmpeg`.

## Pour les utilisateurs

- Téléchargez uniquement les fichiers publiés dans l'onglet **Releases** du dépôt GitHub.
- Les versions Windows sont générées automatiquement par **GitHub Actions** à partir des sources du dépôt.
- Le dépôt Git ne stocke plus les binaires de build ni les gros exécutables tiers.

## Ce que contient une release

La release Windows inclut :

- `ShadowDL_V2.3.exe`
- `yt-dlp.exe`
- `ffmpeg.exe` et `ffprobe.exe`

Ces dépendances sont récupérées pendant le build depuis leurs sources officielles, puis vérifiées avant empaquetage.

## Transparence et confiance

- le code source de l'application est dans `src/shadowdl/`
- les tests unitaires sont dans `tests/`
- le build Windows est décrit dans `ShadowDL.spec`
- les automatisations GitHub Actions sont dans `.github/workflows/`

## Pour les contributeurs

Si vous souhaitez reconstruire l'application localement ou comprendre le pipeline technique, consultez `DEVELOPMENT.md`.

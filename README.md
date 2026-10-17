# Ahmed's art shop

A touch-friendly drawing app made with Python and Kivy.

## Features
- Touch drawing
- 12 colors
- Adjustable brush size
- Eraser
- Undo / redo
- Different paper/background colors
- Save artwork as PNG in the app's private storage
- New canvas confirmation dialog

## Android build (Buildozer)
Use Linux, WSL, or GitHub Actions with Buildozer installed.

1. Put `main.py` and `buildozer.spec` in the same project root.
2. Run:
   ```bash
   buildozer -v android debug
   ```
3. The APK is normally created in the `bin/` folder.

If building through GitHub Actions, make sure the workflow runs `buildozer` from the directory containing `buildozer.spec`.

## Run on desktop
Install Python 3 and Kivy, then run:
```bash
python main.py
```

## Note about saving
For reliability across Android versions, PNGs are saved to the app's private storage under `user_data_dir/artworks`. They remain accessible to the app; adding Android's system photo picker/export flow can be a separate upgrade.

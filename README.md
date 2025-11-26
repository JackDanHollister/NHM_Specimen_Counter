# NHM Specimen Counter (internal)

Designed to count specimens in drawers to support NHC auditing and other counting tasks within the NHM. Provides a Flask-based internal web UI for uploading images and running the YOLO counting script.

## Start the service

From the project directory:
```bash
cd /home/appuser/yolo
./start_server.sh
```

Manual start:
```bash
cd /home/appuser/yolo
/usr/local/bin/python app.py
```

The service listens on port 5000 for internal use (no public tunneling).

## How it works

1. Upload up to 10 images via the web page.
2. The YOLO counting script (`run_count_specimens_with_counts.py`) processes them and writes results.
3. Download a zip with annotated images plus summary text/CSV.
4. Old uploads are cleaned before each run.

## File structure

```
yolo/
├── app.py                     # Flask web server
├── start_server.sh            # Startup script for the server
├── run_count_specimens_with_counts.py  # Counting script
├── run_count_specimens_inference.py    # Standalone inference helper
├── best.pt                    # Trained model weights
├── templates/                 # Web pages
│   ├── upload.html
│   ├── processing.html
│   └── results.html
├── static/                    # Generated zip files
├── yolo_count_specimens/
│   └── images_to_test/        # Uploaded images
└── shareable_results/         # YOLO outputs (annotated images, summaries)
```

## Troubleshooting

- Ensure `best.pt` exists at the project root.
- Ensure `yolo_count_specimens/images_to_test/` and `shareable_results/` are writable.
- To test the counting script directly:
  ```bash
  cd /home/appuser/yolo
  /usr/local/bin/python run_count_specimens_with_counts.py
  ```

## Cleanup

```bash
cd /home/appuser/yolo
rm -f yolo_count_specimens/images_to_test/*
rm -rf shareable_results/specimen_counts_*
rm -f static/*.zip
```

# YOLO Specimen Counter Web Service

## ✅ Setup Complete!

Your YOLO specimen counter is now ready to run as a web service accessible from phones!

## 🚀 How to Start the Service

### Option 1: Use the startup script
```bash
cd ~/Desktop/yolo
./start_server.sh
```

### Option 2: Manual start
```bash
cd ~/Desktop/yolo
conda activate yolo
python app.py
```

## 📱 Access from Phone

### Local Testing (same WiFi network):
- Find your Pi's IP address: `hostname -I`
- Visit: `http://[PI_IP_ADDRESS]:5000`

### Internet Access (via ngrok):
1. **Install ngrok** (if not already installed):
   ```bash
   # Download and install ngrok from https://ngrok.com/download
   ```

2. **Start ngrok tunnel** (in a separate terminal):
   ```bash
   ngrok http 5000
   ```

3. **Share the https URL** with users - they can access it from anywhere!

## 🔧 How It Works

1. **Upload**: Users drag-and-drop up to 10 images on the web page
2. **Process**: Your existing YOLO script runs automatically
3. **Download**: Users get a zip file with:
   - Annotated images (with detection boxes)
   - Summary CSV and text files
4. **Cleanup**: Old uploads are automatically removed

## 📁 File Structure

```
yolo/
├── app.py                    # Flask web server
├── start_server.sh          # Startup script
├── run_count_specimens...py  # Your original YOLO script (unchanged)
├── best.pt                  # Your trained model
├── templates/               # Web pages
│   ├── upload.html         # Main upload page
│   ├── processing.html     # Progress page
│   └── results.html        # Results & download page
├── static/                 # Generated zip files
├── yolo_count_specimens/   
│   └── images_to_test/     # Uploaded images go here
└── shareable_results/      # YOLO output goes here
```

## 🛠️ Troubleshooting

### If the server won't start:
```bash
cd ~/Desktop/yolo
conda activate yolo
pip install flask
python app.py
```

### If uploads fail:
- Check that `yolo_count_specimens/images_to_test/` exists
- Ensure the directory is writable

### If processing fails:
- Test your original script manually:
  ```bash
  python run_count_specimens_with_counts.py
  ```

## 🔄 Starting Fresh

To clear everything and start over:
```bash
cd ~/Desktop/yolo
rm -f yolo_count_specimens/images_to_test/*
rm -rf shareable_results/specimen_counts_*
rm -f static/*.zip
```

## 🎯 Ready to Use!

Your proof-of-concept specimen counter web service is complete and ready for testing. Users can now upload images from their phones and get AI-powered specimen counts back instantly!

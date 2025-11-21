#!/usr/bin/env python3
"""
YOLO Count Specimens - Enhanced Inference with Count Display
Creates annotated images with specimen counts displayed prominently
Saves to a shareable folder structure

Usage: python scripts/run_count_specimens_with_counts.py
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from datetime import datetime
import shutil

def draw_count_banner(image, count, confidence_avg=None):
    """
    Draw a banner at the top of the image showing specimen count
    """
    height, width = image.shape[:2]
    
    # Banner configuration
    banner_height = max(80, int(height * 0.06))  # Adaptive banner height
    font_scale = max(1.5, banner_height / 50)    # Adaptive font size
    thickness = max(2, int(banner_height / 20))   # Adaptive thickness
    
    # Create banner background (semi-transparent dark overlay)
    overlay = image.copy()
    cv2.rectangle(overlay, (0, 0), (width, banner_height), (0, 0, 0), -1)
    image = cv2.addWeighted(image, 0.7, overlay, 0.3, 0)
    
    # Count text
    count_text = f"Specimens Detected: {count}"
    
    # Calculate text size and position
    (text_width, text_height), baseline = cv2.getTextSize(
        count_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
    )
    
    text_x = (width - text_width) // 2
    text_y = (banner_height + text_height) // 2
    
    # Draw white text with black outline for visibility
    cv2.putText(image, count_text, (text_x, text_y), 
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness + 2)
    cv2.putText(image, count_text, (text_x, text_y), 
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
    
    # Add confidence info if available
    if confidence_avg is not None:
        conf_text = f"Avg Confidence: {confidence_avg:.1%}"
        (conf_width, conf_height), _ = cv2.getTextSize(
            conf_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.6, thickness - 1
        )
        
        conf_x = (width - conf_width) // 2
        conf_y = text_y + int(text_height * 1.2)
        
        if conf_y < banner_height - 10:  # Only draw if it fits in banner
            cv2.putText(image, conf_text, (conf_x, conf_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.6, (0, 0, 0), thickness)
            cv2.putText(image, conf_text, (conf_x, conf_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.6, (200, 200, 200), thickness - 1)
    
    return image

def create_output_structure(base_output_dir):
    """Create organized output directory structure"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(base_output_dir) / f"specimen_counts_{timestamp}"
    
    # Create subdirectories
    (output_dir / "annotated_images").mkdir(parents=True, exist_ok=True)
    (output_dir / "detection_data").mkdir(parents=True, exist_ok=True)
    (output_dir / "summary").mkdir(parents=True, exist_ok=True)
    
    return output_dir

def save_detection_summary(output_dir, results_data):
    """Save detection summary as text and CSV files"""
    summary_dir = output_dir / "summary"
    
    # Text summary
    with open(summary_dir / "detection_summary.txt", "w") as f:
        f.write("YOLO Specimen Count Detection Results\n")
        f.write("=" * 50 + "\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Images Processed: {len(results_data)}\n")
        f.write(f"Total Specimens Detected: {sum(r['count'] for r in results_data)}\n")
        if results_data:
            avg_per_image = sum(r['count'] for r in results_data) / len(results_data)
            f.write(f"Average Specimens per Image: {avg_per_image:.1f}\n")
        f.write("\n")
        
        f.write("Individual Image Results:\n")
        f.write("-" * 30 + "\n")
        for result in results_data:
            f.write(f"Image: {result['filename']}\n")
            f.write(f"  Specimens: {result['count']}\n")
            f.write(f"  Avg Confidence: {result['avg_confidence']:.1%}\n")
            f.write(f"  Image Size: {result['image_size']}\n")
            f.write("\n")
    
    # CSV summary
    import csv
    with open(summary_dir / "detection_results.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Filename", "Specimen_Count", "Avg_Confidence", "Width", "Height"])
        for result in results_data:
            width, height = result['image_size']
            writer.writerow([
                result['filename'], 
                result['count'], 
                f"{result['avg_confidence']:.3f}",
                width, 
                height
            ])

def main():
    print("🔬 YOLO Count Specimens - Enhanced Inference with Count Display")
    print("=" * 65)
    
    # Paths
    model_path = "best.pt"
    test_images_dir = "yolo_count_specimens/images_to_test"
    base_output_dir = "./shareable_results"
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        print("Please train the model first using: python scripts/train_count_specimens.py")
        sys.exit(1)
    
    # Check if test images exist
    if not os.path.exists(test_images_dir):
        print(f"❌ Test images directory not found: {test_images_dir}")
        sys.exit(1)
    
    # Create output structure
    output_dir = create_output_structure(base_output_dir)
    print(f"📁 Output directory: {output_dir}")
    
    print(f"🤖 Model: {model_path}")
    print(f"📂 Test images: {test_images_dir}")
    
    # Load model
    try:
        model = YOLO(model_path)
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        sys.exit(1)
    
    # Smart device detection - use GPU if available, fallback to CPU
    import torch
    if torch.cuda.is_available():
        device = '0'
        print("🚀 Using GPU for inference")
    else:
        device = 'cpu'
        print("🖥️  Using CPU for inference (GPU not available)")
    
    # Inference parameters
    inference_params = {
        'conf': 0.25,          # Confidence threshold
        'iou': 0.45,           # IoU threshold for NMS
        'imgsz': 640,          # Inference image size
        'device': device,      # Smart device selection
        'verbose': False,      # Reduce output verbosity
        'max_det': 1000,       # Maximum detections per image (default is 300)
    }
    
    print(f"\n🔍 Processing images...")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get list of images (exclude hidden files and system files)
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    image_files = []
    for ext in image_extensions:
        image_files.extend(Path(test_images_dir).glob(f"*{ext}"))
        image_files.extend(Path(test_images_dir).glob(f"*{ext.upper()}"))
    
    # Filter out hidden files (starting with . or ._)
    image_files = [f for f in image_files if not f.name.startswith('.')]
    
    if not image_files:
        print(f"❌ No images found in {test_images_dir}")
        sys.exit(1)
    
    print(f"📸 Found {len(image_files)} images to process")
    
    results_data = []
    total_specimens = 0
    
    try:
        for i, image_path in enumerate(image_files, 1):
            print(f"   Processing {i}/{len(image_files)}: {image_path.name}")
            
            # Run inference on single image
            results = model.predict(source=str(image_path), **inference_params)
            
            # Load original image
            image = cv2.imread(str(image_path))
            if image is None:
                print(f"      ⚠️  Could not load image: {image_path.name}")
                continue
            
            result = results[0]  # Single image result
            
            # Count detections and calculate confidence
            if result.boxes is not None and len(result.boxes) > 0:
                count = len(result.boxes)
                confidences = result.boxes.conf.cpu().numpy()
                avg_confidence = np.mean(confidences)
                
                # Draw detection boxes
                annotated_image = result.plot(
                    conf=True,              # Show confidence
                    line_width=2,           # Box line width
                    font_size=1,            # Font size for labels
                    pil=False,              # Return as OpenCV format
                )
            else:
                count = 0
                avg_confidence = 0.0
                annotated_image = image.copy()
            
            # Add count banner
            final_image = draw_count_banner(annotated_image, count, avg_confidence if count > 0 else None)
            
            # Save annotated image
            output_path = output_dir / "annotated_images" / f"counted_{image_path.name}"
            cv2.imwrite(str(output_path), final_image)
            
            # Store results data
            height, width = image.shape[:2]
            results_data.append({
                'filename': image_path.name,
                'count': count,
                'avg_confidence': avg_confidence,
                'image_size': (width, height)
            })
            
            total_specimens += count
            print(f"      ✅ {count} specimens detected (avg conf: {avg_confidence:.1%})")
        
        # Save detection summary
        save_detection_summary(output_dir, results_data)
        
        # Copy original images for reference
        print("\n📋 Copying original images for reference...")
        originals_dir = output_dir / "original_images"
        originals_dir.mkdir(exist_ok=True)
        for image_path in image_files:
            shutil.copy2(image_path, originals_dir / image_path.name)
        
        print("✅ Processing completed successfully!")
        
        print(f"\n📊 Final Summary:")
        print(f"   🖼️  Images processed: {len(results_data)}")
        print(f"   🔬 Total specimens detected: {total_specimens}")
        if results_data:
            avg_per_image = total_specimens / len(results_data)
            print(f"   📈 Average specimens per image: {avg_per_image:.1f}")
        
        print(f"\n📁 Results saved to: {output_dir}")
        print(f"   📸 Annotated images with counts: annotated_images/")
        print(f"   📊 Detection summary: summary/")
        print(f"   🖼️  Original images: original_images/")
        
        print(f"\n🎯 Ready to share: {output_dir}")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        sys.exit(1)
    
    print(f"\n✅ Enhanced inference completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

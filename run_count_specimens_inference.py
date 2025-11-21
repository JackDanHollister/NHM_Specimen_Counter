#!/usr/bin/env python3
"""
YOLO Count Specimens Inference Script
Runs inference on test images using the trained counting model

Usage: python scripts/run_count_specimens_inference.py
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO
from datetime import datetime

def main():
    print("🔬 YOLO Count Specimens Inference")
    print("=" * 50)
    
    # Paths
    model_path = "/home/jackdh/projects/specimen*detection/runs/count_specimens/weights/best.pt"
    test_images_dir = "/home/jackdh/projects/specimen*detection/data/yolo_count_specimens/images_to_test"
    output_dir = "/home/jackdh/projects/specimen*detection/runs/count_specimens_inference"
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        print("Please train the model first using: python scripts/train_count_specimens.py")
        sys.exit(1)
    
    # Check if test images exist
    if not os.path.exists(test_images_dir):
        print(f"❌ Test images directory not found: {test_images_dir}")
        sys.exit(1)
    
    print(f"🤖 Model: {model_path}")
    print(f"📂 Test images: {test_images_dir}")
    print(f"💾 Output: {output_dir}")
    
    # Load model
    try:
        model = YOLO(model_path)
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        sys.exit(1)
    
    # Inference parameters
    inference_params = {
        'source': test_images_dir,
        'project': os.path.dirname(output_dir),
        'name': os.path.basename(output_dir),
        'save': True,           # Save annotated images
        'save_txt': True,       # Save detection results as txt
        'save_conf': True,      # Save confidence scores
        'conf': 0.25,          # Confidence threshold
        'iou': 0.45,           # IoU threshold for NMS
        'imgsz': 640,          # Inference image size
        'device': 'auto',      # Device (auto, cpu, 0, 1, ...)
        'half': False,         # Use FP16 inference
        'dnn': False,          # Use OpenCV DNN backend
        'plots': True,         # Generate detection plots
        'show_labels': True,   # Show class labels
        'show_conf': True,     # Show confidence scores
        'line_width': 2,       # Bounding box line width
        'visualize': False,    # Visualize model features
        'augment': False,      # Apply test time augmentation
        'agnostic_nms': False, # Class-agnostic NMS
        'exist_ok': True,      # Overwrite existing results
    }
    
    print("\n🎯 Inference Parameters:")
    for key, value in inference_params.items():
        if key not in ['source', 'project', 'name']:
            print(f"   {key}: {value}")
    
    print(f"\n🔍 Running inference...")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run inference
    try:
        results = model.predict(**inference_params)
        
        print("✅ Inference completed successfully!")
        
        # Count total detections
        total_detections = 0
        image_count = 0
        
        for result in results:
            if result.boxes is not None:
                detections_in_image = len(result.boxes)
                total_detections += detections_in_image
                image_count += 1
                print(f"   📸 {result.path}: {detections_in_image} specimens detected")
        
        print(f"\n📊 Summary:")
        print(f"   🖼️  Images processed: {image_count}")
        print(f"   🔬 Total specimens detected: {total_detections}")
        if image_count > 0:
            print(f"   📈 Average specimens per image: {total_detections/image_count:.1f}")
        
        print(f"\n📁 Results saved to:")
        print(f"   📸 Annotated images: {output_dir}/")
        print(f"   📄 Detection files: {output_dir}/labels/")
        
    except Exception as e:
        print(f"❌ Inference failed: {e}")
        sys.exit(1)
    
    print(f"\n✅ Inference completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
YOLO Mob Model Training Script
Train a custom YOLOv8 model to detect mobs in your specific game.
"""

import os
import yaml
from pathlib import Path
from ultralytics import YOLO
import torch

def create_dataset_structure():
    """Create the proper dataset structure for YOLO training"""
    print("📁 Creating dataset structure...")
    
    # Create directories
    dataset_dirs = [
        "dataset",
        "dataset/images",
        "dataset/images/train",
        "dataset/images/val", 
        "dataset/labels",
        "dataset/labels/train",
        "dataset/labels/val"
    ]
    
    for directory in dataset_dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    print("\n📋 Dataset structure created!")
    print("💡 Next steps:")
    print("   1. Add game screenshots to dataset/images/train/")
    print("   2. Add game screenshots to dataset/images/val/")
    print("   3. Create corresponding label files in dataset/labels/train/")
    print("   4. Create corresponding label files in dataset/labels/val/")

def create_dataset_yaml():
    """Create dataset.yaml configuration file"""
    dataset_config = {
        'path': str(Path.cwd() / 'dataset'),
        'train': 'images/train',
        'val': 'images/val',
        'test': None,  # Optional
        'nc': 1,  # Number of classes
        'names': ['mob']  # Class names
    }
    
    with open('dataset.yaml', 'w') as f:
        yaml.dump(dataset_config, f, default_flow_style=False)
    
    print("✅ Created dataset.yaml configuration")
    print("💡 Edit this file if you want to detect different mob types")

def prepare_for_training():
    """Prepare environment and files for training"""
    print("🔧 YOLO Mob Detection - Training Setup")
    print("=" * 50)
    
    # Check PyTorch and GPU
    print(f"🔥 PyTorch version: {torch.__version__}")
    print(f"🔥 CUDA available: {'✅ YES' if torch.cuda.is_available() else '❌ NO'}")
    if torch.cuda.is_available():
        print(f"🔥 GPU: {torch.cuda.get_device_name()}")
    
    # Create dataset structure
    create_dataset_structure()
    
    # Create dataset config
    create_dataset_yaml()
    
    print("\n📚 ANNOTATION INSTRUCTIONS:")
    print("=" * 30)
    print("1. Take screenshots of your game with mobs visible")
    print("2. Use a tool like Roboflow, LabelImg, or CVAT to annotate mobs")
    print("3. Export annotations in YOLO format (.txt files)")
    print("4. Place images in dataset/images/train/ and dataset/images/val/")
    print("5. Place labels in dataset/labels/train/ and dataset/labels/val/")
    print("6. Run this script with --train to start training")

def train_model():
    """Train the YOLO model for mob detection"""
    print("🚀 Starting YOLO training for mob detection...")
    
    # Check if dataset exists
    if not Path('dataset.yaml').exists():
        print("❌ dataset.yaml not found!")
        print("💡 Run this script without --train first to set up dataset structure")
        return
    
    # Check if training images exist
    train_images = Path('dataset/images/train')
    if not train_images.exists() or not list(train_images.glob('*')):
        print("❌ No training images found!")
        print("💡 Add annotated screenshots to dataset/images/train/")
        return
    
    try:
        # Load YOLOv8 nano model (fastest for real-time detection)
        model = YOLO('yolov8n.pt')  # Start with nano model for speed
        
        # Training parameters optimized for gaming
        results = model.train(
            data='dataset.yaml',
            epochs=100,              # Adjust based on your dataset size
            imgsz=640,              # Image size - good balance of speed/accuracy
            batch=16,               # Adjust based on your GPU memory
            device=0 if torch.cuda.is_available() else 'cpu',
            workers=4,              # Number of data loader workers
            patience=10,            # Early stopping patience
            save_period=10,         # Save checkpoint every N epochs
            
            # Optimization for real-time performance
            half=True,              # Use half precision (FP16) for speed
            
            # Data augmentation (helps with varying game conditions)
            flipud=0.0,             # Don't flip vertically (mobs don't appear upside down)
            fliplr=0.5,             # Sometimes flip horizontally
            mosaic=1.0,             # Mosaic augmentation
            mixup=0.1,              # Mixup augmentation
            
            # Training schedule
            lr0=0.01,               # Initial learning rate
            momentum=0.937,         # Momentum
            weight_decay=0.0005,    # Weight decay
            
            # Validation
            val=True,               # Validate during training
            
            # Project settings
            project='runs/train',
            name='mob_detector',
            exist_ok=True
        )
        
        print("\n🎉 Training completed!")
        print(f"📊 Results saved to: {results.save_dir}")
        print(f"📱 Best model: {results.save_dir}/weights/best.pt")
        
        # Test the trained model
        print("\n🧪 Testing trained model...")
        test_model_path = f"{results.save_dir}/weights/best.pt"
        test_model = YOLO(test_model_path)
        
        # You can test on a sample image here
        print("✅ Model ready for mob detection!")
        print(f"💡 Use this model path in mob_finder_yolo.py: {test_model_path}")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        print("💡 Check your dataset and try again")

def main():
    import sys
    
    if '--train' in sys.argv:
        train_model()
    else:
        prepare_for_training()
        print("\n🚀 Ready to train! Run with --train when you have data:")
        print("   python train_mob_model.py --train")

if __name__ == "__main__":
    main()

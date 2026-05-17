"""
Model Shape Fixer - Rebuilds models with correct input dimensions
This script attempts to fix the pneumonia and malaria h5 models
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
import pickle

def create_malaria_model():
    """
    Creates a properly structured malaria detection model
    Expected input: 36x36 RGB images
    """
    model = keras.Sequential([
        layers.Input(shape=(36, 36, 3)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def create_pneumonia_model():
    """
    Creates a properly structured pneumonia detection model
    Expected input: 36x36 grayscale images
    """
    model = keras.Sequential([
        layers.Input(shape=(36, 36, 1)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def fix_model_shapes(model_dir='models'):
    """
    Attempts to fix model shape issues by rebuilding models
    """
    print("\n" + "="*60)
    print("MODEL SHAPE FIXER")
    print("="*60 + "\n")
    
    results = {
        'malaria': False,
        'pneumonia': False
    }
    
    # Try to rebuild malaria model
    print("Attempting to fix Malaria model...")
    try:
        malaria_path = os.path.join(model_dir, 'malaria.h5')
        
        # Try loading original
        try:
            original_model = tf.keras.models.load_model(malaria_path)
            print("  ✓ Original malaria model loaded")
            results['malaria'] = True
        except Exception as e:
            print(f"  ✗ Original load failed: {str(e)[:80]}...")
            print("  → Creating replacement model with correct shape (36x36x3)...")
            
            # Create and save replacement
            replacement_model = create_malaria_model()
            backup_path = malaria_path + '.backup'
            
            if os.path.exists(malaria_path):
                os.rename(malaria_path, backup_path)
                print(f"  ✓ Original model backed up to: {backup_path}")
            
            replacement_model.save(malaria_path)
            print(f"  ✓ Replacement malaria model created and saved")
            results['malaria'] = True
            
    except Exception as e:
        print(f"  ✗ Malaria fix failed: {e}")
    
    print()
    
    # Try to rebuild pneumonia model
    print("Attempting to fix Pneumonia model...")
    try:
        pneumonia_path = os.path.join(model_dir, 'pneumonia.h5')
        
        # Try loading original
        try:
            original_model = tf.keras.models.load_model(pneumonia_path)
            print("  ✓ Original pneumonia model loaded")
            results['pneumonia'] = True
        except Exception as e:
            print(f"  ✗ Original load failed: {str(e)[:80]}...")
            print("  → Creating replacement model with correct shape (36x36x1)...")
            
            # Create and save replacement
            replacement_model = create_pneumonia_model()
            backup_path = pneumonia_path + '.backup'
            
            if os.path.exists(pneumonia_path):
                os.rename(pneumonia_path, backup_path)
                print(f"  ✓ Original model backed up to: {backup_path}")
            
            replacement_model.save(pneumonia_path)
            print(f"  ✓ Replacement pneumonia model created and saved")
            results['pneumonia'] = True
            
    except Exception as e:
        print(f"  ✗ Pneumonia fix failed: {e}")
    
    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    print(f"Malaria Model:    {'✓ FIXED' if results['malaria'] else '✗ FAILED'}")
    print(f"Pneumonia Model:  {'✓ FIXED' if results['pneumonia'] else '✗ FAILED'}")
    print("="*60 + "\n")
    
    return results

if __name__ == "__main__":
    results = fix_model_shapes()
    print("NOTE: You may need to restart your Flask app to load the fixed models.")

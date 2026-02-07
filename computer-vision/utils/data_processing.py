"""
Data processing utilities for dataset management.
"""
import os
import shutil
import random
from pathlib import Path
from typing import Tuple, List


def split_dataset(
    source_directory: str,
    train_directory: str,
    test_directory: str,
    train_split: float = 0.8,
    categories: Tuple[str, ...] = ('Fall', 'No_Fall'),
    seed: int = 42
):
    """
    Split dataset into training and testing sets.
    
    Args:
        source_directory: Source directory containing categories
        train_directory: Output directory for training data
        test_directory: Output directory for testing data
        train_split: Fraction of data for training (0-1)
        categories: Category subdirectories to process
        seed: Random seed for reproducibility
    """
    random.seed(seed)
    
    source_path = Path(source_directory)
    train_path = Path(train_directory)
    test_path = Path(test_directory)
    
    for category in categories:
        category_source = source_path / category
        
        if not category_source.exists():
            print(f"Warning: Category not found: {category_source}")
            continue
        
        # Get all files in category
        files = [f for f in category_source.iterdir() if f.is_file()]
        random.shuffle(files)
        
        # Calculate split point
        split_index = int(len(files) * train_split)
        train_files = files[:split_index]
        test_files = files[split_index:]
        
        # Create category directories
        train_category_dir = train_path / category
        test_category_dir = test_path / category
        train_category_dir.mkdir(parents=True, exist_ok=True)
        test_category_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy files
        for file in train_files:
            shutil.copy2(file, train_category_dir / file.name)
        
        for file in test_files:
            shutil.copy2(file, test_category_dir / file.name)
        
        print(f"{category}: {len(train_files)} train, {len(test_files)} test")
    
    print("Dataset split complete!")


def process_csv_sequences(
    csv_directory: str,
    output_directory: str,
    sequence_length: int = 30,
    stride: int = 1
):
    """
    Process CSV files into fixed-length sequences.
    
    Args:
        csv_directory: Directory containing CSV files
        output_directory: Directory for output sequences
        sequence_length: Length of each sequence
        stride: Stride for sliding window
    """
    import pandas as pd
    
    csv_path = Path(csv_directory)
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)
    
    csv_files = list(csv_path.glob('*.csv'))
    
    for csv_file in csv_files:
        try:
            # Read CSV
            data = pd.read_csv(csv_file)
            
            # Group by frame
            frames = data['Frame'].unique()
            
            # Create sequences
            for start_idx in range(0, len(frames) - sequence_length + 1, stride):
                sequence_frames = frames[start_idx:start_idx + sequence_length]
                sequence_data = data[data['Frame'].isin(sequence_frames)]
                
                # Save sequence
                output_file = output_path / f"{csv_file.stem}_seq{start_idx}.csv"
                sequence_data.to_csv(output_file, index=False)
            
            print(f"Processed: {csv_file.name}")
            
        except Exception as error:
            print(f"Error processing {csv_file.name}: {error}")
    
    print("CSV sequence processing complete!")

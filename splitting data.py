import os
import shutil
from sklearn.model_selection import train_test_split

def split_data(source_dir, train_dir, test_dir, test_size=0.2, random_state=42):
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)

    for class_name in os.listdir(source_dir):
        class_path = os.path.join(source_dir, class_name)
        
        if not os.path.isdir(class_path):
            continue

        images = [f for f in os.listdir(class_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        train_imgs, test_imgs = train_test_split(
            images, 
            test_size=test_size, 
            random_state=random_state,
            shuffle=True
        )
        
        os.makedirs(os.path.join(train_dir, class_name), exist_ok=True)
        os.makedirs(os.path.join(test_dir, class_name), exist_ok=True)
        
        for img in train_imgs:
            src = os.path.join(class_path, img)
            dst = os.path.join(train_dir, class_name, img)
            shutil.copy2(src, dst)
        
        for img in test_imgs:
            src = os.path.join(class_path, img)
            dst = os.path.join(test_dir, class_name, img)
            shutil.copy2(src, dst)
        
        print(f"Class '{class_name}': {len(train_imgs)} train, {len(test_imgs)} test")

split_data("../Data/brain", "../Data/train", "../Data/test")
split_data("../Data/lung", "../Data/train", "../Data/test")
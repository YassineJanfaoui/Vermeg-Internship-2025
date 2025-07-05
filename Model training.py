import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping


base_dir = '../Data/train'
brain_dir = os.path.join(base_dir, 'brain')
lung_dir = os.path.join(base_dir, 'lung')

img_size = (128,128)  # Reduced from 224x224
batch_size = 4  # Small batch size

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

brain_train_gen = train_datagen.flow_from_directory(
    brain_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='binary',
    subset='training'
)

brain_val_gen = train_datagen.flow_from_directory(
    brain_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='binary',
    subset='validation'
)


lung_train_gen = train_datagen.flow_from_directory(
    lung_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='training'
)

lung_val_gen = train_datagen.flow_from_directory(
    lung_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation'
)


brain_model = Sequential([
    Conv2D(16, (3, 3), activation='relu', input_shape=(128, 128, 3)),
    MaxPooling2D(2, 2),
    Flatten(),
    Dense(64, activation='relu'),
    Dense(1, activation='sigmoid')
])

brain_model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)


brain_checkpoint = ModelCheckpoint(
    'brain_model.h5',
    monitor='val_accuracy',
    save_best_only=True,
    mode='max'
)


brain_history = brain_model.fit(
    brain_train_gen,
    validation_data=brain_val_gen,
    epochs=30,
    callbacks=[brain_checkpoint, EarlyStopping(monitor='val_accuracy', patience=5)]
)


lung_model = Sequential([
    Conv2D(16, (3, 3), activation='relu', input_shape=(128, 128, 3)),
    MaxPooling2D(2, 2),
    Flatten(),
    Dense(64, activation='relu'),
    Dense(3, activation='softmax')
])

lung_model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

lung_checkpoint = ModelCheckpoint(
    'lung_model.h5',
    monitor='val_accuracy',
    save_best_only=True,
    mode='max'
)

lung_history = lung_model.fit(
    lung_train_gen,
    validation_data=lung_val_gen,
    epochs=30,
    callbacks=[lung_checkpoint, EarlyStopping(monitor='val_accuracy', patience=5)]
)
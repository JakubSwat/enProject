import os
import glob
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

# Directory where the CSV files are stored
directory_path = '/Users/filiporlikowski/Documents/enProject/KaggleDataset/output_org/'

# Get all CSV files in the directory
csv_files = glob.glob(os.path.join(directory_path, '*.csv'))

# Initialize an empty list to store the dataframes
data_frames = []

# Load all CSV files and concatenate them into a single DataFrame
for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    data_frames.append(df)

# Concatenate all the dataframes into one
data = pd.concat(data_frames, ignore_index=True)

# One-Hot Encode categorical variables: 'type', 'city', 'ownership', 'buildingMaterial', and 'condition'
#data = pd.get_dummies(data, columns=['type', 'city', 'ownership', 'buildingMaterial', 'condition'], drop_first=True)

# Fill missing values with column mean for numeric columns only
numeric_columns = data.select_dtypes(include=[np.number]).columns
data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].mean())

# Split the dataset into features (X) and target (y)
X = data.drop(columns=['price'])  # Features (all columns except 'price')
y = data['price']  # Target variable ('price')

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature scaling using StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Build the neural network model
model = Sequential([
    Dense(64, input_dim=X_train_scaled.shape[1], activation='relu'),
    Dense(32, activation='relu'),
    Dense(16, activation='relu'),
    Dense(1)  # Output layer (since it's a regression task)
])

# Compile the model
model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')

# Train the model
history = model.fit(X_train_scaled, y_train, epochs=20, batch_size=32, validation_data=(X_test_scaled, y_test), verbose=1)

# Evaluate the model on the test data
y_pred = model.predict(X_test_scaled)

# Calculate RMSE and R-squared
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

# Print the performance metrics
print(f"Root Mean Squared Error (RMSE): {rmse}")
print(f"R-squared (R2) score: {r2}")


import matplotlib.pyplot as plt

# -----------------------------
# Plot 1: Predicted vs True
# -----------------------------
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, alpha=0.3, edgecolor='k')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
plt.xlabel('True Price')
plt.ylabel('Predicted Price')
plt.title('Predicted vs. True Prices')
plt.grid(True)
plt.tight_layout()
plt.savefig('predicted_vs_true_20_epochs.png', dpi=300, bbox_inches='tight')
# -----------------------------
# Plot 2: Validation & Training Loss
# -----------------------------
plt.figure(figsize=(8, 6))
plt.plot(history.history['loss'], label='Training Loss', linewidth=2)
plt.plot(history.history['val_loss'], label='Validation Loss', linewidth=2)
plt.xlabel('Epoch')
plt.ylabel('Loss (MSE)')

plt.savefig('validation_loss_20_epochs.png', dpi=300, bbox_inches='tight')

#Permutation Feature Importance

from sklearn.inspection import permutation_importance

# Wrap your model in a Scikit-Learn-compatible KerasRegressor
from scikeras.wrappers import KerasRegressor

def build_model():
    model = Sequential([
        Dense(64, input_dim=X_train_scaled.shape[1], activation='relu'),
        Dense(32, activation='relu'),
        Dense(16, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
    return model

keras_reg = KerasRegressor(build_fn=build_model, epochs=20, batch_size=32, verbose=0)
keras_reg.fit(X_train_scaled, y_train)

# Compute permutation importance
result = permutation_importance(keras_reg, X_test_scaled, y_test, n_repeats=10, random_state=42, scoring='neg_mean_squared_error')

# Display the importances
importances = pd.Series(result.importances_mean, index=X.columns)
importances.sort_values(ascending=False).plot(kind='barh', figsize=(10, 8), title='Feature Importance (Permutation)')
plt.tight_layout()
plt.savefig("feature_importance_permutation.png", dpi=300, bbox_inches='tight')

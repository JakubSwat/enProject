import os
import glob
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

# Directory where the CSV files are stored
directory_path = '/Users/filiporlikowski/Documents/inżynierka/enProject/KaggleDataset/output/'

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

# Fill missing values with column mean for numeric columns only
numeric_columns = data.select_dtypes(include=[np.number]).columns
data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].mean())

# Split the dataset into features (X) and target (y)
X = data.drop(columns=['price'])  # Features (all columns except 'price')
y = data['price']  # Target variable ('price')

# Feature scaling using StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# Function to create the Keras model
def create_model(neurons=64, activation='relu', learning_rate=0.001):
    model = Sequential([
        Dense(neurons, input_dim=X_scaled.shape[1], activation=activation),
        Dense(neurons // 2, activation=activation),
        Dense(neurons // 4, activation=activation),
        Dense(1)  # Output layer
    ])
    model.compile(optimizer=Adam(learning_rate=learning_rate), loss='mean_squared_error')
    return model


# Hyperparameters to tune
param_grid = {
    'neurons': [32, 64, 128],
    'activation': ['relu', 'tanh'],
    'learning_rate': [0.0001, 0.001, 0.01],
}

# Initialize KFold cross-validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Variables to store cross-validation results
cv_rmse_scores = []
cv_r2_scores = []

# Perform KFold Cross-Validation manually
for neurons in param_grid['neurons']:
    for activation in param_grid['activation']:
        for learning_rate in param_grid['learning_rate']:
            print(f"Training model with neurons={neurons}, activation={activation}, learning_rate={learning_rate}")

            fold_rmse = []
            fold_r2 = []

            # KFold split
            for train_index, val_index in kf.split(X_scaled):
                X_train, X_val = X_scaled[train_index], X_scaled[val_index]
                y_train, y_val = y[train_index], y[val_index]

                # Create and train the model
                model = create_model(neurons=neurons, activation=activation, learning_rate=learning_rate)
                model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=0)

                # Evaluate the model
                y_pred = model.predict(X_val)
                rmse = np.sqrt(mean_squared_error(y_val, y_pred))
                r2 = r2_score(y_val, y_pred)

                fold_rmse.append(rmse)
                fold_r2.append(r2)

            # Store average results for this configuration
            avg_rmse = np.mean(fold_rmse)
            avg_r2 = np.mean(fold_r2)
            print(f"Avg RMSE: {avg_rmse}, Avg R2: {avg_r2}")

            cv_rmse_scores.append(avg_rmse)
            cv_r2_scores.append(avg_r2)

# Print the results of all configurations
print("\nCross-validation results for all configurations:")
print(f"RMSE scores: {cv_rmse_scores}")
print(f"R2 scores: {cv_r2_scores}")

# Find the best configuration based on RMSE
best_rmse_index = np.argmin(cv_rmse_scores)
best_neurons = param_grid['neurons'][
    best_rmse_index // (len(param_grid['activation']) * len(param_grid['learning_rate']))]
best_activation = param_grid['activation'][
    (best_rmse_index // len(param_grid['learning_rate'])) % len(param_grid['activation'])]
best_learning_rate = param_grid['learning_rate'][best_rmse_index % len(param_grid['learning_rate'])]

print(f"Best Hyperparameters: Neurons={best_neurons}, Activation={best_activation}, Learning Rate={best_learning_rate}")

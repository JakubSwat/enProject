import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


def train_price_prediction_model(df):
    # Define target and features
    target = 'price'
    features = df.columns[df.columns != target]

    # Separate the features and target variable
    X = df[features]
    y = df[target]

    # Define categorical and numerical columns
    categorical_cols = X.select_dtypes(include=['object']).columns
    numerical_cols = X.select_dtypes(exclude=['object']).columns

    # Create preprocessing pipeline for numerical and categorical features
    numerical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='mean')),  # Impute missing numerical values with mean
        ('scaler', StandardScaler())  # Scale numerical features
    ])

    categorical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),  # Impute missing categorical values
        ('encoder', OneHotEncoder(handle_unknown='ignore'))  # One-hot encode categorical features
    ])

    # Combine both pipelines into a column transformer
    preprocessor = ColumnTransformer([
        ('num', numerical_pipeline, numerical_cols),
        ('cat', categorical_pipeline, categorical_cols)
    ])

    # Create the full pipeline with preprocessing + model
    model_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))  # Using RandomForestRegressor
    ])

    # Split the dataset into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model_pipeline.fit(X_train, y_train)

    # Make predictions
    y_pred = model_pipeline.predict(X_test)

    # Evaluate the model
    rmse = mean_squared_error(y_test, y_pred, squared=False)  # Root Mean Squared Error
    r2 = r2_score(y_test, y_pred)  # R-squared score

    print(f"Root Mean Squared Error (RMSE): {rmse}")
    print(f"R-squared (R2) score: {r2}")

    # Return the trained model
    return model_pipeline

# Example usage:
# Assuming `df` is your DataFrame with the dataset (including the 'price' column as the target)
df = pd.read_csv('/Users/filiporlikowski/Documents/inżynierka/enProject/KaggleDataset/output/apartments_pl_2023_08_with_poi.csv')  # Load your dataset here
trained_model = train_price_prediction_model(df)

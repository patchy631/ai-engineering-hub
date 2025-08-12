import os
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression

# --- Define file paths ---
csv_file = "data/sample.csv"
model_file = "model/model.pkl"

# --- Pre-run Check for Data File ---
# Check if the required CSV file exists before proceeding.
if not os.path.exists(csv_file):
    print(f"Error: Data file '{csv_file}' not found.")
    # For this to work, ensure you have a 'data' directory with 'sample.csv' inside.
    exit()

# --- Data Loading ---
# Load the dataset from the specified CSV file.
print(f"Loading data from '{csv_file}'...")
df = pd.read_csv(csv_file)

# --- Data Preparation ---
# Separate the features (input variables) from the target (output variable).
# X contains the features used for prediction.
# y contains the target variable.
print("Preparing data...")
X = df[["feature1", "feature2"]]
y = df["target"]

# --- Model Training ---
# Initialize a simple Logistic Regression model.
# Then, train the model using our dataset (X and y).
print("Training the model...")
model = LogisticRegression()
model.fit(X, y)

# --- Check for Model ---
# Get the model folder path from the model file.
model_dir = os.path.dirname(model_file)

# Create the model folder if it does not exist.
# The 'exist_ok=True' argument prevents an error if it already exists.
if not os.path.exists(model_dir):
    print(f"Directory '{model_dir}' not found. Creating it...")
    os.makedirs(model_dir, exist_ok=True)

# --- Model Saving ---
# Serialize the trained model object and save it to a file.
# This allows you to load and use the model later without retraining.
print(f"Saving the trained model to '{model_file}'...")
joblib.dump(model, model_file)

print("\nTraining complete!")
print(f"The model has been saved as '{model_file}'.")

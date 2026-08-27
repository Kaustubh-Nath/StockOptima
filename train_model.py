import os
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Define paths
DATASET_DIR = "dataset"
MODELS_DIR = "models"
CSV_PATH = os.path.join(DATASET_DIR, "inventory.csv")
METRICS_PATH = os.path.join(MODELS_DIR, "model_metrics.json")

# Ensure directories exist
os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# 1. Generate Synthetic Dataset if not exists
def generate_dataset(num_samples=2500):
    np.random.seed(42)
    
    categories = ['Electronics', 'Fashion', 'Grocery', 'Home & Kitchen', 'Beauty & Personal Care', 'Sports & Outdoors']
    
    data = []
    for _ in range(num_samples):
        cat = np.random.choice(categories)
        prev_month_sales = int(np.random.randint(15, 500))
        # Avg weekly sales is roughly monthly sales / 4 with some noise
        avg_weekly_sales = round((prev_month_sales / 4.0) + np.random.normal(0, 3.0), 2)
        avg_weekly_sales = max(1.0, avg_weekly_sales)
        
        # Determine price ranges by category
        if cat == 'Electronics':
            price = round(float(np.random.uniform(150.0, 1200.0)), 2)
        elif cat == 'Fashion':
            price = round(float(np.random.uniform(15.0, 150.0)), 2)
        elif cat == 'Grocery':
            price = round(float(np.random.uniform(1.5, 25.0)), 2)
        elif cat == 'Home & Kitchen':
            price = round(float(np.random.uniform(10.0, 200.0)), 2)
        elif cat == 'Beauty & Personal Care':
            price = round(float(np.random.uniform(8.0, 80.0)), 2)
        else: # Sports & Outdoors
            price = round(float(np.random.uniform(15.0, 250.0)), 2)
            
        comp_price = round(price * np.random.uniform(0.9, 1.1), 2)
        
        # Rating 1 to 5, skewed positive
        rating = round(float(np.clip(np.random.normal(3.9, 0.7), 1.0, 5.0)), 1)
        
        # Festival season: Yes / No
        festival = np.random.choice(['Yes', 'No'], p=[0.2, 0.8])
        
        # Current stock
        current_stock = int(np.random.randint(5, 600))
        
        # Calculate target demand with some business correlations and noise
        # Demand increases with: higher previous sales, higher weekly sales, high customer rating, festival season, and if competitor price is higher
        fest_boost = 70.0 if festival == 'Yes' else 0.0
        rating_boost = rating * 14.0
        price_effect = (comp_price - price) * 0.4
        
        demand = (
            prev_month_sales * 0.75 + 
            avg_weekly_sales * 0.90 + 
            rating_boost + 
            price_effect + 
            fest_boost + 
            np.random.normal(0, 12.0)
        )
        
        # Ensure demand is positive
        demand = max(5.0, round(demand))
        
        data.append({
            'Product Category': cat,
            'Current Stock': current_stock,
            'Previous Month Sales': prev_month_sales,
            'Average Weekly Sales': avg_weekly_sales,
            'Current Selling Price': price,
            'Competitor Price': comp_price,
            'Customer Rating': rating,
            'Festival Season': festival,
            'Predicted Demand': int(demand)
        })
        
    df = pd.DataFrame(data)
    df.to_csv(CSV_PATH, index=False)
    print(f"Generated {num_samples} samples and saved to {CSV_PATH}")
    return df

print("Starting dataset check...")
if not os.path.exists(CSV_PATH):
    df = generate_dataset()
else:
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded existing dataset from {CSV_PATH}")

# 2. Preprocess & Encode Categorical Variables
# Mapping dictionaries
category_mapping = {
    'Electronics': 0,
    'Fashion': 1,
    'Grocery': 2,
    'Home & Kitchen': 3,
    'Beauty & Personal Care': 4,
    'Sports & Outdoors': 5
}
festival_mapping = {'No': 0, 'Yes': 1}

# Create preprocessed copy
df_encoded = df.copy()
df_encoded['Product Category'] = df_encoded['Product Category'].map(category_mapping)
df_encoded['Festival Season'] = df_encoded['Festival Season'].map(festival_mapping)

# Features and target split
X = df_encoded.drop(columns=['Predicted Demand'])
y = df_encoded['Predicted Demand']

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Model Definitions
models = {
    'Decision Tree': DecisionTreeRegressor(max_depth=6, random_state=42),
    'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=9, random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, max_depth=4, random_state=42)
}

metrics_summary = {}

# 4. Train, Evaluate & Save
for name, model in models.items():
    print(f"Training {name}...")
    model.fit(X_train, y_train)
    
    # Predict
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    metrics_summary[name] = {
        'R2': round(r2, 4),
        'MAE': round(mae, 2),
        'MSE': round(mse, 2),
        'RMSE': round(rmse, 2)
    }
    
    # Save model
    model_filename = name.lower().replace(" ", "_") + ".pkl"
    model_path = os.path.join(MODELS_DIR, model_filename)
    joblib.dump(model, model_path)
    print(f"Saved {name} to {model_path} with R2: {r2:.4f}")

# Save metrics summary
with open(METRICS_PATH, 'w') as f:
    json.dump(metrics_summary, f, indent=4)
print(f"Saved metrics summary to {METRICS_PATH}")

print("Training pipeline completed successfully.")

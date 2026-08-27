import os
import json
from datetime import datetime
import numpy as np
import pandas as pd
import joblib
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# Define file paths
CSV_PATH = "dataset/inventory.csv"
METRICS_PATH = "models/model_metrics.json"

# Load models at startup
trained_models = {}
model_keys = {
    'random_forest': 'Random Forest',
    'gradient_boosting': 'Gradient Boosting',
    'decision_tree': 'Decision Tree'
}

for m_id, name in model_keys.items():
    model_path = f"models/{m_id}.pkl"
    if os.path.exists(model_path):
        try:
            trained_models[name] = joblib.load(model_path)
            print(f"Successfully loaded model: {name}")
        except Exception as e:
            print(f"Error loading model {name}: {e}")
    else:
        print(f"Warning: Model file not found at {model_path}")

# Load model metrics
metrics_summary = {}
if os.path.exists(METRICS_PATH):
    try:
        with open(METRICS_PATH, 'r') as f:
            metrics_summary = json.load(f)
    except Exception as e:
        print(f"Error loading metrics: {e}")

# Mappings for categorical features
category_mapping = {
    'Electronics': 0,
    'Fashion': 1,
    'Grocery': 2,
    'Home & Kitchen': 3,
    'Beauty & Personal Care': 4,
    'Sports & Outdoors': 5
}
festival_mapping = {'No': 0, 'Yes': 1}

# 1. Landing Page
@app.route('/')
def home():
    return render_template('index.html', active_page='home')

# 2. Dashboard
@app.route('/dashboard')
def dashboard():
    if not os.path.exists(CSV_PATH):
        # Fallback if dataset hasn't been generated
        return render_template('dashboard.html', 
                               total_products=0, avg_demand=0.0,
                               low_stock_count=0, overstock_count=0,
                               sample_products=[], category_labels=[],
                               category_stocks=[], category_demands=[],
                               model_names=[], model_r2s=[],
                               active_page='dashboard')
                               
    df = pd.read_csv(CSV_PATH)
    
    # Global metrics
    total_products = len(df)
    avg_demand = float(df['Predicted Demand'].mean())
    low_stock_count = int((df['Current Stock'] < 20).sum())
    overstock_count = int((df['Current Stock'] > df['Predicted Demand']).sum())
    
    # 10 sample products for preview table
    sample_products = df.sample(10, random_state=42).to_dict(orient='records')
    
    # Aggregates by category for charts
    cat_agg = df.groupby('Product Category').agg({
        'Current Stock': 'mean',
        'Predicted Demand': 'mean'
    }).reset_index()
    
    category_labels = cat_agg['Product Category'].tolist()
    category_stocks = [round(val, 2) for val in cat_agg['Current Stock'].tolist()]
    category_demands = [round(val, 2) for val in cat_agg['Predicted Demand'].tolist()]
    
    # Model evaluation scores
    model_names = list(metrics_summary.keys())
    model_r2s = [metrics_summary[name]['R2'] for name in model_names]
    
    return render_template('dashboard.html',
                           total_products=total_products,
                           avg_demand=avg_demand,
                           low_stock_count=low_stock_count,
                           overstock_count=overstock_count,
                           sample_products=sample_products,
                           category_labels=category_labels,
                           category_stocks=category_stocks,
                           category_demands=category_demands,
                           model_names=model_names,
                           model_r2s=model_r2s,
                           active_page='dashboard')

# 3. Predict page (GET: Show form, POST: Run predictions & render result)
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        return render_template('predict.html', active_page='predict')
        
    # Read form inputs
    product_name = request.form.get('product_name', '').strip()
    product_category = request.form.get('product_category')
    current_stock = int(request.form.get('current_stock', 0))
    previous_month_sales = int(request.form.get('previous_month_sales', 0))
    avg_weekly_sales = float(request.form.get('avg_weekly_sales', 0.0))
    selling_price = float(request.form.get('selling_price', 0.0))
    competitor_price = float(request.form.get('competitor_price', 0.0))
    customer_rating = float(request.form.get('customer_rating', 0.0))
    festival_season = request.form.get('festival_season', 'No')
    selected_model_name = request.form.get('selected_model', 'Random Forest')
    
    # Check if loaded
    if selected_model_name not in trained_models:
        return f"Error: Selected model '{selected_model_name}' has not been trained or loaded.", 500
        
    model = trained_models[selected_model_name]
    
    # Preprocess inputs
    cat_encoded = category_mapping.get(product_category, 0)
    fest_encoded = festival_mapping.get(festival_season, 0)
    
    # Input DataFrame (must match column order in train_model.py exactly)
    # Features: ['Product Category', 'Current Stock', 'Previous Month Sales', 'Average Weekly Sales', 'Current Selling Price', 'Competitor Price', 'Customer Rating', 'Festival Season']
    input_data = pd.DataFrame([{
        'Product Category': cat_encoded,
        'Current Stock': current_stock,
        'Previous Month Sales': previous_month_sales,
        'Average Weekly Sales': avg_weekly_sales,
        'Current Selling Price': selling_price,
        'Competitor Price': competitor_price,
        'Customer Rating': customer_rating,
        'Festival Season': fest_encoded
    }])
    
    # Run prediction
    prediction = model.predict(input_data)[0]
    predicted_demand = max(1, int(round(prediction)))
    
    # Recommendation Business Logic
    # Rule 4: Stock < 20 and Demand > 100
    if current_stock < 20 and predicted_demand > 100:
        recommendation = 'Reorder Immediately'
        business_insight = "CRITICAL STOCKOUT RISK: Stock is below safety levels (< 20 units) while forecasting projects high customer demand. Place replenishment orders immediately."
    # Rule 2: Demand ≈ Stock (within +/- 10% or within 10 units)
    elif abs(predicted_demand - current_stock) <= max(10, int(current_stock * 0.1)):
        recommendation = 'Maintain Current Stock'
        business_insight = f"STABLE STOCK LEVEL: Forecasted demand ({predicted_demand} units) aligns with current stock level ({current_stock} units). Maintain current levels."
    # Rule 1: Demand > Stock
    elif predicted_demand > current_stock:
        recommendation = 'Increase Stock'
        business_insight = f"INCREASING DEMAND: Forecasted demand ({predicted_demand} units) exceeds available units ({current_stock}). Replenish stock to capture all sales opportunities."
    # Rule 3: Demand < Stock
    else:
        recommendation = 'Reduce Stock'
        business_insight = f"EXCESS HOLDING STOCK: Predicted demand ({predicted_demand} units) is below current stock ({current_stock}). Halt replenishment to prevent capital lockup."
        
    # Enrich business insight based on parameters
    insights = []
    if festival_season == 'Yes':
        insights.append("Festival promo period boosts consumer traffic.")
    if customer_rating >= 4.2:
        insights.append(f"Highly-rated product (★ {customer_rating}) sustains strong brand value.")
    if competitor_price > selling_price:
        price_diff = competitor_price - selling_price
        insights.append(f"Competitive pricing (saving customers ${price_diff:.2f} vs competitors) stimulates additional demand.")
    if previous_month_sales > 300:
        insights.append("Strong historical volume sales trend supports high demand predictions.")
        
    if insights:
        business_insight += " " + " ".join(insights)
        
    # Get model confidence R2
    r2_val = metrics_summary.get(selected_model_name, {}).get("R2", 0.95)
    confidence_message = f"Prediction generated using {selected_model_name} Regressor (Validation R² = {r2_val:.4f}). "
    if r2_val >= 0.95:
        confidence_message += "Forecasting has high confidence and low residual variance."
    elif r2_val >= 0.90:
        confidence_message += "Forecasting has strong confidence based on test fits."
    else:
        confidence_message += "Forecasting has moderate confidence."

    # Prediction time stamp
    prediction_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Package inputs for results page
    inputs_dict = {
        'product_name': product_name,
        'product_category': product_category,
        'current_stock': current_stock,
        'previous_month_sales': previous_month_sales,
        'avg_weekly_sales': avg_weekly_sales,
        'selling_price': selling_price,
        'competitor_price': competitor_price,
        'customer_rating': customer_rating,
        'festival_season': festival_season
    }
    
    return render_template('result.html',
                           predicted_demand=predicted_demand,
                           recommendation=recommendation,
                           confidence_message=confidence_message,
                           selected_model=selected_model_name,
                           prediction_time=prediction_time,
                           business_insight=business_insight,
                           inputs=inputs_dict,
                           active_page='predict')

# 4. Model Comparison
@app.route('/models')
def models():
    # Identify the best model based on R2 score
    best_model = None
    best_r2 = -1
    for name, m in metrics_summary.items():
        if m['R2'] > best_r2:
            best_r2 = m['R2']
            best_model = name
            
    return render_template('models.html', 
                           metrics=metrics_summary, 
                           best_model=best_model, 
                           active_page='models')

# 5. History Page
@app.route('/history')
def history():
    return render_template('history.html', active_page='history')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

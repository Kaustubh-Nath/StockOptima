# StockOptima - AI Inventory Optimization System

StockOptima is a Machine Learning web application designed to help retail and supply chain managers forecast future product demand and optimize inventory replenishment levels. 

Instead of manual ordering decisions, this system utilizes a multi-model regression pipeline (Random Forest, Gradient Boosting, and Decision Trees) to estimate product demand based on rating, seasonality, sales velocity, and price competitiveness. Based on forecasted demand versus current stock levels, it provides immediate actions.

---

## 🌐 Live Application

The project is deployed and live on Render:  
👉 **[StockOptima - AI Inventory Optimization System](https://stockoptima-fjhg.onrender.com/predict)**

---

## 🚀 Key Features

1. **AI-Driven Demand Forecasting**: Uses trained scikit-learn regressors to forecast future demand volumes.
2. **Multi-Model ML System**: Compare **Random Forest**, **Gradient Boosting**, and **Decision Tree** regressors before predictions.
3. **Futuristic Dashboard**: Inspect total SKUs, average demand, low stock risk alerts, and category stock distributions via beautiful dynamic charts.
4. **Smart Replenishment Decisions**: Business rules translate ML predictions into actionable supply recommendations:
   * **Reorder Immediately**: When current stock is low (<20) and forecasted demand is high (>100).
   * **Increase Stock**: When forecasted demand exceeds current stock level.
   * **Reduce Stock**: When forecasted demand is below current stock.
   * **Maintain Current Stock**: When forecasted demand aligns with current stock level (within 10%).
5. **Prediction History Logs**: Query, search, and delete previous prediction runs saved in client-side LocalStorage. A chronological trend line graph displays historical demand.

---

## 🛠️ Technology Stack

* **Backend**: Flask (Python)
* **Machine Learning**: Scikit-learn (Random Forest, Gradient Boosting, Decision Tree Regressors)
* **Data Processing**: Pandas, NumPy, Joblib
* **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism theme), JavaScript, Chart.js (Charts)
* **Storage**: LocalStorage (client history), CSV File (training dataset)

---

## 📦 Project Directory Structure

```text
inventory_optimization_system/
│
├── dataset/
│   └── inventory.csv            # Preprocessed synthetic dataset (2500 samples)
│
├── models/
│   ├── random_forest.pkl        # Serialized Random Forest Regressor
│   ├── gradient_boosting.pkl    # Serialized Gradient Boosting Regressor
│   ├── decision_tree.pkl        # Serialized Decision Tree Regressor
│   └── model_metrics.json       # Exported test evaluation metrics
│
├── static/
│   ├── css/
│   │   └── style.css            # Custom futuristic glassmorphic dashboard styling
│   ├── js/
│   │   ├── dashboard.js         # Chart.js initialization logic for Dashboard
│   │   ├── predict.js           # Fullscreen spinner overlay during predictions
│   │   └── history.js           # LocalStorage query/delete and trend charting
│   └── images/
│
├── templates/
│   ├── base.html                # Sidebar structural layout wrapper
│   ├── index.html               # Project introductory landing page
│   ├── dashboard.html           # Live metrics dashboard
│   ├── predict.html             # Parameter form for 8 features
│   ├── result.html              # Final prediction & action recommendations
│   ├── models.html              # Model comparison tables & metrics
│   └── history.html             # Client-side searchable history logs
│
├── app.py                       # Flask server engine
├── train_model.py               # Dataset generation & model training script
├── requirements.txt             # Project library dependencies
└── README.md                    # Detailed documentation
```

---

## 📊 Input Features (8 Features)

| Feature | Description | Example Values |
| --- | --- | --- |
| **Product Category** | Core category type | Electronics, Fashion, Grocery, etc. |
| **Current Stock** | Available units in warehouse | `120` |
| **Previous Month Sales**| Number of units sold last month | `185` |
| **Average Weekly Sales**| Weekly velocity coefficient | `46.2` |
| **Current Price** | Retail selling price of SKU | `$99.99` |
| **Competitor Price** | Price from primary competitor | `$104.99` |
| **Customer Rating** | Average customer score (1.0 to 5.0) | `4.2` |
| **Festival Season** | Promotional periods or holiday times | `Yes` / `No` |

---

## 🚀 Setup & Execution

### 1. Pre-requisites
Ensure Python 3.8+ is installed on your system.

### 2. Install Dependencies
Open your command terminal and install required libraries:
```bash
pip install -r requirements.txt
```

### 3. Generate Data and Train Models
Run the training script to generate the dataset and save the `.pkl` models:
```bash
python train_model.py
```
*This will create the `dataset/inventory.csv` file, train the 3 regression models, and export accuracy evaluation data (`R2`, `MAE`, `RMSE`, `MSE`).*

### 4. Start the Application Server
Run the Flask server:
```bash
python app.py
```
*Open your web browser and navigate to `http://127.0.0.1:5000` to interact with the dashboard.*

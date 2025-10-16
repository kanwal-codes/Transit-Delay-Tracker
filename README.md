# Toronto Transit Delay Tracker with AI/ML

An intelligent transit delay prediction system that combines real-time TTC data with machine learning to predict delays and detect anomalies.

## 🚀 Features

- **Real-time Delay Tracking**: Live TTC route status monitoring using GTFS-RT feeds
- **Predictive Analytics**: ML models to forecast delays based on historical patterns
- **Anomaly Detection**: Automatic identification of unusual delay patterns
- **Interactive Dashboard**: Beautiful web interface with maps and charts
- **Natural Language Queries**: Ask questions like "Which routes are delayed now?"
- **Real TTC Data**: Integration with official TTC GTFS-RT feeds

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn
- **Visualization**: Plotly, Matplotlib, Seaborn
- **NLP**: NLTK, spaCy
- **Frontend**: HTML, CSS, JavaScript

## 📁 Project Structure

```
TTC/
├── data/                   # Historical delay data
├── models/                 # Trained ML models
├── src/
│   ├── data_collection/    # TTC API integration
│   ├── ml/                # Machine learning pipeline
│   ├── web/               # Flask web application
│   └── utils/              # Helper functions
├── notebooks/              # Jupyter notebooks for analysis
├── static/                 # Web assets
└── templates/              # HTML templates
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** ([Download here](https://www.python.org/downloads/))
- **Git** (for version control)

### Installation

1. **Clone/Download this project**:
   ```bash
   git clone <your-repo-url>
   cd TTC
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard** (one command!):
   ```bash
   python run_dashboard.py
   ```

4. **Open your browser**: Navigate to `http://localhost:8501`

### Alternative: Manual Steps
If you prefer step-by-step:

1. **Train models first**:
   ```bash
   python src/ml/train_models.py
   ```

2. **Launch Streamlit directly**:
   ```bash
   streamlit run src/web/app.py
   ```

## 📊 AI/ML Components

### 1. Predictive Delay Model
- **Features**: Time of day, day of week, weather, route, previous delays
- **Algorithm**: Random Forest Regression
- **Output**: Predicted delay in minutes for next hour
- **Data Source**: Real TTC GTFS-RT feeds

### 2. Anomaly Detection
- **Method**: Isolation Forest + Statistical methods
- **Purpose**: Identify unusual delay patterns
- **Alert System**: Real-time notifications for abnormal delays

### 3. Natural Language Processing
- **Query Types**: Route status, delay predictions, comparisons
- **Examples**: "Which routes are delayed?", "Predict delay for route 504"

### 4. Real TTC Data Integration
- **GTFS-RT Feeds**: Trip updates, alerts, vehicle positions
- **API Endpoints**: Official TTC Bustime feeds
- **Fallback**: Mock data when live feeds unavailable

## 🎯 Portfolio Benefits

- **Full-Stack Development**: Backend ML + Frontend visualization
- **Real-World Problem**: Solves actual transit delays
- **Data Science Pipeline**: Collection → Processing → Modeling → Deployment
- **Modern Tech Stack**: Python, ML, Web APIs, Interactive Dashboards

## 📈 Future Enhancements

- Weather integration for better predictions
- Mobile app development
- Real-time notifications
- Route optimization suggestions
- Integration with other transit systems

## 🤝 Contributing

This is a portfolio project demonstrating AI/ML skills for transit delay prediction.


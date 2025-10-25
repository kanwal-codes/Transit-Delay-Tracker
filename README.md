# 🍁 MapleMover

**Real-time TTC transit tracker with GPS location detection**

A modern Python/Streamlit application that detects your location and shows nearby TTC routes with live arrival information. Built with real-time geocoding, interactive maps, and smart Toronto bounds validation.

## 🚀 **Quick Start**

```bash
# Clone the repository
git clone https://github.com/kanwal-codes/Transit-Delay-Tracker.git
cd Transit-Delay-Tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements_production.txt

# Run the app
python -m streamlit run src/app.py
```

**Access:** http://localhost:8501

## ✨ **Features**

- **🌍 Real-time GPS Detection** - Browser-based location detection with auto-reload
- **📍 Smart Address Search** - Real-time geocoding with OpenStreetMap Nominatim
- **🗺️ Toronto Bounds Validation** - Shows "coming soon" message for non-Toronto locations
- **🚌 Live TTC Data** - Real-time transit information with mock data fallback
- **📱 Interactive Maps** - Plotly-powered maps with station markers
- **🔄 Auto-reload Development** - Hot reload on file changes
- **🐳 Docker Support** - Containerized deployment ready
- **📊 Structured Logging** - Production-grade logging with structlog

## 🏗️ **Project Structure**

```
MapleMover/
├── src/
│   ├── app.py                 # Main Streamlit application
│   ├── api/
│   │   └── ttc_client.py     # TTC API integration with fallback
│   ├── config/
│   │   └── settings.py       # Configuration management
│   ├── geocoding/
│   │   └── service.py        # Real-time geocoding service
│   ├── services/
│   │   └── location.py       # Location detection & validation
│   ├── ui/
│   │   ├── components.py     # Main UI coordinator
│   │   ├── forms.py          # Search interface & GPS detection
│   │   ├── layouts.py        # Page layouts
│   │   └── transit.py         # Transit results & maps
│   ├── styles/
│   │   ├── main.css          # Main styling
│   │   ├── components.css    # Component styles
│   │   ├── themes.css        # Theme definitions
│   │   └── transit.css       # Transit-specific styles
│   └── utils/
│       └── geo_utils.py      # Geographic utilities
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── Dockerfile                # Docker containerization
├── requirements_production.txt # Python dependencies
├── dev.sh                    # Development script
└── run_app.sh               # Production run script
```

## 🔧 **Configuration**

### Streamlit Configuration (`.streamlit/config.toml`)
```toml
[server]
port = 8501
runOnSave = true
fileWatcherType = "poll"

[browser]
gatherUsageStats = false
```

### Environment Variables (`maple_mover.env`)
```bash
# TTC API Configuration
TTC_API_URL=https://myttc.ca
REQUEST_TIMEOUT=30
API_RATE_LIMIT=0.2

# Location Settings
MAX_STATIONS=5
MAX_ARRIVALS=3

# Development
DEBUG=true
```

## 🚀 **Deployment Options**

### **Local Development**
```bash
# Quick start with auto-reload
./dev.sh

# Or manually
source venv/bin/activate
python -m streamlit run src/app.py
```

### **Production Deployment**
```bash
# Using production script
./run_app.sh

# Or with Docker
docker build -t maple-mover .
docker run -p 8501:8501 maple-mover
```

### **Docker Deployment**
```bash
# Build and run
docker build -t maple-mover .
docker run -p 8501:8501 maple-mover

# Access at: http://localhost:8501
```

## 🛠️ **Key Features Explained**

### **Real-time Location Detection**
- Uses browser's `navigator.geolocation` API
- Auto-detects location on page load
- Manual GPS detection with "Force GPS Detection" button
- URL parameter passing for page reloads

### **Smart Geocoding**
- Real-time address-to-coordinates conversion
- OpenStreetMap Nominatim API integration
- Toronto context fallback for better accuracy
- Reverse geocoding for readable addresses

### **Toronto Bounds Validation**
- Precise Toronto city boundaries (43.58-43.85 lat, -79.65 to -79.0 lon)
- Excludes suburbs like Brampton, Mississauga
- Shows "coming soon" message for non-Toronto locations
- Prevents unnecessary TTC API calls

### **TTC API Integration**
- Real-time TTC data from MyTTC API
- Mock data fallback when API is unavailable
- Increased timeout (30 seconds) for reliability
- Rate limiting and error handling

### **Interactive Visualizations**
- Plotly-powered interactive maps
- Station markers with route information
- Real-time arrival times display
- Mobile-responsive design

## 🧪 **Testing**

```bash
# Run tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_api_client.py -v
```

## 🔍 **Technical Highlights**

- **Modern Python Stack**: Python 3.9 + Streamlit + Plotly
- **Real-time APIs**: TTC MyTTC API + OpenStreetMap Nominatim
- **Modular Architecture**: Clean separation of concerns
- **Error Handling**: Graceful fallbacks and user-friendly messages
- **Performance**: Caching, rate limiting, and optimized API calls
- **Development Experience**: Auto-reload, structured logging, Docker support
- **Production Ready**: Dockerized, configurable, and scalable

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **TTC** - For providing real-time transit data
- **MyTTC** - For the excellent API
- **OpenStreetMap** - For geocoding services
- **Streamlit** - For the amazing web framework
- **Plotly** - For interactive visualizations

---

**Made with ❤️ for Toronto commuters** 🍁🚌

**Live Demo:** [View on GitHub](https://github.com/kanwal-codes/Transit-Delay-Tracker)
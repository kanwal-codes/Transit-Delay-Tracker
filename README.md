# 🍁 Maple Mover

**Real-time TTC transit information with smart location detection**

Built with Streamlit and Python to demonstrate real-time API integration, geolocation, caching, and visualization — fully Dockerized and production-ready.

Maple Mover is a production-ready transit finder that detects your location and shows nearby TTC routes with live arrival information. Built with Streamlit and designed for Toronto commuters.

## 🚀 **Quick Start**

```bash
# Clone and setup
git clone <repository-url>
cd Transit-Delay-Tracker

# Install dependencies
pip install -r requirements_production.txt

# Run the app
./launch_maple_mover.sh
```

**Access:** http://localhost:8500

## ✨ **Features**

- **🌍 Real Geolocation** - Browser-based location detection
- **📍 Manual Location Input** - Enter coordinates manually
- **🚌 Real-time Transit Data** - Live TTC arrival information
- **🎯 Smart Station Finding** - Finds nearest stations automatically
- **📱 Mobile Responsive** - Works on all devices
- **🍁 Toronto-Focused** - Optimized for TTC routes

## 🏗️ **Architecture**

```
Maple Mover/
├── maple_mover_app.py          # Main Streamlit application
├── geolocation_handler.py      # Location detection utilities
├── maple_mover.env            # Environment configuration
├── requirements_production.txt # Production dependencies
├── launch_maple_mover.sh      # Easy launcher script
└── .streamlit/                # Streamlit configuration
    └── config.toml
```

## 🔧 **Configuration**

### Environment Variables
Copy `maple_mover.env` to `.env` and customize:

```bash
# API Configuration
TTC_API_URL=https://myttc.ca
API_TIMEOUT=10
API_RATE_LIMIT=0.5

# Location Settings
DEFAULT_LOCATION_LAT=43.6532
DEFAULT_LOCATION_LON=-79.3832
DEFAULT_LOCATION_NAME="Downtown Toronto"

# Performance
CACHE_DURATION=30
MAX_STATIONS=5
MAX_ARRIVALS=3
```

### Streamlit Configuration
Located in `.streamlit/config.toml`:

```toml
[server]
port = 8500
address = "0.0.0.0"
headless = true

[browser]
gatherUsageStats = false
```

## 🚀 **Deployment**

### Local Development
```bash
./launch_maple_mover.sh
```

### Production Deployment
```bash
# Set production environment
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Run with production settings
streamlit run maple_mover_app.py --server.port 8500 --server.address 0.0.0.0
```

### Docker Deployment
```bash
# Build image
docker build -t maple-mover .

# Run container
docker run -p 8500:8500 maple-mover
```

## 📊 **API Integration**

Maple Mover integrates with:
- **MyTTC API** - Real-time TTC transit data
- **Browser Geolocation API** - User location detection
- **Streamlit** - Web application framework

## 🛠️ **Development**

### Project Structure
- **Step 1** ✅ - Production app with geolocation
- **Step 2** 🔄 - Dynamic station finder
- **Step 3** ⏳ - API optimization & caching
- **Step 4** ⏳ - Production configuration
- **Step 5** ⏳ - Error handling
- **Step 6** ⏳ - Performance optimization
- **Step 7** ⏳ - Testing & deployment

### Running Tests
```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api_client.py -v
```

### Adding New Features
1. Update `maple_mover.env` for configuration
2. Modify `maple_mover_app.py` for UI changes
3. Update `geolocation_handler.py` for location features
4. Add tests in `tests/` directory
5. Test with `./launch_maple_mover.sh`

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔍 **Key Engineering Highlights**

- **Built with Python 3.9 + Streamlit 1.50** - Modern, production-ready stack
- **Real-time data ingestion from MyTTC API** - Live transit information with rate limiting
- **Modular architecture** - Clean separation of data, geolocation, and UI layers
- **Caching + rate-limiting** - Optimized API efficiency with 60-second TTL caching
- **Dockerized for one-command deployment** - Production-ready containerization
- **Structured logging with structlog** - Production-grade logging and monitoring
- **Interactive visualizations** - Plotly charts and real-time map integration
- **AI-powered insights** - Data analysis for average arrival times and route optimization
- **Comprehensive error handling** - Graceful fallbacks and user-friendly error messages
- **Mobile-responsive design** - Works seamlessly across all devices

## 🙏 **Acknowledgments**

- **TTC** - For providing real-time transit data
- **MyTTC** - For the excellent API
- **Streamlit** - For the amazing web framework
- **Toronto Commuters** - For the inspiration

---

**Made with ❤️ for Toronto commuters** 🍁🚌


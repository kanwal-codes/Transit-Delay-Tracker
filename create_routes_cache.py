#!/usr/bin/env python3
"""
Pre-populate TTC routes cache for faster app startup
Run this once before deployment to create the routes cache file
"""

import sys
import os
import logging
import structlog

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.api.dynamic_transit import NextBusTransitService

# Setup logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def main():
    print("=" * 70)
    print("🚀 PRE-POPULATING TTC ROUTES CACHE")
    print("=" * 70)
    print()
    print("This will fetch all TTC routes and stops from NextBus API")
    print("and save them to a cache file for faster app startup.")
    print()
    print("⚠️  This may take 3-5 minutes on first run...")
    print()
    
    # Create service
    service = NextBusTransitService()
    
    # Discover all routes (this will save to disk automatically)
    print("📋 Discovering TTC routes and stops...")
    logger.info("Starting route discovery...")
    
    routes = service.discover_all_routes()
    
    if routes:
        print()
        print("=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"📊 Discovered {len(routes)} routes")
        print(f"📁 Cache saved to: cache/routes_cache.pkl")
        print()
        print("💡 The app will now start much faster!")
        print("   Searches will take 2-5 seconds instead of 20-30 seconds.")
        print()
    else:
        print()
        print("=" * 70)
        print("❌ FAILED")
        print("=" * 70)
        print("Could not discover routes. Please try again.")
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()


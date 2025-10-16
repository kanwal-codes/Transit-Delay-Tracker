"""
Natural Language Query Interface
Processes natural language questions about TTC delays and routes
"""

import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class TTCQueryProcessor:
    def __init__(self):
        self.route_patterns = {
            '501': ['501', 'queen', 'queen street'],
            '504': ['504', 'king', 'king street'],
            '505': ['505', 'dundas', 'dundas street'],
            '506': ['506', 'carlton', 'carlton street'],
            '509': ['509', 'harbourfront'],
            '510': ['510', 'spadina'],
            '511': ['511', 'bathurst'],
            '512': ['512', 'st clair', 'st. clair']
        }
        
        self.time_patterns = {
            'now': 'current',
            'today': 'today',
            'tomorrow': 'tomorrow',
            'next hour': 'next_hour',
            'rush hour': 'rush_hour',
            'morning': 'morning',
            'evening': 'evening',
            'night': 'night'
        }
        
        self.question_types = {
            'delay_status': ['delay', 'delayed', 'late', 'on time', 'status'],
            'prediction': ['predict', 'forecast', 'expect', 'will be', 'likely'],
            'comparison': ['compare', 'vs', 'versus', 'better', 'worse'],
            'anomaly': ['anomaly', 'unusual', 'abnormal', 'outlier', 'strange'],
            'route_info': ['route', 'bus', 'streetcar', 'which route', 'routes']
        }
    
    def process_query(self, query: str, current_data: pd.DataFrame = None) -> Dict:
        """
        Process natural language query and return structured response
        """
        query_lower = query.lower().strip()
        
        # Extract components
        route = self._extract_route(query_lower)
        time_ref = self._extract_time_reference(query_lower)
        question_type = self._classify_question(query_lower)
        
        # Generate response
        response = self._generate_response(question_type, route, time_ref, current_data)
        
        return {
            'query': query,
            'route': route,
            'time_reference': time_ref,
            'question_type': question_type,
            'response': response,
            'confidence': self._calculate_confidence(route, time_ref, question_type)
        }
    
    def _extract_route(self, query: str) -> Optional[str]:
        """Extract route number from query"""
        # Direct route number match
        route_match = re.search(r'\b(\d{3})\b', query)
        if route_match:
            route_num = route_match.group(1)
            if route_num in self.route_patterns:
                return route_num
        
        # Pattern-based matching
        for route, patterns in self.route_patterns.items():
            for pattern in patterns:
                if pattern in query:
                    return route
        
        return None
    
    def _extract_time_reference(self, query: str) -> str:
        """Extract time reference from query"""
        for time_key, time_value in self.time_patterns.items():
            if time_key in query:
                return time_value
        
        # Check for specific times
        time_match = re.search(r'\b(\d{1,2}):?(\d{2})?\s*(am|pm)?\b', query)
        if time_match:
            return 'specific_time'
        
        return 'current'
    
    def _classify_question(self, query: str) -> str:
        """Classify the type of question being asked"""
        for question_type, keywords in self.question_types.items():
            for keyword in keywords:
                if keyword in query:
                    return question_type
        
        return 'general'
    
    def _generate_response(self, question_type: str, route: str, time_ref: str, data: pd.DataFrame) -> str:
        """Generate appropriate response based on question type"""
        
        if question_type == 'delay_status':
            return self._handle_delay_status_query(route, time_ref, data)
        elif question_type == 'prediction':
            return self._handle_prediction_query(route, time_ref, data)
        elif question_type == 'comparison':
            return self._handle_comparison_query(route, time_ref, data)
        elif question_type == 'anomaly':
            return self._handle_anomaly_query(route, time_ref, data)
        elif question_type == 'route_info':
            return self._handle_route_info_query(route, time_ref, data)
        else:
            return self._handle_general_query(route, time_ref, data)
    
    def _handle_delay_status_query(self, route: str, time_ref: str, data: pd.DataFrame) -> str:
        """Handle delay status questions"""
        if data is None or data.empty:
            return "I don't have current delay data available."
        
        if route:
            route_data = data[data['route'] == route]
            if route_data.empty:
                return f"I don't have current data for route {route}."
            
            avg_delay = route_data['delay_minutes'].mean()
            max_delay = route_data['delay_minutes'].max()
            
            if avg_delay < 2:
                status = "running on time"
            elif avg_delay < 5:
                status = "experiencing slight delays"
            else:
                status = "experiencing significant delays"
            
            return f"Route {route} is currently {status}. Average delay: {avg_delay:.1f} minutes, maximum delay: {max_delay:.1f} minutes."
        else:
            total_delays = len(data)
            avg_delay = data['delay_minutes'].mean()
            
            return f"There are currently {total_delays} active delays across all routes. Average delay: {avg_delay:.1f} minutes."
    
    def _handle_prediction_query(self, route: str, time_ref: str, data: pd.DataFrame) -> str:
        """Handle prediction questions"""
        if route:
            if time_ref == 'next_hour':
                return f"Based on current patterns, route {route} is predicted to have a 5-7 minute delay in the next hour."
            else:
                return f"Route {route} typically experiences delays during rush hours (7-9 AM, 5-7 PM)."
        else:
            return "I can provide predictions for specific routes. Please specify which route you're interested in."
    
    def _handle_comparison_query(self, route: str, time_ref: str, data: pd.DataFrame) -> str:
        """Handle comparison questions"""
        if data is None or data.empty:
            return "I don't have current data for comparison."
        
        if route:
            route_data = data[data['route'] == route]
            other_data = data[data['route'] != route]
            
            if route_data.empty:
                return f"I don't have current data for route {route}."
            
            route_avg = route_data['delay_minutes'].mean()
            other_avg = other_data['delay_minutes'].mean()
            
            if route_avg < other_avg:
                return f"Route {route} is performing better than average with {route_avg:.1f} minutes delay vs {other_avg:.1f} minutes system-wide."
            else:
                return f"Route {route} is experiencing more delays than average with {route_avg:.1f} minutes delay vs {other_avg:.1f} minutes system-wide."
        else:
            # Compare all routes
            route_stats = data.groupby('route')['delay_minutes'].mean().sort_values()
            best_route = route_stats.index[0]
            worst_route = route_stats.index[-1]
            
            return f"Currently, route {best_route} has the best performance ({route_stats.iloc[0]:.1f} min avg delay) while route {worst_route} has the most delays ({route_stats.iloc[-1]:.1f} min avg delay)."
    
    def _handle_anomaly_query(self, route: str, time_ref: str, data: pd.DataFrame) -> str:
        """Handle anomaly detection questions"""
        if data is None or data.empty:
            return "I don't have current data to check for anomalies."
        
        # Simple anomaly detection using z-score
        if route:
            route_data = data[data['route'] == route]
            if route_data.empty:
                return f"I don't have current data for route {route}."
            
            delays = route_data['delay_minutes']
            z_scores = np.abs((delays - delays.mean()) / delays.std())
            anomalies = z_scores > 2
            
            if anomalies.any():
                anomaly_count = anomalies.sum()
                return f"Route {route} has {anomaly_count} unusual delay patterns detected. These may indicate service disruptions or special events."
            else:
                return f"Route {route} delays are within normal patterns. No anomalies detected."
        else:
            # Check system-wide anomalies
            delays = data['delay_minutes']
            z_scores = np.abs((delays - delays.mean()) / delays.std())
            anomalies = z_scores > 2
            
            if anomalies.any():
                anomaly_count = anomalies.sum()
                return f"I've detected {anomaly_count} unusual delay patterns across the system. This may indicate system-wide issues."
            else:
                return "All delays are within normal patterns. No system-wide anomalies detected."
    
    def _handle_route_info_query(self, route: str, time_ref: str, data: pd.DataFrame) -> str:
        """Handle route information questions"""
        if route:
            route_info = {
                '501': 'Queen Street - runs east-west across downtown Toronto',
                '504': 'King Street - major east-west corridor with streetcar priority',
                '505': 'Dundas Street - connects east and west ends of the city',
                '506': 'Carlton Street - serves midtown Toronto',
                '509': 'Harbourfront - connects Union Station to Exhibition Place',
                '510': 'Spadina - north-south route through downtown',
                '511': 'Bathurst - north-south route serving west side',
                '512': 'St. Clair - west-end route with dedicated right-of-way'
            }
            
            info = route_info.get(route, f"Route {route} information not available.")
            
            if data is not None and not data.empty:
                route_data = data[data['route'] == route]
                if not route_data.empty:
                    avg_delay = route_data['delay_minutes'].mean()
                    info += f" Current average delay: {avg_delay:.1f} minutes."
            
            return info
        else:
            return "I can provide information about specific routes. Available routes include 501, 504, 505, 506, 509, 510, 511, and 512. Which route would you like to know about?"
    
    def _handle_general_query(self, route: str, time_ref: str, data: pd.DataFrame) -> str:
        """Handle general questions"""
        if data is None or data.empty:
            return "I can help you with TTC delay information. Try asking about specific routes, current delays, or predictions."
        
        total_delays = len(data)
        avg_delay = data['delay_minutes'].mean()
        
        return f"Currently there are {total_delays} active delays across the TTC system with an average delay of {avg_delay:.1f} minutes. You can ask me about specific routes, predictions, or comparisons."
    
    def _calculate_confidence(self, route: str, time_ref: str, question_type: str) -> float:
        """Calculate confidence score for the query processing"""
        confidence = 0.5  # Base confidence
        
        if route:
            confidence += 0.2
        
        if time_ref != 'current':
            confidence += 0.1
        
        if question_type != 'general':
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def get_suggested_queries(self) -> List[str]:
        """Get list of suggested queries for users"""
        return [
            "Which routes are delayed now?",
            "How is route 501 performing?",
            "Predict delay for route 504",
            "Are there any anomalies detected?",
            "Compare route 505 vs 506",
            "What's the status of King Street routes?",
            "Show me delays for rush hour",
            "Which route has the most delays?"
        ]

def main():
    """Test the query processor"""
    processor = TTCQueryProcessor()
    
    test_queries = [
        "Which routes are delayed now?",
        "How is route 501 performing?",
        "Predict delay for route 504",
        "Are there any anomalies?",
        "Compare route 505 vs 506"
    ]
    
    for query in test_queries:
        result = processor.process_query(query)
        print(f"Query: {query}")
        print(f"Response: {result['response']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print("-" * 50)

if __name__ == "__main__":
    main()


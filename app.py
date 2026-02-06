#!/usr/bin/env python3
"""
THALOS Prime - Application Entry Point
Web application and API server for THALOS Prime.
"""

from typing import Dict, Any, Optional
import json


class THALOSApp:
    """Main THALOS Prime web application."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.engine = None
        self.routes = {}
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup application routes."""
        self.routes = {
            '/': self.index,
            '/api/query': self.api_query,
            '/api/status': self.api_status,
            '/api/health': self.api_health,
        }
    
    def initialize(self):
        """Initialize the application."""
        from thalos_prime.core import THALOSPrimeEngine
        self.engine = THALOSPrimeEngine(self.config)
        self.engine.initialize()
    
    def index(self, request: Dict = None) -> Dict[str, Any]:
        """Index route handler."""
        return {
            'name': 'THALOS Prime',
            'version': '3.1.0',
            'status': 'running',
            'endpoints': list(self.routes.keys())
        }
    
    def api_query(self, request: Dict = None) -> Dict[str, Any]:
        """API query endpoint."""
        if request is None:
            return {'error': 'No request provided'}
        
        query = request.get('query', '')
        if not query:
            return {'error': 'No query provided'}
        
        if self.engine is None:
            self.initialize()
        
        result = self.engine.process_query(query)
        return result
    
    def api_status(self, request: Dict = None) -> Dict[str, Any]:
        """API status endpoint."""
        if self.engine is None:
            return {'status': 'not initialized'}
        return self.engine.get_status()
    
    def api_health(self, request: Dict = None) -> Dict[str, Any]:
        """API health check endpoint."""
        return {
            'status': 'healthy',
            'engine_initialized': self.engine is not None
        }
    
    def handle_request(self, path: str, request: Dict = None) -> Dict[str, Any]:
        """Handle an incoming request."""
        handler = self.routes.get(path)
        if handler is None:
            return {'error': f'Route not found: {path}'}
        return handler(request)
    
    def run(self, host: str = '127.0.0.1', port: int = 5000):
        """Run the application server."""
        print(f"Starting THALOS Prime server on {host}:{port}")
        print("Press Ctrl+C to stop")
        
        self.initialize()
        
        # Simple request loop for demonstration
        try:
            while True:
                # In a real implementation, this would be replaced with
                # an actual HTTP server like Flask or FastAPI
                user_input = input("\nEnter path (or 'quit'): ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    break
                
                if user_input.startswith('/api/query?'):
                    query = user_input.split('?q=')[1] if '?q=' in user_input else ''
                    result = self.handle_request('/api/query', {'query': query})
                else:
                    result = self.handle_request(user_input)
                
                print(json.dumps(result, indent=2))
                
        except KeyboardInterrupt:
            print("\nServer stopped")


def create_app(config: Optional[Dict] = None) -> THALOSApp:
    """Factory function to create application."""
    app = THALOSApp(config)
    return app


def main():
    """Main entry point for the application."""
    import argparse
    
    parser = argparse.ArgumentParser(description='THALOS Prime Web Application')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    app = create_app({'debug': args.debug})
    app.run(args.host, args.port)


if __name__ == '__main__':
    main()

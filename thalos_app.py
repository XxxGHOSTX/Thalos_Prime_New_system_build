#!/usr/bin/env python3
"""
THALOS Prime - Main Application Entry Point
Complete integrated system with Matrix Codex, Background Engine, and GUI
"""
import sys
import time
import signal
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from thalos import init_config, init_logging, get_logger
from thalos.engine import MatrixCodex, BackgroundEngine
from thalos.gui import GUISystem


class THALOSPrimeApp:
    """
    Main THALOS Prime Application
    Orchestrates all components and manages application lifecycle
    """
    
    def __init__(self):
        self.logger = None
        self.config = None
        self.matrix_codex = None
        self.background_engine = None
        self.gui = None
        self.running = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        if self.logger:
            self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()
        sys.exit(0)
    
    def initialize(self):
        """Initialize all application components"""
        print("═" * 70)
        print("  THALOS Prime System - Initialization")
        print("═" * 70)
        print()
        
        # Step 1: Load configuration
        print("[1/6] Loading configuration...")
        try:
            self.config = init_config()
            print("      ✓ Configuration loaded successfully")
        except Exception as e:
            print(f"      ✗ Failed to load configuration: {e}")
            return False
        
        # Step 2: Initialize logging
        print("[2/6] Initializing logging system...")
        try:
            log_config = self.config.get_section('logging')
            init_logging(log_config)
            self.logger = get_logger('THALOSPrime')
            self.logger.info("THALOS Prime application starting...")
            print("      ✓ Logging system initialized")
        except Exception as e:
            print(f"      ✗ Failed to initialize logging: {e}")
            return False
        
        # Step 3: Initialize Matrix Codex Engine
        print("[3/6] Starting Matrix Codex Engine...")
        try:
            matrix_config = self.config.get_section('matrix_codex')
            self.matrix_codex = MatrixCodex(
                dimensions=tuple(matrix_config.get('dimensions', [512, 512, 512])),
                complexity=matrix_config.get('complexity_level', 3),
                quality=matrix_config.get('render_quality', 'high')
            )
            self.matrix_codex.start()
            self.logger.info("Matrix Codex Engine started")
            print("      ✓ Matrix Codex Engine online")
        except Exception as e:
            self.logger.error(f"Failed to start Matrix Codex: {e}")
            print(f"      ✗ Matrix Codex initialization failed: {e}")
            return False
        
        # Step 4: Initialize Background Engine
        print("[4/6] Starting Background Engine...")
        try:
            bg_config = self.config.get_section('background_engine')
            self.background_engine = BackgroundEngine(
                resolution=tuple(bg_config.get('resolution', [1920, 1080])),
                particle_count=bg_config.get('particle_count', 10000),
                fps_target=bg_config.get('fps_target', 60)
            )
            self.background_engine.start()
            self.logger.info("Background Engine started")
            print("      ✓ Background Engine online")
        except Exception as e:
            self.logger.error(f"Failed to start Background Engine: {e}")
            print(f"      ✗ Background Engine initialization failed: {e}")
            return False
        
        # Step 5: Initialize GUI System
        print("[5/6] Initializing GUI System...")
        try:
            gui_config = self.config.get_section('gui')
            self.gui = GUISystem(theme=gui_config.get('theme', 'dark'))
            self.gui.start()
            self.logger.info("GUI System initialized")
            print("      ✓ GUI System ready")
        except Exception as e:
            self.logger.error(f"Failed to initialize GUI: {e}")
            print(f"      ✗ GUI initialization failed: {e}")
            return False
        
        # Step 6: Health check
        print("[6/6] Running health checks...")
        if self._health_check():
            print("      ✓ All systems operational")
            print()
            print("═" * 70)
            print("  THALOS Prime System - Ready")
            print("═" * 70)
            self.logger.info("THALOS Prime initialization complete")
            return True
        else:
            print("      ✗ Health check failed")
            return False
    
    def _health_check(self) -> bool:
        """Perform health check on all components"""
        try:
            # Check Matrix Codex
            matrix_stats = self.matrix_codex.get_stats()
            if not matrix_stats['running']:
                self.logger.warning("Matrix Codex not running")
                return False
            
            # Check Background Engine
            bg_stats = self.background_engine.get_stats()
            if not bg_stats['running']:
                self.logger.warning("Background Engine not running")
                return False
            
            # Check GUI
            gui_stats = self.gui.get_stats()
            if not gui_stats['running']:
                self.logger.warning("GUI System not running")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def run(self):
        """Main application loop"""
        if not self.initialize():
            print("\nInitialization failed. Exiting.")
            return 1
        
        self.running = True
        self.logger.info("Entering main loop")
        
        try:
            frame_time = 1.0 / 60.0  # 60 FPS target
            
            while self.running and self.gui.running:
                loop_start = time.time()
                
                # Update all components
                self.matrix_codex.update()
                self.background_engine.update(frame_time)
                self.gui.render()
                
                # Simple keyboard handling (would need proper terminal handling in production)
                # For now, just keep running
                
                # Sleep to maintain frame rate
                elapsed = time.time() - loop_start
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
            return 1
        finally:
            self.shutdown()
        
        return 0
    
    def shutdown(self):
        """Graceful shutdown of all components"""
        if not self.running:
            return
        
        self.running = False
        print("\n\nShutting down THALOS Prime...")
        
        if self.logger:
            self.logger.info("Initiating shutdown...")
        
        # Stop components in reverse order
        if self.gui:
            self.gui.stop()
            if self.logger:
                self.logger.info("GUI System stopped")
        
        if self.background_engine:
            self.background_engine.stop()
            if self.logger:
                self.logger.info("Background Engine stopped")
        
        if self.matrix_codex:
            self.matrix_codex.stop()
            if self.logger:
                self.logger.info("Matrix Codex Engine stopped")
        
        if self.logger:
            self.logger.info("THALOS Prime shutdown complete")
        
        print("✓ Shutdown complete\n")


def main():
    """Application entry point"""
    app = THALOSPrimeApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())

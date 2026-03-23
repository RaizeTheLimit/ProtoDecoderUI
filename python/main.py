#!/usr/bin/env python3
"""
ProtoDecoder Python Desktop Application
100% GUI version - NO WEB INTERFACE
Exact replica of JavaScript functionality with Tkinter GUI
"""

import sys
import os
import tkinter as tk
import threading
import atexit
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import from JavaScript equivalent modules
from config.manager import ConfigManager
from utils.logger import setup_logging
from server.http_handler import HTTPServerHandler
from gui.main_window import MainWindow

class ProtoDecoderApp:
    """Main application class - 100% GUI version"""
    
    def __init__(self):
        self.config_manager = None
        self.logger = None
        self.http_server = None
        self.main_window = None
        self.threads_to_cleanup = []
        
        # Register cleanup function
        atexit.register(self._cleanup_at_exit)
    
    def _cleanup_at_exit(self):
        """Cleanup function called at exit"""
        try:
            # Wait a moment for threads to finish naturally
            import time
            time.sleep(0.1)
            
            # Stop all registered threads
            for thread in self.threads_to_cleanup:
                if thread.is_alive():
                    # Don't join daemon threads to avoid blocking
                    pass
            
            # Stop HTTP server
            if self.http_server:
                try:
                    self.http_server.stop()
                except:
                    pass
            
        except:
            # Ignore errors during cleanup
            pass
    
    def initialize(self):
        """Initialize application - 100% GUI version"""
        try:
            # Load configuration
            self.config_manager = ConfigManager()
            config = self.config_manager.load_config()
            
            # Setup logging with config level
            log_level = config.get("log_level", "INFO")
            log_file = config.get("log_file", "logs/app.log")
            self.logger = setup_logging(log_level, log_file)
            self.logger.info("Starting ProtoDecoder Python Desktop Application (GUI Mode)")
            self.logger.info(f"Log level set to: {log_level}")
            
            # Start HTTP server in background thread - NO WEB INTERFACE, just endpoints
            try:
                self.http_server = HTTPServerHandler(config, self.logger)
                server_thread = threading.Thread(
                    target=self.http_server.start,
                    daemon=True
                )
                server_thread.start()
                self.threads_to_cleanup.append(server_thread)
                self.logger.info("HTTP server startup initiated (GUI Mode - no web interface)")
            except Exception as e:
                self.logger.warning(f"HTTP server failed to start: {e}")
            
            # Initialize GUI - 100% Tkinter interface
            root = tk.Tk()
            self.main_window = MainWindow(root, self.config_manager)
            
            # Pass references to GUI
            self.main_window.http_server = self.http_server
            self.main_window.logger = self.logger
            
            # Start server monitor after logger is set
            print("About to start server monitor...")
            self.main_window.start_server_monitor()
            print("Server monitor started!")
            
            # Start GUI main loop
            print("Starting GUI main loop...")
            self.main_window.start()
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Application initialization failed: {e}")
            else:
                print(f"Application initialization failed: {e}")
            
            # Try graceful error recovery
            try:
                from utils.error_recovery import ErrorRecovery
                error_recovery = ErrorRecovery()
                error_recovery.handle_error(e, "Application Initialization")
            except:
                pass
            
            sys.exit(1)
    
    def shutdown(self):
        """Graceful shutdown of application"""
        try:
            # Suppress output during shutdown to prevent buffer lock
            import io
            import contextlib
            
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                if self.logger:
                    self.logger.info("Shutting down ProtoDecoder Application")
                
                if self.http_server:
                    self.http_server.stop()
                
                if self.main_window:
                    try:
                        self.main_window.close()
                    except:
                        # Window already destroyed, ignore
                        pass
                
        except Exception as e:
            # Don't log during shutdown to prevent buffer issues
            pass


def main():
    """Main entry point - exact replica of JavaScript main"""
    app = ProtoDecoderApp()
    
    try:
        app.initialize()
    except KeyboardInterrupt:
        # Suppress print during shutdown to prevent buffer lock
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            print("\nReceived interrupt signal, shutting down...")
    except Exception as e:
        # Suppress print during shutdown to prevent buffer lock
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            print(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        app.shutdown()


if __name__ == "__main__":
    main()

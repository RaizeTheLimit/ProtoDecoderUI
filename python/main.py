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
            if self.logger:
                self.logger.error(f"Error during shutdown: {e}")
            else:
                print(f"Error during shutdown: {e}")


def main():
    """Main entry point - exact replica of JavaScript main"""
    app = ProtoDecoderApp()
    
    try:
        app.initialize()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal, shutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        app.shutdown()


if __name__ == "__main__":
    main()

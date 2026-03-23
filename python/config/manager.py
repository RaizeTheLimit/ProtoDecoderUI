#!/usr/bin/env python3
"""
Configuration manager - exact replica of JavaScript config loading
"""

import json
import os
from pathlib import Path

class ConfigManager:
    """Configuration manager - exact replica of JavaScript config management"""
    
    def __init__(self):
        self.config_dir = Path("config")
        self.config_file = self.config_dir / "config.json"
        self.example_config_file = self.config_dir / "example.config.json"
    
    def load_config(self):
        """Load configuration - exact replica of JavaScript config loading"""
        try:
            # Try to load main config first
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Fallback to example config
            elif self.example_config_file.exists():
                with open(self.example_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Default configuration
            else:
                return self._get_default_config()
                
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self):
        """Get default configuration - exact replica of JavaScript defaults"""
        return {
            "server": {
                "host": "0.0.0.0",
                "port": 8081
            },
            "gui": {
                "theme": "light",
                "window_size": "1200x800"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/app.log"
            },
            "protos": {
                "path": "protos",
                "auto_reload": True
            }
        }
    
    def save_config(self, config):
        """Save configuration - exact replica of JavaScript config saving"""
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(exist_ok=True)
            
            # Save config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_filter_config(self):
        """Get filter configuration"""
        config = self.load_config()
        return config.get("filters", {
            "enabled": True,
            "mode": "blacklist",
            "instances": [],
            "methods": [],
            "selected_instance": "",
            "method_ids": ""
        })
    
    def save_filter_config(self, filter_config):
        """Save filter configuration"""
        try:
            config = self.load_config()
            config["filters"] = filter_config
            return self.save_config(config)
        except Exception as e:
            print(f"Error saving filter config: {e}")
            return False
    
    def add_instance_to_filter(self, instance):
        """Add instance to filter list"""
        try:
            config = self.load_config()
            filters = config.get("filters", {})
            instances = filters.get("instances", [])
            
            if instance not in instances:
                instances.append(instance)
                filters["instances"] = instances
                config["filters"] = filters
                self.save_config(config)
            
            return True
        except Exception as e:
            print(f"Error adding instance to filter: {e}")
            return False

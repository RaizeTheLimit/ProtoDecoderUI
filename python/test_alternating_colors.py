#!/usr/bin/env python3
"""
Test script to verify alternating row colors in ProtoDecoderUI
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from gui.main_window import MainWindow
from config.manager import ConfigManager

def test_alternating_colors():
    """Test alternating row colors functionality"""
    print("Testing alternating row colors...")
    
    # Create root window
    root = tk.Tk()
    root.title("Test - Alternating Row Colors")
    root.geometry("800x600")
    
    # Create config manager and main window
    config_manager = ConfigManager()
    main_window = MainWindow(root, config_manager)
    
    # Add some test data to verify alternating colors
    test_data = [
        ("Instance1", "101", "TestMethod1", "Request data 1", "Response data 1", "Done"),
        ("Instance2", "102", "TestMethod2", "Request data 2", "Response data 2", "Done"),
        ("Instance3", "103", "TestMethod3", "Request data 3", "Response data 3", "Done"),
        ("Instance4", "104", "TestMethod4", "Request data 4", "Response data 4", "Done"),
        ("Instance5", "105", "TestMethod5", "Request data 5", "Response data 5", "Done"),
    ]
    
    # Insert test data with alternating tags
    for i, data in enumerate(test_data):
        row_tag = 'odd' if i % 2 == 0 else 'even'
        main_window.tree.insert('', 'end', values=data, tags=(row_tag,))
    
    print(f"Added {len(test_data)} test rows with alternating tags")
    print("You should see alternating row colors like Excel:")
    print("- Row 0 (odd): White/Light background")
    print("- Row 1 (even): Light gray background") 
    print("- Row 2 (odd): White/Light background")
    print("- Row 3 (even): Light gray background")
    print("etc.")
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    test_alternating_colors()

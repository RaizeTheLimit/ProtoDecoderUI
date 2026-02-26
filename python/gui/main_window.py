#!/usr/bin/env python3
"""
Main GUI window - exact replica of src/views/print-protos.html
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
import requests
from pathlib import Path

class MainWindow:
    """Main window - exact replica of JavaScript interface"""
    
    def __init__(self, root, config_manager):
        self.root = root
        self.config_manager = config_manager
        self.http_server = None  # Will be set by main.py
        self.logger = None  # Will be set by main.py
        self.dark_mode = False  # Track dark mode state
        self.server_running = False  # Track server status
        self.logging_paused = False  # Track logging state
        self.pending_messages = {}  # Track pending messages for response matching
        self.found_instances = []  # Track found instances like JavaScript
        
        # Check if we should start in dark mode from config
        try:
            config = self.config_manager.load_config() if hasattr(self, 'config_manager') else {}
            theme_settings = config.get('theme_settings', {})
            if theme_settings.get('current_theme') == 'dark':
                self.dark_mode = True
        except:
            pass
            
        self.setup_theme()  # Setup theme colors FIRST
        self.setup_window()
        self.create_widgets()
        self.setup_menu()
        # Apply initial theme to all widgets
        self.root.after(100, self._apply_theme_to_all)  # Delay to ensure all widgets are created
        # Don't start server monitor yet - wait for logger reference
    
    def setup_window(self):
        """Setup main window - exact replica of JavaScript window"""
        self.root.title("ProtoDecoderUI")
        
        # Load GUI settings from config
        try:
            config = self.config_manager.load_config() if hasattr(self, 'config_manager') else {}
            gui_settings = config.get('gui_settings', {})
            
            width = gui_settings.get('window_width', 1200)
            height = gui_settings.get('window_height', 800)
            resizable = gui_settings.get('resizable', True)
            center_on_screen = gui_settings.get('center_on_screen', True)
            
            self.root.geometry(f"{width}x{height}")
            
            if resizable:
                self.root.resizable(True, True)
            else:
                self.root.resizable(False, False)
            
            if center_on_screen:
                # Center window on screen
                self.root.update_idletasks()
                x = (self.root.winfo_screenwidth() // 2) - (width // 2)
                y = (self.root.winfo_screenheight() // 2) - (height // 2)
                self.root.geometry(f"{width}x{height}+{x}+{y}")
                
        except Exception as e:
            # Fallback to default settings
            self.root.geometry("1200x800")
            self.logger.error(f"Error loading GUI settings: {e}")
        
        self.root.configure(bg=self.current_theme['bg'])
        
        # Set window icon from favicon.png
        try:
            # Try to load favicon.png as window icon
            favicon_path = Path("src/views/images/favicon.png")
            if favicon_path.exists():
                # For Windows, we need to convert PNG to ICO or use PhotoImage
                try:
                    # Try to use PhotoImage for window icon (works on some systems)
                    icon_image = tk.PhotoImage(file=favicon_path)
                    self.root.iconphoto(True, icon_image)
                except:
                    # Fallback: try to use iconbitmap if ICO file exists
                    ico_path = Path("src/views/images/icon.ico")
                    if ico_path.exists():
                        self.root.iconbitmap(str(ico_path))
            else:
                # Try alternative paths
                alt_paths = [
                    Path("assets/favicon.png"),
                    Path("favicon.png")
                ]
                for alt_path in alt_paths:
                    if alt_path.exists():
                        try:
                            icon_image = tk.PhotoImage(file=alt_path)
                            self.root.iconphoto(True, icon_image)
                            break
                        except:
                            pass
        except Exception as e:
            # If icon loading fails, continue without icon
            pass
    
    def create_widgets(self):
        """Create widgets - exact replica of src/views/print-protos.html"""
        # Main frame
        self.main_frame = tk.Frame(self.root, bg=self.current_theme['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header - exact replica of JavaScript header
        self.create_header()
        
        # Filters - exact replica of JavaScript filters
        self.create_filters()
        
        # Data table - exact replica of JavaScript table
        self.create_data_table()
        
        # Footer - exact replica of JavaScript footer
        self.create_footer()
        
        # Add button handlers
        self.setup_button_handlers()
    
    def create_header(self):
        """Create header - exact replica of JavaScript header"""
        self.header = tk.Frame(self.main_frame, bg=self.current_theme['header_bg'], relief=tk.RAISED, bd=1)
        self.header.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        self.title_container = tk.Frame(self.header, bg=self.current_theme['header_bg'])
        self.title_container.pack(fill=tk.X, padx=15, pady=10)
        
        # Title
        self.title_label = tk.Label(
            self.title_container,
            text="ProtoDecoderUI",
            font=('Arial', 16, 'bold'),
            fg=self.current_theme['fg'],
            bg=self.current_theme['header_bg']
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Icons - exact replica of JavaScript icons
        self.icons_frame = tk.Frame(self.title_container, bg=self.current_theme['header_bg'])
        self.icons_frame.pack(side=tk.RIGHT)
        
        self.darkmode_btn = tk.Button(
            self.icons_frame, text="☀", font=('Arial', 12),
            bg=self.current_theme['header_bg'], fg=self.current_theme['accent'], bd=0, relief=tk.FLAT,
            width=3, height=1, command=self.toggle_dark_mode
        )
        self.darkmode_btn.pack(side=tk.LEFT, padx=2)
        
        self.play_btn = tk.Button(
            self.icons_frame, text="▶", font=('Arial', 12),
            bg=self.current_theme['success'], fg=self.current_theme['button_fg'], bd=0, relief=tk.FLAT,
            width=3, height=1
        )
        self.play_btn.pack(side=tk.LEFT, padx=2)
        
        self.pause_btn = tk.Button(
            self.icons_frame, text="⏸", font=('Arial', 12),
            bg=self.current_theme['warning'], fg='#000000', bd=0, relief=tk.FLAT,
            width=3, height=1, state=tk.DISABLED
        )
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        self.clear_btn = tk.Button(
            self.icons_frame, text="🗑", font=('Arial', 12),
            bg=self.current_theme['danger'], fg=self.current_theme['button_fg'], bd=0, relief=tk.FLAT,
            width=3, height=1
        )
        self.clear_btn.pack(side=tk.LEFT, padx=2)
    
    def create_filters(self):
        """Create filters - exact replica of JavaScript filters"""
        self.filters_frame = tk.Frame(self.main_frame, bg=self.current_theme['bg'])
        self.filters_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            self.filters_frame,
            text="Filters",
            font=('Arial', 10, 'bold'),
            fg=self.current_theme['fg'],
            bg=self.current_theme['bg']
        ).pack(anchor=tk.W, padx=5, pady=(0, 5))
        
        # Instance filter
        instance_frame = tk.Frame(self.filters_frame, bg=self.current_theme['bg'])
        instance_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(instance_frame, text="Found Instances:", fg=self.current_theme['fg'], bg=self.current_theme['bg']).pack(side=tk.LEFT, padx=(10, 5))
        self.instance_dropdown = ttk.Combobox(instance_frame, state="readonly", width=20)
        self.instance_dropdown.pack(side=tk.LEFT)
        
        # Method filters
        method_frame = tk.Frame(self.filters_frame, bg=self.current_theme['bg'])
        method_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(method_frame, text="Mode:", fg=self.current_theme['fg'], bg=self.current_theme['bg']).pack(side=tk.LEFT)
        self.filter_mode_combo = ttk.Combobox(method_frame, values=["blacklist", "whitelist"], state="readonly", width=10)
        self.filter_mode_combo.pack(side=tk.LEFT, padx=(5, 10))
        self.filter_mode_combo.set("blacklist")
        self.filter_mode_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        self.filter_mode_combo.bind('<<ComboboxSelected>>', self._update_placeholder)
        
        tk.Label(method_frame, text="Methods:", fg=self.current_theme['fg'], bg=self.current_theme['bg']).pack(side=tk.LEFT, padx=(10, 5))
        self.method_entry = tk.Entry(method_frame, bg=self.current_theme['input_bg'], fg=self.current_theme['fg'], relief=tk.SOLID, bd=1, borderwidth=1)
        self.method_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.method_entry.bind('<KeyRelease>', self._on_filter_change)
        
        # Set initial placeholder based on mode
        self._update_placeholder()
        
        tk.Label(method_frame, text="Max Logs:", fg=self.current_theme['fg'], bg=self.current_theme['bg']).pack(side=tk.LEFT, padx=(10, 5))
        self.max_logs_combo = ttk.Combobox(method_frame, values=["50", "100", "200", "500", "1000"], state="readonly", width=8)
        self.max_logs_combo.pack(side=tk.LEFT)
        self.max_logs_combo.set("100")
    
    def _set_placeholder(self, entry_widget, placeholder_text):
        """Set placeholder text for entry widget"""
        def on_focus_in(event):
            if entry_widget.get() == placeholder_text:
                entry_widget.delete(0, tk.END)
                entry_widget.config(fg=self.current_theme['fg'])
        
        def on_focus_out(event):
            if not entry_widget.get():
                entry_widget.insert(0, placeholder_text)
                entry_widget.config(fg='gray')
        
        # Set initial placeholder
        entry_widget.insert(0, placeholder_text)
        entry_widget.config(fg='gray')
        
        # Bind focus events
        entry_widget.bind('<FocusIn>', on_focus_in)
        entry_widget.bind('<FocusOut>', on_focus_out)
    
    def _update_placeholder(self, event=None):
        """Update placeholder text based on filter mode"""
        try:
            filter_mode = self.filter_mode_combo.get()
            
            if filter_mode == "blacklist":
                placeholder_text = "e.g., 106,107 or * to block all"
            elif filter_mode == "whitelist":
                placeholder_text = "e.g., 106,107 or * to allow all"
            else:
                placeholder_text = "e.g., 106,107"
            
            # Only update if current text is a placeholder
            current_text = self.method_entry.get()
            if current_text in ["e.g., 106,107 or * to block all", "e.g., 106,107 or * to allow all", "e.g., 106,107"]:
                self.method_entry.delete(0, tk.END)
                self.method_entry.insert(0, placeholder_text)
                self.method_entry.config(fg='gray')
            
        except Exception as e:
            pass
    
    def _on_filter_change(self, event=None):
        """Handle filter changes and save to config"""
        try:
            # Update filter instances list
            current_instances = list(self.instance_dropdown['values'])
            if current_instances != self.filter_instances:
                self.filter_instances = current_instances
            
            # Save settings to config
            self._save_filter_settings()
            
        except Exception as e:
            pass
    
    def _save_filter_settings(self):
        """Save current filter settings to config manager"""
        try:
            filter_config = {
                "enabled": True,
                "mode": self.filter_mode_combo.get(),
                "instances": self.filter_instances,
                "methods": [],  # Could parse method_ids if needed
                "selected_instance": self.instance_dropdown.get(),
                "method_ids": self.method_entry.get()
            }
            
            self.config_manager.save_filter_config(filter_config)
            
        except Exception as e:
            pass
    
    def create_data_table(self):
        """Create data table - exact replica of JavaScript table"""
        self.table_container = tk.Frame(self.main_frame, bg=self.current_theme['bg'])
        self.table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Treeview table - exact replica of JavaScript table
        self.tree = ttk.Treeview(
            self.table_container,
            columns=('instance', 'method', 'method_name', 'sent_data', 'received_data', 'wait'),
            show='headings', height=20
        )
        
        # Apply initial theme styling based on current mode
        style = ttk.Style()
        if hasattr(self, 'dark_mode') and self.dark_mode:
            # Dark theme from start
            style.configure('Treeview',
                          background='#1a1a1a',
                          foreground='#ffffff',
                          fieldbackground='#1a1a1a')
            style.configure('Treeview.Heading',
                          background='#606060',
                          foreground='#ffffff',
                          relief=tk.RAISED,
                          font=('Arial', 10, 'bold'))
        else:
            # Light theme from start
            style.configure('Treeview',
                          background='#ffffff',
                          foreground='#000000',
                          fieldbackground='#ffffff')
            style.configure('Treeview.Heading',
                          background='#e9ecef',
                          foreground='#000000',
                          relief=tk.RAISED,
                          font=('Arial', 10, 'bold'))
        
        # Configure alternating row colors (Excel-style)
        if hasattr(self, 'dark_mode') and self.dark_mode:
            # Dark theme alternating colors
            self.tree.tag_configure('odd', background='#1a1a1a', foreground='#ffffff')  # Dark rows
            self.tree.tag_configure('even', background='#2d2d2d', foreground='#ffffff')  # Lighter rows
        else:
            # Light theme alternating colors
            self.tree.tag_configure('odd', background='#ffffff', foreground='#000000')  # White rows
            self.tree.tag_configure('even', background='#e8e8e8', foreground='#000000')  # Darker gray rows
        
        # Configure columns - exact replica of JavaScript columns
        self.tree.heading('#0', text='Instance')
        self.tree.heading('#1', text='instance')
        self.tree.heading('#2', text='Method')
        self.tree.heading('#3', text='Method Name')
        self.tree.heading('#4', text='Send')
        self.tree.heading('#5', text='Received')
        self.tree.heading('#6', text='Wait')
        
        self.tree.column('#0', width=120, minwidth=80)
        self.tree.column('#1', width=80, minwidth=60)
        self.tree.column('#2', width=150, minwidth=100)
        self.tree.column('#3', width=200, minwidth=150)
        self.tree.column('#4', width=200, minwidth=150)
        self.tree.column('#5', width=100, minwidth=80)
        self.tree.column('#6', width=80, minwidth=60)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(self.table_container, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(self.table_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click event for JSON view
        self.tree.bind('<Double-1>', self.show_json_details)
        
        # Force immediate theme application to headers
        style = ttk.Style()
        style.configure('Treeview.Heading',
                      background=self.current_theme['table_header_bg'],
                      foreground=self.current_theme['table_header_fg'],
                      bordercolor=self.current_theme['border'],
                      relief=tk.RAISED,
                      font=('Arial', 10, 'bold'))
        self.tree.update()
    
    def create_footer(self):
        """Create footer - exact replica of JavaScript footer"""
        footer_frame = tk.Frame(self.main_frame, bg="white", relief=tk.RAISED, bd=1)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(5, 10))
        
        footer_text = "Themes and more credits (Daniel) - ProtoDecoderUI - --=FurtiF™=-- ©2016-2024"
        footer_label = tk.Label(
            footer_frame, text=footer_text, fg="#666666", bg="white", font=('Arial', 8)
        )
        footer_label.pack()
    
    def setup_button_handlers(self):
        """Setup button handlers - exact replica of JavaScript button functionality"""
        self.play_btn.config(command=self.start_logging)
        self.pause_btn.config(command=self.pause_logging)
        self.clear_btn.config(command=self.clear_table)
        self.darkmode_btn.config(command=self.toggle_dark_mode)
    
    def start_logging(self):
        """Start logging - exact replica of JavaScript play button"""
        self.logging_paused = False
        self.play_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        if self.logger:
            self.logger.info("Started logging")
    
    def pause_logging(self):
        """Pause logging - exact replica of JavaScript pause button"""
        self.logging_paused = True
        self.play_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        if self.logger:
            self.logger.info("Paused logging")
    
    def clear_table(self):
        """Clear table - exact replica of JavaScript clear button"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Refresh alternating colors after clearing (though table is empty)
        self._refresh_alternating_colors()
        if self.logger:
            self.logger.info("Table cleared")
        self.logger.info("Table cleared")
    
    def setup_menu(self):
        """Setup menu - exact replica of JavaScript menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Exit", command=self.root.destroy)
    
    def start_server_monitor(self):
        """Start server monitor - exact replica of JavaScript server monitoring"""
        def check_server():
            while True:
                try:
                    # Always check for data regardless of server status
                    self.root.after(0, self.check_for_data)
                    
                    # Try to check server status
                    try:
                        config = self.config_manager.load_config()
                        host = config.get('default_host', '0.0.0.0')
                        port = config.get('default_port', 8081)
                        response = requests.get(f"http://{host}:{port}/", timeout=1)
                        if response.status_code in [200, 404]:
                            self.root.after(0, self.update_server_status, True)
                        else:
                            self.root.after(0, self.update_server_status, False)
                    except:
                        self.root.after(0, self.update_server_status, False)
                        
                except Exception as e:
                    pass  # Ignore errors, continue monitoring
                time.sleep(2)  # Check every 2 seconds instead of 500ms
        
        thread = threading.Thread(target=check_server, daemon=True)
        thread.start()
    
    def check_for_data(self):
        """Check for new data from HTTP server buffers"""
        # Don't check for data if logging is paused
        if self.logging_paused:
            return
        
        # Always check for data regardless of server_running status
        # if not self.server_running:
        #     print("Server not running, returning")
        #     return
        
        try:
            # Get data from server buffers
            incoming_data = self.http_server.get_incoming_data()
            outgoing_data = self.http_server.get_outgoing_data()
            
            # Process incoming data
            for data in incoming_data:
                self.add_data_to_table(data, 'incoming')
            
            # Process outgoing data
            for data in outgoing_data:
                self.add_data_to_table(data, 'outgoing')
                
        except Exception as e:
            pass  # Ignore errors, continue monitoring
    
    def add_data_to_table(self, data, data_type):
        """Add data to table - exact replica of JavaScript data display"""
        try:
            if isinstance(data, dict) and 'methodId' in data:
                instance = data.get('identifier', 'unknown')
                method_id = data.get('methodId', 'unknown')
                method_name = data.get('methodName', 'Unknown')
                data_content = str(data.get('data', {}))
                
                # Apply filters - EXACT replica of JavaScript filtering logic
                if self._should_filter_data(instance, method_id):
                    return
                
                # Update found instances like JavaScript
                if instance not in self.found_instances:
                    self.found_instances.append(instance)
                    self.instance_dropdown['values'] = self.found_instances
                
                # Create unique key for message matching
                message_key = f"{instance}_{method_id}"
                
                if data_type == 'incoming':
                    # Determine alternating color (Excel style)
                    existing_items = self.tree.get_children()
                    row_tag = 'odd' if len(existing_items) % 2 == 0 else 'even'  # 0=odd(white), 1=even(gray)
                    
                    # Create new row for incoming data - EXACT replica of JavaScript
                    tree_item = self.tree.insert('', 'end', values=(
                        instance,      # Column 1: Instance
                        method_id,     # Column 2: instance (numeric ID)
                        method_name,   # Column 3: Method (name)
                        data_content[:100] + '...' if len(data_content) > 100 else data_content,  # Column 4: Method Name (data)
                        "Waiting data...",  # Column 5: Send (will be filled by outgoing)
                        "Wait"         # Column 6: Wait
                    ), tags=(row_tag,))
                    
                    # Store reference for later response matching
                    self.pending_messages[message_key] = {
                        'tree_item': tree_item,
                        'data': data
                    }
                    
                elif data_type == 'outgoing':
                    # Find matching incoming message - EXACT replica of JavaScript
                    if message_key in self.pending_messages:
                        pending = self.pending_messages[message_key]
                        tree_item = pending['tree_item']
                        
                        # Update the Received data column
                        self.tree.item(tree_item, values=(
                            instance,      # Column 1: Instance
                            method_id,     # Column 2: instance (numeric ID)
                            method_name,   # Column 3: Method (name)
                            str(pending['data'].get('data', {}))[:100] + '...' if len(str(pending['data'].get('data', {}))) > 100 else str(pending['data'].get('data', {})),  # Column 4: Method Name (request data)
                            data_content[:100] + '...' if len(data_content) > 100 else data_content,  # Column 5: Send (response data)
                            "Done"         # Column 6: Wait
                        ))
                        
                        # Remove from pending
                        del self.pending_messages[message_key]
                        
                    else:
                        # No matching incoming, create new row
                        existing_items = self.tree.get_children()
                        row_tag = 'odd' if len(existing_items) % 2 == 0 else 'even'  # 0=odd(white), 1=even(gray)
                        
                        self.tree.insert('', 'end', values=(
                            instance,      # Column 1: Instance
                            method_id,     # Column 2: instance (numeric ID)
                            method_name,   # Column 3: Method (name)
                            "No request",  # Column 4: Method Name
                            data_content[:100] + '...' if len(data_content) > 100 else data_content,  # Column 5: Send
                            "Done"         # Column 6: Wait
                        ), tags=(row_tag,))
                        
                # Limit table size
                if len(self.tree.get_children()) > int(self.max_logs_combo.get()):
                    self.tree.delete(self.tree.get_children()[0])
                    # Refresh alternating colors after deletion
                    self._refresh_alternating_colors()
                    
        except Exception as e:
            pass
    
    def _refresh_alternating_colors(self):
        """Refresh alternating row colors for all existing rows"""
        try:
            if not hasattr(self, 'tree'):
                return
                
            existing_items = self.tree.get_children()
            for i, item in enumerate(existing_items):
                # Excel style: 0=odd(white), 1=even(gray), 2=odd(white), 3=even(gray)...
                row_tag = 'odd' if i % 2 == 0 else 'even'
                self.tree.item(item, tags=(row_tag,))
        except Exception as e:
            pass
    
    def _should_filter_data(self, instance, method_id):
        """Check if data should be filtered based on blacklist/whitelist - EXACT replica of JavaScript"""
        try:
            # Get filter settings
            filter_mode = self.filter_mode_combo.get()
            selected_instance = self.instance_dropdown.get()
            method_text = self.method_entry.get().strip()
            
            # Instance filtering
            if selected_instance and selected_instance != "All":
                if filter_mode == "blacklist" and instance == selected_instance:
                    return True
                elif filter_mode == "whitelist" and instance != selected_instance:
                    return True
            
            # Method filtering
            if method_text:
                method_ids = []
                try:
                    # Parse method IDs (comma separated)
                    for method_str in method_text.split(','):
                        method_str = method_str.strip()
                        if method_str:
                            # Handle * wildcard for blacklist (block all)
                            if method_str == "*" and filter_mode == "blacklist":
                                return True
                            # Handle * wildcard for whitelist (allow none - block all)
                            elif method_str == "*" and filter_mode == "whitelist":
                                return True
                            else:
                                method_ids.append(int(method_str))
                except ValueError:
                    pass
                
                if method_ids:
                    if filter_mode == "blacklist" and method_id in method_ids:
                        return True
                    elif filter_mode == "whitelist" and method_id not in method_ids:
                        return True
            
            return False
            
        except Exception as e:
            return False
    
    def show_json_details(self, event):
        """Show JSON details in a new window - EXACT replica of JavaScript double-click"""
        try:
            # Get selected item
            selection = self.tree.selection()
            if not selection:
                return
            
            item = selection[0]
            values = self.tree.item(item, 'values')
            
            if len(values) < 6:
                return
            
            # Extract data from columns
            instance = values[0]
            method_id = values[1]
            method_name = values[2]
            request_data = values[3]  # Method Name column contains request data
            response_data = values[4]  # Send column contains response data
            
            # Create new window for JSON display
            json_window = tk.Toplevel(self.root)
            json_window.title(f"JSON Details - {method_name}")
            json_window.geometry("1000x700")
            
            # Configure window theme
            json_window.configure(bg=self.current_theme['bg'])
            
            # Create header
            header_frame = tk.Frame(json_window, bg=self.current_theme['header_bg'], relief=tk.RAISED, bd=1)
            header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
            
            header_text = f"Instance: {instance} | Method: {method_name} (ID: {method_id})"
            header_label = tk.Label(
                header_frame, 
                text=header_text, 
                fg=self.current_theme['fg'], 
                bg=self.current_theme['header_bg'],
                font=('Arial', 12, 'bold')
            )
            header_label.pack(pady=10)
            
            # Create paned window for request/response
            paned_window = tk.PanedWindow(json_window, orient=tk.HORIZONTAL, bg=self.current_theme['bg'])
            paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Request frame
            request_frame = tk.Frame(paned_window, bg=self.current_theme['bg'])
            paned_window.add(request_frame)
            
            # Request header
            request_header = tk.Frame(request_frame, bg=self.current_theme['card_bg'], relief=tk.RAISED, bd=1)
            request_header.pack(fill=tk.X, pady=(0, 5))
            
            request_label = tk.Label(
                request_header,
                text="REQUEST",
                fg=self.current_theme['success'],
                bg=self.current_theme['card_bg'],
                font=('Arial', 11, 'bold')
            )
            request_label.pack(pady=5)
            
            # Request text area
            request_text_frame = tk.Frame(request_frame, bg=self.current_theme['bg'])
            request_text_frame.pack(fill=tk.BOTH, expand=True)
            
            request_scroll = ttk.Scrollbar(request_text_frame)
            request_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            request_text = tk.Text(
                request_text_frame,
                wrap=tk.WORD,
                yscrollcommand=request_scroll.set,
                bg=self.current_theme['input_bg'],
                fg=self.current_theme['fg'],
                font=('Courier', 9)
            )
            request_text.pack(fill=tk.BOTH, expand=True)
            request_scroll.config(command=request_text.yview)
            
            # Response frame
            response_frame = tk.Frame(paned_window, bg=self.current_theme['bg'])
            paned_window.add(response_frame)
            
            # Response header
            response_header = tk.Frame(response_frame, bg=self.current_theme['card_bg'], relief=tk.RAISED, bd=1)
            response_header.pack(fill=tk.X, pady=(0, 5))
            
            response_label = tk.Label(
                response_header,
                text="RESPONSE",
                fg=self.current_theme['danger'],
                bg=self.current_theme['card_bg'],
                font=('Arial', 11, 'bold')
            )
            response_label.pack(pady=5)
            
            # Response text area
            response_text_frame = tk.Frame(response_frame, bg=self.current_theme['bg'])
            response_text_frame.pack(fill=tk.BOTH, expand=True)
            
            response_scroll = ttk.Scrollbar(response_text_frame)
            response_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            response_text = tk.Text(
                response_text_frame,
                wrap=tk.WORD,
                yscrollcommand=response_scroll.set,
                bg=self.current_theme['input_bg'],
                fg=self.current_theme['fg'],
                font=('Courier', 9)
            )
            response_text.pack(fill=tk.BOTH, expand=True)
            response_scroll.config(command=response_text.yview)
            
            # Function to format and insert data
            def format_and_insert_data(text_widget, data, data_type):
                try:
                    if data and data not in ["Waiting data...", "No request"]:
                        import json
                        import ast
                        
                        # Handle different data formats
                        if data.startswith('{') or data.startswith('['):
                            # Try JSON first
                            try:
                                parsed_data = json.loads(data)
                                formatted_json = json.dumps(parsed_data, indent=2, ensure_ascii=False)
                            except json.JSONDecodeError:
                                # Try Python dict literal
                                try:
                                    parsed_data = ast.literal_eval(data)
                                    formatted_json = json.dumps(parsed_data, indent=2, ensure_ascii=False)
                                except:
                                    formatted_json = data
                        elif data.startswith('{\'') or data.startswith('['):
                            # Python dict format - use ast.literal_eval
                            try:
                                parsed_data = ast.literal_eval(data)
                                formatted_json = json.dumps(parsed_data, indent=2, ensure_ascii=False)
                            except:
                                formatted_json = data
                        else:
                            formatted_json = data
                    else:
                        formatted_json = f"No {data_type} data available"
                    
                    text_widget.insert(tk.END, formatted_json)
                    text_widget.config(state=tk.DISABLED)
                    
                except Exception as e:
                    text_widget.insert(tk.END, f"Error parsing {data_type}: {e}\n\nRaw data:\n{data}")
                    text_widget.config(state=tk.DISABLED)
            
            # Insert request and response data
            format_and_insert_data(request_text, request_data, "request")
            format_and_insert_data(response_text, response_data, "response")
            
            # Create button frame
            button_frame = tk.Frame(json_window, bg=self.current_theme['bg'])
            button_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
            
            # Copy request button
            def copy_request():
                try:
                    request_text.config(state=tk.NORMAL)
                    content = request_text.get(1.0, tk.END)
                    request_text.config(state=tk.DISABLED)
                    json_window.clipboard_clear()
                    json_window.clipboard_append(content)
                    messagebox.showinfo("Copied", "Request data copied to clipboard!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to copy request: {e}")
            
            copy_request_btn = tk.Button(
                button_frame,
                text="Copy Request",
                command=copy_request,
                bg=self.current_theme['success'],
                fg=self.current_theme['button_fg'],
                font=('Arial', 10, 'bold'),
                relief=tk.RAISED,
                bd=1
            )
            copy_request_btn.pack(side=tk.LEFT, padx=5)
            
            # Copy response button
            def copy_response():
                try:
                    response_text.config(state=tk.NORMAL)
                    content = response_text.get(1.0, tk.END)
                    response_text.config(state=tk.DISABLED)
                    json_window.clipboard_clear()
                    json_window.clipboard_append(content)
                    messagebox.showinfo("Copied", "Response data copied to clipboard!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to copy response: {e}")
            
            copy_response_btn = tk.Button(
                button_frame,
                text="Copy Response",
                command=copy_response,
                bg=self.current_theme['danger'],
                fg=self.current_theme['button_fg'],
                font=('Arial', 10, 'bold'),
                relief=tk.RAISED,
                bd=1
            )
            copy_response_btn.pack(side=tk.LEFT, padx=5)
            
            # Close button
            close_btn = tk.Button(
                button_frame,
                text="Close",
                command=json_window.destroy,
                bg=self.current_theme['button_bg'],
                fg=self.current_theme['button_fg'],
                font=('Arial', 10, 'bold'),
                relief=tk.RAISED,
                bd=1
            )
            close_btn.pack(side=tk.RIGHT, padx=5)
            
            # Set initial paned window position (50/50 split)
            paned_window.update()
            paned_window.sash_place(0, 500, 0)
            
            # Center window
            json_window.update_idletasks()
            x = (json_window.winfo_screenwidth() // 2) - (1000 // 2)
            y = (json_window.winfo_screenheight() // 2) - (700 // 2)
            json_window.geometry(f"1000x700+{x}+{y}")
            
        except Exception as e:
            self.logger.error(f"Error showing JSON details: {e}")
            messagebox.showerror("Error", f"Failed to show JSON details: {e}")
    
    def update_server_status(self, is_running: bool):
        """Update server status and theme"""
        self.server_running = is_running
        
        # Server status button was removed, so just update theme
        self._apply_theme_to_all()
    
    def show_about(self):
        """Show about dialog - exact replica of JavaScript about"""
        messagebox.showinfo(
            "About ProtoDecoderUI",
            "ProtoDecoderUI - Python Desktop Version\n\n"
            "Exact replica of JavaScript interface with:\n"
            "• Same layout and functionality\n"
            "• Same HTTP endpoints\n"
            "• Same data processing\n"
            "• Same user experience"
        )
    
    def start(self):
        """Start application - exact replica of JavaScript start"""
        self.root.mainloop()
    
    def close(self):
        """Close application - exact replica of JavaScript close"""
        try:
            if hasattr(self, 'root'):
                self.root.destroy()
        except:
            # Window already destroyed or doesn't exist, ignore
            pass
    
    def setup_theme(self):
        """Setup theme colors - Enhanced contrast and accessibility"""
        # Light theme colors - Enhanced contrast for better readability
        self.light_theme = {
            'bg': '#ffffff',  # Pure white background for maximum brightness
            'fg': '#000000',  # Pure black text for maximum contrast
            'card_bg': '#f8f9fa',  # Very light gray for cards
            'input_bg': '#ffffff',  # White inputs
            'border': '#ced4da',  # Clear borders
            'header_bg': '#f8f9fa',  # Light gray header
            'button_bg': '#0056b3',  # Darker blue for better contrast
            'button_fg': '#ffffff',  # White button text
            'table_bg': '#ffffff',  # White table background
            'table_alt_bg': '#f8f9fa',  # Light gray for alternating rows
            'table_header_bg': '#e9ecef',  # Light gray header
            'table_header_fg': '#000000',  # Black text for headers
            'accent': '#495057',  # Darker accent for visibility
            'success': '#198754',  # Green for success
            'warning': '#fd7e14',  # Orange for better visibility
            'danger': '#dc3545',  # Red for danger
            'hover': '#e9ecef'  # Light hover color
        }
        
        # Dark theme colors - Enhanced contrast for dark mode
        self.dark_theme = {
            'bg': '#000000',  # Pure black background for maximum contrast
            'fg': '#ffffff',  # Pure white text for maximum readability
            'card_bg': '#1a1a1a',  # Very dark gray for cards
            'input_bg': '#2d2d2d',  # Dark inputs
            'border': '#404040',  # Medium borders
            'header_bg': '#1a1a1a',  # Dark header
            'button_bg': '#0066cc',  # Bright blue for dark mode
            'button_fg': '#ffffff',  # White button text
            'table_bg': '#1a1a1a',  # Dark table background
            'table_alt_bg': '#2d2d2d',  # Slightly lighter for alternating rows
            'table_header_bg': '#606060',  # Much lighter header for visibility
            'table_header_fg': '#ffffff',  # White text for headers
            'accent': '#b3b3b3',  # Light gray for secondary elements
            'success': '#28a745',  # Bright green for success
            'warning': '#ffc107',  # Yellow for warnings
            'danger': '#ff4444',  # Bright red for danger
            'hover': '#333333'  # Dark hover color
        }
        
        self.current_theme = self.light_theme
    
    def toggle_dark_mode(self):
        """Toggle dark mode - Enhanced with auto_switch and transition_duration"""
        # Load theme settings from config
        try:
            config = self.config_manager.load_config() if hasattr(self, 'config_manager') else {}
            theme_settings = config.get('theme_settings', {})
            auto_switch = theme_settings.get('auto_switch', False)
            transition_duration = theme_settings.get('transition_duration', 300)
        except:
            auto_switch = False
            transition_duration = 300
        
        self.dark_mode = not self.dark_mode
        
        # Apply transition if duration > 0
        if transition_duration > 0:
            self.root.after(transition_duration // 2, self._apply_theme_transition)
        else:
            self._apply_theme_transition()
        
        # Auto-switch logic
        if auto_switch:
            # Could implement time-based auto-switching here
            # For now, just log that auto-switch is enabled
            if hasattr(self, 'logger'):
                self.logger.info("Auto-switch enabled - theme toggled")
    
    def _apply_theme_transition(self):
        """Apply the actual theme transition"""
        if self.dark_mode:
            self.current_theme = self.dark_theme
            self.darkmode_btn.config(text="☾")
            self.root.configure(bg=self.current_theme['bg'])
        else:
            self.current_theme = self.light_theme
            self.darkmode_btn.config(text="☀")
            self.root.configure(bg=self.current_theme['bg'])
        
        # Apply theme to all widgets
        self._apply_theme_to_all()
        
        # Force immediate table header update
        if hasattr(self, 'tree'):
            self._simple_header_fix()
    
    def _simple_header_fix(self):
        """Aggressive header fix for dark theme - force complete refresh"""
        try:
            style = ttk.Style()
            
            # Get current theme
            if self.dark_mode:
                header_bg = '#505050'
                header_fg = '#FFFFFF'
                table_bg = '#1a1a1a'
                table_fg = '#ffffff'
            else:
                header_bg = '#e9ecef'
                header_fg = '#000000'
                table_bg = '#ffffff'
                table_fg = '#000000'
            
            # Force complete style refresh
            style.theme_use('default')  # Reset to default
            
            # Apply new styles aggressively
            style.configure('Treeview',
                          background=table_bg,
                          foreground=table_fg,
                          fieldbackground=table_bg,
                          bordercolor=header_bg)
            
            style.configure('Treeview.Heading',
                          background=header_bg,
                          foreground=header_fg,
                          relief=tk.RAISED,
                          font=('Arial', 10, 'bold'))
            
            # Force mapping for hover states
            style.map('Treeview',
                     background=[('selected', '#0066cc')],
                     foreground=[('selected', '#ffffff')])
            
            style.map('Treeview.Heading',
                     background=[('active', '#404040' if self.dark_mode else '#d1d1d1')],
                     foreground=[('active', header_fg)])
            
            # Multiple force updates
            if hasattr(self, 'tree'):
                for _ in range(3):  # Multiple updates
                    self.tree.update()
                    self.tree.update_idletasks()
                    self.root.update_idletasks()
                
                # Force header recreation
                headers = {
                    '#0': 'Instance',
                    '#1': 'instance', 
                    '#2': 'Method',
                    '#3': 'Method Name',
                    '#4': 'Send',
                    '#5': 'Received',
                    '#6': 'Wait'
                }
                
                for col_id, text in headers.items():
                    try:
                        # Remove and recreate header
                        self.tree.heading(col_id, text='')
                        self.tree.update()
                        self.tree.heading(col_id, text=text)
                        self.tree.update()
                    except:
                        pass
                        
                # Apply alternating colors to existing rows
                existing_items = self.tree.get_children()
                for i, item in enumerate(existing_items):
                    # Excel style: line 0 white, line 1 gray, line 2 white, line 3 gray...
                    row_tag = 'odd' if i % 2 == 0 else 'even'  # 0=odd(white), 1=even(gray), 2=odd(white)...
                    try:
                        self.tree.item(item, tags=(row_tag,))
                    except:
                        pass
                            
                # Final update
                self.tree.update()
                self.tree.update_idletasks()
                        
        except Exception as e:
            # If everything fails, try basic approach
            try:
                style = ttk.Style()
                if self.dark_mode:
                    style.configure('Treeview.Heading', background='#505050', foreground='#FFFFFF')
                else:
                    style.configure('Treeview.Heading', background='#e9ecef', foreground='#000000')
                if hasattr(self, 'tree'):
                    self.tree.update()
            except:
                pass
    
    def _recreate_table_for_theme(self):
        """Completely recreate the table with proper theme styling"""
        try:
            # Store current data if exists
            if hasattr(self, 'tree'):
                # Get all current data
                current_data = []
                for child in self.tree.get_children():
                    current_data.append(self.tree.item(child)['values'])
            
            # Destroy old tree
            if hasattr(self, 'tree'):
                self.tree.destroy()
            
            # Recreate table container if needed
            if not hasattr(self, 'table_container') or self.table_container is None:
                self.table_container = tk.Frame(self.main_frame, bg=self.current_theme['bg'])
                self.table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            
            # Create new treeview with proper theme
            self.tree = ttk.Treeview(
                self.table_container,
                columns=('instance', 'method', 'method_name', 'sent_data', 'received_data', 'wait'),
                show='headings', height=20
            )
            
            # Apply theme styling immediately
            style = ttk.Style()
            if self.dark_mode:
                style.configure('Treeview',
                              background='#1a1a1a',
                              foreground='#ffffff',
                              fieldbackground='#1a1a1a')
                style.configure('Treeview.Heading',
                              background='#606060',
                              foreground='#ffffff',
                              relief=tk.RAISED,
                              font=('Arial', 10, 'bold'))
            else:
                style.configure('Treeview',
                              background='#ffffff',
                              foreground='#000000',
                              fieldbackground='#ffffff')
                style.configure('Treeview.Heading',
                              background='#e9ecef',
                              foreground='#000000',
                              relief=tk.RAISED,
                              font=('Arial', 10, 'bold'))
            
            # Configure alternating row colors (Excel-style)
            if self.dark_mode:
                # Dark theme alternating colors
                self.tree.tag_configure('odd', background='#1a1a1a', foreground='#ffffff')  # Dark rows
                self.tree.tag_configure('even', background='#2d2d2d', foreground='#ffffff')  # Lighter rows
            else:
                # Light theme alternating colors
                self.tree.tag_configure('odd', background='#ffffff', foreground='#000000')  # White rows
                self.tree.tag_configure('even', background='#e8e8e8', foreground='#000000')  # Darker gray rows
            
            # Refresh alternating colors for existing rows
            self._refresh_alternating_colors()
            
            # Configure headers
            self.tree.heading('#0', text='Instance')
            self.tree.heading('#1', text='instance')
            self.tree.heading('#2', text='Method')
            self.tree.heading('#3', text='Method Name')
            self.tree.heading('#4', text='Send')
            self.tree.heading('#5', text='Received')
            self.tree.heading('#6', text='Wait')
            
            # Configure columns
            self.tree.column('#0', width=120, minwidth=80)
            self.tree.column('#1', width=80, minwidth=60)
            self.tree.column('#2', width=150, minwidth=100)
            self.tree.column('#3', width=200, minwidth=150)
            self.tree.column('#4', width=200, minwidth=150)
            self.tree.column('#5', width=100, minwidth=80)
            self.tree.column('#6', width=80, minwidth=60)
            
            # Pack treeview
            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Restore scrollbars if they existed
            if hasattr(self, 'tree_scroll_y'):
                self.tree_scroll_y = ttk.Scrollbar(self.table_container, orient=tk.VERTICAL, command=self.tree.yview)
                self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
                self.tree.configure(yscrollcommand=self.tree_scroll_y.set)
            
            # Restore data
            for row_data in current_data:
                self.tree.insert('', tk.END, values=row_data)
            
            # Force update
            self.tree.update()
            self.tree.update_idletasks()
            
        except Exception as e:
            pass  # If recreation fails, at least we tried
    
    def _force_header_update(self):
        """Force complete recreation of table headers with aggressive styling"""
        if not hasattr(self, 'tree'):
            return
            
        try:
            # Get current theme colors
            if self.dark_mode:
                header_bg = '#606060'
                header_fg = '#ffffff'
                table_bg = '#1a1a1a'
                table_fg = '#ffffff'
            else:
                header_bg = '#e9ecef'
                header_fg = '#000000'
                table_bg = '#ffffff'
                table_fg = '#000000'
            
            # Create completely new style to override ttk defaults
            style = ttk.Style()
            
            # Use theme name to force new style
            theme_name = 'Custom.Treeview' if not self.dark_mode else 'CustomDark.Treeview'
            
            # Configure completely new Treeview style
            style.configure(theme_name,
                          background=table_bg,
                          foreground=table_fg,
                          fieldbackground=table_bg,
                          bordercolor=header_bg)
            
            # Configure completely new Heading style
            heading_theme = theme_name + '.Heading'
            style.configure(heading_theme,
                          background=header_bg,
                          foreground=header_fg,
                          relief=tk.RAISED,
                          font=('Arial', 10, 'bold', 'underline'))  # Add underline for visibility
            
            # Apply the new style to the treeview
            self.tree.configure(style=theme_name)
            
            # Force multiple updates
            for _ in range(5):  # More aggressive updates
                self.tree.update()
                self.tree.update_idletasks()
                self.root.update_idletasks()
                
            # Recreate all headers with forced styling
            headers_mapping = {
                '#0': 'Instance',
                '#1': 'instance', 
                '#2': 'Method',
                '#3': 'Method Name',
                '#4': 'Send',
                '#5': 'Received',
                '#6': 'Wait'
            }
            
            for col_id, header_text in headers_mapping.items():
                try:
                    self.tree.heading(col_id, text=header_text)
                    # Force each header update
                    self.tree.heading(col_id)
                except:
                    pass
                    
            # Final forced update
            self.tree.update()
            self.tree.update_idletasks()
            self.root.update()
                    
        except Exception as e:
            # If everything fails, try basic approach
            try:
                style = ttk.Style()
                if self.dark_mode:
                    style.configure('Treeview.Heading', background='#606060', foreground='#ffffff')
                else:
                    style.configure('Treeview.Heading', background='#e9ecef', foreground='#000000')
                self.tree.update()
            except:
                pass
    
    def _apply_theme_to_all(self):
        """Apply theme to all widgets - Optimized for better readability"""
        theme = self.current_theme
        
        # Update main frame
        self.main_frame.configure(bg=theme['bg'])
        
        # Update header
        self._update_frame_colors(self.main_frame, theme)
        
        # Update treeview style for table
        style = ttk.Style()
        
        # Configure Treeview for both themes
        style.configure('Treeview', 
                      background=theme['table_bg'],
                      foreground=theme['fg'],
                      fieldbackground=theme['table_bg'],
                      bordercolor=theme['border'])
        
        # Configure Treeview.Heading for both themes
        style.configure('Treeview.Heading',
                      background=theme['table_header_bg'],
                      foreground=theme['table_header_fg'],
                      bordercolor=theme['border'],
                      relief=tk.RAISED,
                      font=('Arial', 10, 'bold'))  # Bold font for headers
        
        # Configure mapping for both themes
        style.map('Treeview',
                 background=[('selected', theme['button_bg'])],
                 foreground=[('selected', theme['button_fg'])])
        style.map('Treeview.Heading',
                 background=[('active', theme['hover'])],
                 foreground=[('active', theme['table_header_fg'])])
        
        # Configure alternating row colors (Excel-style)
        if self.dark_mode:
            # Dark theme alternating colors
            self.tree.tag_configure('odd', background='#1a1a1a', foreground='#ffffff')  # Dark rows
            self.tree.tag_configure('even', background='#2d2d2d', foreground='#ffffff')  # Lighter rows
        else:
            # Light theme alternating colors  
            self.tree.tag_configure('odd', background='#ffffff', foreground='#000000')  # White rows
            self.tree.tag_configure('even', background='#e8e8e8', foreground='#000000')  # Darker gray rows
        
        # Refresh alternating colors for existing rows
        self._refresh_alternating_colors()
        
        # Force update the treeview if it exists
        if hasattr(self, 'tree'):
            # Force theme application with specific theme colors
            if self.dark_mode:
                # Dark theme specific styling
                style.configure('Treeview.Heading',
                              background='#606060',  # Force darker header
                              foreground='#ffffff',   # Force white text
                              bordercolor='#404040',
                              relief=tk.RAISED,
                              font=('Arial', 10, 'bold'))
            else:
                # Light theme specific styling  
                style.configure('Treeview.Heading',
                              background='#e9ecef',  # Force light header
                              foreground='#000000',   # Force black text
                              bordercolor='#ced4da',
                              relief=tk.RAISED,
                              font=('Arial', 10, 'bold'))
            
            self.tree.update()
            self.tree.update_idletasks()
            
            # Force redraw of headers with correct column names
            try:
                self.tree.heading('#0', text='ID')
                self.tree.heading('#1', text='Instance')
                self.tree.heading('#2', text='Method')
                self.tree.heading('#3', text='Method Name')
                self.tree.heading('#4', text='Sent Data')
                self.tree.heading('#5', text='Received Data')
                self.tree.heading('#6', text='Wait')
            except:
                pass  # Ignore if columns don't exist
    
    def _update_frame_colors(self, frame, theme):
        """Recursively update frame colors with enhanced contrast"""
        try:
            frame.configure(bg=theme['bg'])
            for child in frame.winfo_children():
                if isinstance(child, tk.Frame):
                    self._update_frame_colors(child, theme)
                elif isinstance(child, tk.Label):
                    child.configure(bg=theme['bg'], fg=theme['fg'])
                elif isinstance(child, tk.Button):
                    # Enhanced button theming with better contrast
                    button_text = child.cget('text') if hasattr(child, 'cget') else ''
                    if '☀' in button_text or '☾' in button_text:
                        # Theme toggle button
                        child.configure(bg=theme['header_bg'], fg=theme['accent'], relief=tk.FLAT)
                    elif '▶' in button_text:
                        # Play button
                        child.configure(bg=theme['success'], fg=theme['button_fg'], relief=tk.FLAT)
                    elif '⏸' in button_text:
                        # Pause button
                        child.configure(bg=theme['warning'], fg='#000000', relief=tk.FLAT)
                    elif '🗑' in button_text:
                        # Clear button
                        child.configure(bg=theme['danger'], fg=theme['button_fg'], relief=tk.FLAT)
                    elif '🔴' in button_text or '🟢' in button_text:
                        # Server status button
                        status_color = theme['success'] if self.server_running else theme['danger']
                        child.configure(bg=theme['header_bg'], fg=status_color, relief=tk.FLAT)
                    else:
                        # Default button styling
                        child.configure(bg=theme['button_bg'], fg=theme['button_fg'], relief=tk.RAISED)
                elif isinstance(child, tk.Entry):
                    child.configure(
                        bg=theme['input_bg'], 
                        fg=theme['fg'],
                        insertbackground=theme['fg'],
                        selectbackground=theme['button_bg'],
                        selectforeground=theme['button_fg'],
                        borderwidth=1,
                        relief=tk.SOLID,
                        bd=1
                    )
                elif isinstance(child, ttk.Combobox):
                    # Enhanced combobox styling
                    style = ttk.Style()
                    if self.dark_mode:
                        style.configure('TCombobox',
                                      fieldbackground=theme['input_bg'],
                                      background=theme['button_bg'],
                                      foreground=theme['fg'],
                                      bordercolor=theme['border'],
                                      selectbackground=theme['button_bg'],
                                      selectforeground=theme['button_fg'])
                    else:
                        style.configure('TCombobox',
                                      fieldbackground=theme['input_bg'],
                                      background=theme['button_bg'],
                                      foreground=theme['fg'],
                                      bordercolor=theme['border'],
                                      selectbackground=theme['button_bg'],
                                      selectforeground=theme['button_fg'])
                    child.configure(
                        fieldbackground=theme['input_bg'],
                        borderwidth=1,
                        relief=tk.FLAT
                    )
        except Exception as e:
            pass  # Ignore errors for widgets that don't support these options

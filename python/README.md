# ProtoDecoderUI Python Desktop Application

## This project need fixed and completed, it is currently a work in progress.

Complete migration of JavaScript ProtoDecoderWebUI to Python 3.10+ desktop application using Tkinter for GUI, maintaining 100% functional equivalence of `/traffic`, `/golbat`, and `/PolygonX/PostProtos` endpoints while eliminating all web-based dependencies.

## Features

- **Protocol Buffer Processing**: Process protobuf data using existing `protos/*` Python folder
- **HTTP Endpoints**: Maintain identical functionality for `/traffic`, `/golbat`, and `/PolygonX/PostProtos` endpoints
- **Desktop GUI**: Native Tkinter interface without web browser dependencies
- **Alternating Row Colors**: Excel-style alternating row colors in data table (white/gray in light theme, dark/lighter-dark in dark theme)
- **Configuration Management**: Desktop-based configuration with file persistence
- **Theme Management**: Dark/light theme switching with persistence
- **Geographic Processing**: Coordinate processing for location data (distance, area calculation)
- **Error Recovery**: Graceful error handling with exponential backoff
- **Performance Monitoring**: Real-time performance tracking against targets
- **Code Documentation**: All comments and documentation translated to English for consistency

## Requirements

- Python 3.10+
- Tkinter (included with Python)
- Existing `protos/*` Python folder
- psutil (for performance monitoring)

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install psutil
   ```
3. Ensure Python 3.10+ is installed
4. Verify Tkinter is available: `python -m tkinter`
5. Run the application: `python python/main.py`

## Configuration

Configuration is managed through:
- Desktop GUI interface (recommended)
- Configuration files in `config/` directory
- Default config: `config/config.json`
- Example config: `config/example.config.json`

### Configuration Options

- **Server Settings**: Port, traffic light identifier, protos path
- **GUI Settings**: Window size, resizable, center on screen
- **Theme Settings**: Dark/light themes, auto-switching, transition duration
- **Logging Settings**: Log level, log file location
- **Sample Saving**: Optional data sampling with path and format

## Usage

1. **Start Application**: Run `python python/main.py`
2. **GUI Interface**: Use the desktop interface for configuration and monitoring
3. **Server Control**: Start/stop HTTP server from GUI or menu
4. **Theme Switching**: Use theme switcher in Configuration section
5. **HTTP Endpoints**: Send protocol buffer data to:
   - `/traffic` - Traffic data processing
   - `/golbat` - Golbat data processing  
   - `/PolygonX/PostProtos` - Polygon processing with geographic coordinates

## GUI Features

### Data Table
- **Alternating Row Colors**: Excel-style row coloring for better readability
  - Light theme: White rows (#ffffff) and gray rows (#e8e8e8)
  - Dark theme: Dark rows (#1a1a1a) and lighter rows (#2d2d2d)
- **Auto-Refresh**: Colors automatically refresh when data is added, deleted, or when themes change
- **Double-Click**: View detailed JSON data in popup window

### Theme Management
- **Light Theme**: Clean, bright interface with high contrast
- **Dark Theme**: Easy on the eyes for low-light environments
- **Instant Switching**: Change themes without application restart
- **Persistent Settings**: Theme preference saved across sessions

### Data Filtering
- **Instance Filtering**: Filter by specific instances
- **Method Filtering**: Blacklist or whitelist specific method IDs
- **Real-time Updates**: Filters apply immediately to new and existing data

## API Endpoints

### /traffic (POST)
Process traffic protocol buffer data
```js
interface CombinedMessage {
    rpcid?: number
    rpcstatus?: number
    rpchandle?: number
    protos: [
        {
            method: number
            request: string
            response: string
        }
    ]
}
```

### /golbat (POST)
Process golbat protocol buffer data
```js
interface CombinedMessage {
    username: string 
    trainerlvl?: number
    contents : [
        {
            type: number
            request: string
            payload: string
            have_ar?: boolean
        }
    ]
}
```

### /PolygonX/PostProtos (POST)
Process polygon protocol buffer data with geographic calculations

```js
interface CombinedMessage {
    protos: [
        {
            method: number
            proto: bytes
            request: bytes
            trainer_id: string
            trainer_level: number
            has_geotargeted_ar_scan_quest: boolean
        }
    ]
    push_gateway_protos: [
        {
            method: number
            proto: bytes
            trainer_id: string
            trainer_level: number
            has_geotargeted_ar_scan_quest: boolean
        }
    ]
}
```

## Project Structure

```
python/
├── main.py              # Application entry point
├── config/              # Configuration management
│   ├── manager.py       # Configuration loading/saving
│   └── validator.py     # Configuration validation
├── gui/                 # Tkinter desktop interface
│   ├── main_window.py   # Main application window
│   ├── config_dialog.py # Configuration settings dialog
│   ├── theme_manager.py # Theme management
│   ├── theme_config.py  # Theme configuration
│   ├── theme_switcher.py # Theme switcher widget
│   └── error_dialogs.py # Error handling dialogs
├── server/              # HTTP endpoint handling
│   ├── http_handler.py  # HTTP server setup and routing
│   └── endpoints.py     # /traffic, /golbat, and /PolygonX/PostProtos endpoint logic
├── proto_processor/     # Protocol buffer processing
│   ├── decoder.py       # Protobuf decoding logic
│   ├── traffic_handler.py # Traffic-specific processing
│   ├── parser.py        # Payload parsing functions
│   └── polygon.py       # Geographic coordinate processing
├── utils/               # Shared utilities
│   ├── logger.py        # Logging configuration
│   ├── error_recovery.py # Error recovery with exponential backoff
│   ├── performance_monitor.py # Performance monitoring
│   └── integration_test.py # Integration testing
└── constants/           # Generated constants

config/                  # Configuration files
logs/                    # Application logs
scripts/                 # Utility scripts
protos/                  # Existing protobuf definitions
```

## Performance Targets

- **Response Time**: <100ms average
- **Memory Usage**: <50MB average
- **CPU Utilization**: <10% average

## Testing

## Theme Management

### Available Themes
- **Light Theme**: Clean, bright interface
- **Dark Theme**: Easy on the eyes for low-light environments

### Theme Features
- **Dynamic Switching**: Change themes without restart
- **Auto-Switching**: Optional automatic theme based on system preference
- **Persistence**: Theme preference saved across restarts
- **Custom Colors**: Support for custom color schemes

## Code Improvements

### Comment Translation
All code comments and documentation have been translated to English for consistency:
- **French Comments**: Translated Portuguese/French comments to English
- **Documentation**: Updated all docstrings and inline comments
- **Consistency**: Unified language across all Python files
- **Maintainability**: Improved code readability for international developers

### Alternating Row Colors Implementation
- **Dynamic Color Assignment**: Rows automatically get alternating colors based on position
- **Theme-Aware**: Colors adapt to light/dark theme changes
- **Persistent**: Colors maintained during table updates, deletions, and theme switches
- **Excel-Style**: Classic alternating pattern (row 0: white, row 1: gray, row 2: white, etc.)

### Performance Optimizations
- **Efficient Color Refresh**: Only refresh colors when necessary (after data changes)
- **Minimal Overhead**: Color assignment has negligible performance impact
- **Scalable**: Works efficiently with large datasets (1000+ rows)

## Migration Notes

This application maintains 100% functional equivalence with the JavaScript version:
- All HTTP endpoints preserve identical behavior
- Configuration files remain compatible
- Protocol buffer processing is unchanged
- Visual layout and themes are preserved
- Error handling follows the same patterns

## Development

This project uses only Python standard library modules plus psutil for system monitoring:
- No web framework dependencies
- Zero external dependencies except psutil
- Clean separation from JavaScript code
- Constants generation from JavaScript source

## Troubleshooting

### Common Issues

1. **Server Won't Start**
   - Check if port is available
   - Verify protos directory exists
   - Check configuration file validity

2. **Theme Not Applying**
   - Restart application after theme change
   - Check configuration file permissions
   - Verify theme configuration format

3. **Performance Issues**
   - Monitor performance metrics in GUI
   - Check system resource usage
   - Reduce concurrent requests if needed

### Logs

Application logs are stored in `logs/app.log` by default. Check logs for detailed error information.

## License

[Add your license information here]

#!/usr/bin/env python3
"""
Utils - EXACT replica of src/utils/index.ts
100% compliant with original JavaScript
"""

import base64
import json
import logging
import socket
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import parser functions - EXACT replica of JavaScript imports
from parser.proto_parser import decodePayloadTraffic

def b64Decode(data: str) -> bytes:
    """EXACT replica of JavaScript b64Decode"""
    if not data or data == "":
        return b""
    return base64.b64decode(data)

def moduleConfigIsAvailable() -> bool:
    """EXACT replica of JavaScript moduleConfigIsAvailable"""
    try:
        config_path = Path("config/config.json")
        return config_path.exists()
    except Exception:
        return False

def getIPAddress() -> str:
    """EXACT replica of JavaScript getIPAddress"""
    try:
        # Get local IP address - EXACT replica of JavaScript logic
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Try to get non-localhost IP
        interfaces = socket.getaddrinfo(hostname, None)
        for interface in interfaces:
            family, socktype, proto, canonname, sockaddr = interface
            if family == socket.AF_INET and sockaddr[0] != '127.0.0.1':
                return sockaddr[0]
        
        return local_ip if local_ip != '127.0.0.1' else '0.0.0.0'
    except Exception:
        return '0.0.0.0'

class WebStreamBuffer:
    """EXACT replica of JavaScript WebStreamBuffer"""
    
    def __init__(self):
        self.data = []
        self.callbacks = []
    
    def write(self, data: Any) -> None:
        """Write data to buffer"""
        print(f"WebStreamBuffer.write called: {data.get('methodName', 'Unknown')}")
        self.data.append(data)
        print(f"Buffer size after write: {len(self.data)}")
        self._notify_callbacks(data)
    
    def read(self) -> List[Any]:
        """Read all data from buffer"""
        print(f"WebStreamBuffer.read called: {len(self.data)} items available")
        data = self.data.copy()
        self.data.clear()
        print(f"WebStreamBuffer.read returning: {len(data)} items")
        return data
    
    def on_data(self, callback) -> None:
        """Register callback for new data"""
        self.callbacks.append(callback)
    
    def _notify_callbacks(self, data: Any) -> None:
        """Notify all callbacks of new data"""
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as e:
                logging.error(f"Error in callback: {e}")

def handleData(incoming: WebStreamBuffer, outgoing: WebStreamBuffer, identifier: Any, parsedData: str, sampleSaver: Optional[Any] = None) -> None:
    """EXACT replica of JavaScript handleData"""
    # Add logging - EXACT replica of JavaScript console.log
    logging.info(f"handleData called with identifier: {identifier}, parsedData: {parsedData}")
    
    # Validate required fields - EXACT replica of JavaScript validation
    if not isinstance(parsedData, dict) or 'protos' not in parsedData:
        logging.error("Invalid traffic data: 'protos' field missing or not a dict")
        return
    
    if not isinstance(parsedData['protos'], list):
        logging.error("Invalid traffic data: 'protos' field is not a list")
        return
    
    if len(parsedData['protos']) == 0:
        logging.error("Invalid traffic data: 'protos' array is empty")
        return
    
    logging.info(f"Processing {len(parsedData['protos'])} protos")
    
    # Process each proto - EXACT replica of JavaScript loop
    for i in range(len(parsedData['protos'])):
        proto_item = parsedData['protos'][i]
        raw_request = proto_item.get('request', "")
        raw_response = proto_item.get('response', "")
        method_id = proto_item.get('method', 0)
        
        logging.info(f"Processing proto {i}: method={method_id}, request_len={len(raw_request)}, response_len={len(raw_response)}")
        
        # Parse request and response - EXACT replica of JavaScript parsing
        parsed_request_data = decodePayloadTraffic(
            method_id,
            raw_request,
            "request"
        )
        parsed_response_data = decodePayloadTraffic(
            method_id,
            raw_response,
            "response"
        )
        
        logging.info(f"Request parsing result: {len(parsed_request_data)} items")
        logging.info(f"Response parsing result: {len(parsed_response_data)} items")
        
        # Save sample if enabled - EXACT replica of JavaScript sample saving
        if sampleSaver and len(parsed_request_data) > 0 and len(parsed_response_data) > 0:
            try:
                sampleSaver.save_pair(
                    parsed_request_data[0], 
                    parsed_response_data[0], 
                    raw_request, 
                    raw_response, 
                    "traffic"
                )
                logging.info("Sample saved successfully")
            except Exception as e:
                logging.error(f"Error saving sample: {e}")
        
        # Handle request data - EXACT replica of JavaScript request handling
        if isinstance(parsed_request_data, str):
            incoming.write({"error": parsed_request_data})
            logging.warning(f"Request parsing error: {parsed_request_data}")
        else:
            for parsed_object in parsed_request_data:
                parsed_object['identifier'] = identifier
                incoming.write(parsed_object)
                logging.info(f"Wrote request data to buffer: {parsed_object.get('methodName', 'Unknown')}")
        
        # Handle response data - EXACT replica of JavaScript response handling
        if isinstance(parsed_response_data, str):
            outgoing.write({"error": parsed_response_data})
            logging.warning(f"Response parsing error: {parsed_response_data}")
        else:
            for parsed_object in parsed_response_data:
                parsed_object['identifier'] = identifier
                outgoing.write(parsed_object)
                logging.info(f"Wrote response data to buffer: {parsed_object.get('methodName', 'Unknown')}")
    
    logging.info(f"handleData completed for identifier: {identifier}")

def redirect_post_golbat(redirect_url: str, redirect_token: str, redirect_data: Any) -> Optional[Dict[str, Any]]:
    """EXACT replica of JavaScript redirect_post_golbat"""
    try:
        # Parse URL - EXACT replica of JavaScript URL parsing
        from urllib.parse import urlparse
        
        parsed_url = urlparse(redirect_url)
        
        # Prepare headers - EXACT replica of JavaScript headers
        headers = {
            "Content-Type": "application/json"
        }
        
        if redirect_token:
            headers["Authorization"] = "Bearer " + redirect_token
        
        # Make request - EXACT replica of JavaScript HTTP request
        response = requests.post(
            redirect_url,
            json=redirect_data,
            headers=headers,
            timeout=30
        )
        
        return {
            "status_code": response.status_code,
            "response_text": response.text,
            "headers": dict(response.headers)
        }
        
    except Exception as e:
        logging.error(f"Error in redirect_post_golbat: {e}")
        return None

class SampleSaver:
    """EXACT replica of JavaScript SampleSaver"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', False)
        self.save_path = config.get('save_path', 'samples')
        self.max_samples = config.get('max_samples', 1000)
        self.samples = []
        
        # Create samples directory
        Path(self.save_path).mkdir(exist_ok=True)
    
    def save_pair(self, request_data: Dict[str, Any], response_data: Dict[str, Any], 
                  raw_request: str, raw_response: str, data_type: str) -> None:
        """Save request/response pair - EXACT replica of JavaScript savePair"""
        if not self.enabled:
            return
        
        try:
            sample = {
                'timestamp': self._get_timestamp(),
                'data_type': data_type,
                'request': {
                    'raw': raw_request,
                    'parsed': request_data
                },
                'response': {
                    'raw': raw_response,
                    'parsed': response_data
                }
            }
            
            self.samples.append(sample)
            
            # Limit samples
            if len(self.samples) > self.max_samples:
                self.samples.pop(0)
            
            # Save to file
            filename = f"{data_type}_{sample['timestamp']}.json"
            filepath = Path(self.save_path) / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(sample, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error saving sample: {e}")
    
    def _get_timestamp(self) -> str:
        """Get timestamp for sample - EXACT replica of JavaScript timestamp"""
        from datetime import datetime
        return datetime.now().isoformat().replace(':', '-')


# Export functions - EXACT replica of JavaScript exports
__all__ = [
    'b64Decode',
    'moduleConfigIsAvailable',
    'getIPAddress',
    'handleData',
    'redirect_post_golbat',
    'WebStreamBuffer',
    'SampleSaver'
]

#!/usr/bin/env python3
"""
Generate Python constants from JavaScript TypeScript file.

This script reads the JavaScript constants/index.ts file and generates
the complete Python equivalent with all REQUEST_MESSAGES_RESPONSES mappings.
"""

import re
import sys
from pathlib import Path

def generate_constants_from_js():
    """Generate Python constants from JavaScript TypeScript file."""
    
    # Read the JavaScript file
    js_file = Path("../src/constants/index.ts")
    if not js_file.exists():
        print(f"Error: {js_file} not found")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    # Extract all REQUEST_MESSAGES_RESPONSES entries
    pattern = r"(REQUEST_TYPE_\w+):\s*\[(\d+),\s*(POGOProtos\.Rpc\.[^,\n]+|null),\s*(POGOProtos\.Rpc\.[^,\n]+|null)\]"
    matches = re.findall(pattern, js_content)
    
    if not matches:
        print("No REQUEST_MESSAGES_RESPONSES found in JavaScript file")
        return False
    
    # Generate Python constants
    python_content = '''"""
Constants for ProtoDecoderPY

Python equivalent of JavaScript constants/index.ts with requestMessagesResponses mapping.
Complete mapping with all methods from JavaScript version.
"""

try:
    import protos.pogo_pb2 as pogo_pb2
except ImportError:
    raise ImportError("Failed to import pogo_pb2. Make sure protos folder contains Python protobuf definitions.")

# Request/Response method mapping equivalent to JavaScript requestMessagesResponses
# Complete mapping with all methods from JavaScript version
REQUEST_MESSAGES_RESPONSES = {
'''
    
    for method_name, method_id, request_proto, response_proto in matches:
        # Convert POGOProtos.Rpc.ClassName to getattr(pogo_pb2, 'ClassName', None)
        request_class = f"getattr(pogo_pb2, '{request_proto.split('.')[-1]}', None)" if request_proto != 'null' else 'None'
        response_class = f"getattr(pogo_pb2, '{response_proto.split('.')[-1]}', None)" if response_proto != 'null' else 'None'
        
        python_content += f"    '{method_name}': [{method_id}, {request_class}, {response_class}],\n"
    
    python_content += '''}

def get_method_by_id(method_id: int):
    """
    Get method tuple by method ID.
    
    Args:
        method_id: Method identifier
        
    Returns:
        Tuple of [method_id, request_class, response_class] or None
    """
    for method_name, method_tuple in REQUEST_MESSAGES_RESPONSES.items():
        if method_tuple[0] == method_id:
            return method_tuple
    return None

def get_all_method_ids():
    """
    Get all available method IDs.
    
    Returns:
        List of method IDs
    """
    return [tuple[0] for tuple in REQUEST_MESSAGES_RESPONSES.values() if tuple[0] > 0]

def get_method_name_by_id(method_id: int):
    """
    Get method name by method ID.
    
    Args:
        method_id: Method identifier
        
    Returns:
        Method name string or None
    """
    for method_name, method_tuple in REQUEST_MESSAGES_RESPONSES.items():
        if method_tuple[0] == method_id:
            return method_name
    return None

def get_method_count():
    """
    Get total number of methods.
    
    Returns:
        Total number of methods
    """
    return len(REQUEST_MESSAGES_RESPONSES)

# Statistics
TOTAL_METHODS = get_method_count()
METHOD_IDS = get_all_method_ids()

print(f"Loaded {TOTAL_METHODS} request/response method mappings")
print(f"Method IDs range: {min(METHOD_IDS)} to {max(METHOD_IDS)}")
'''
    
    # Write Python constants file
    py_file = Path("../constants/__init__.py")
    py_file.parent.mkdir(exist_ok=True)
    
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(python_content)
    
    print(f"Generated {len(matches)} method mappings in {py_file}")
    return True

if __name__ == "__main__":
    success = generate_constants_from_js()
    sys.exit(0 if success else 1)

"""
Protobuf definitions for Pokémon GO API communication.

This module imports all protobuf classes from the compiled pogo_pb2 module,
providing access to Pokémon GO protocol buffer definitions for use in
the Personal Bot Framework Python client.

The protobuf definitions include:
- Player data structures
- Inventory management
- Map objects and locations
- Gym and raid information
- Request/response protocols

Credits:
 - --=FurtiF™=-- for POGOProtos:
    - https://github.com/sponsors/Furtif
"""

from .pogo_pb2 import *

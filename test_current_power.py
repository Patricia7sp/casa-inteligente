#!/usr/bin/env python3
"""
Testar get_current_power()
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tapo import ApiClient
from src.utils.config import settings

async def main():
    client = ApiClient(settings.tapo_username, settings.tapo_password)
    device = await client.p110("192.168.68.108")
    
    power = await device.get_current_power()
    
    print("⚡ CURRENT POWER:")
    print(f"   Tipo: {type(power)}")
    print()
    for attr in dir(power):
        if not attr.startswith('_'):
            try:
                value = getattr(power, attr)
                if not callable(value):
                    print(f"   {attr}: {value}")
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())

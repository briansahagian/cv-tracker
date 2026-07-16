import os, sys
os.add_dll_directory(os.path.dirname(os.path.abspath(__file__)))
from pyorbbecsdk import Context

ctx = Context()
devs = ctx.query_devices()
n = devs.get_count()
print("device_count:", n)
for i in range(n):
    d = devs.get_device_by_index(i)
    info = d.get_device_info()
    print(f"  [{i}] name={info.get_name()} pid=0x{info.get_pid():04x} "
          f"vid=0x{info.get_vid():04x} sn={info.get_serial_number()} "
          f"fw={info.get_firmware_version()}")
print("OK")

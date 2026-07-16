import os
from openni import openni2

REDIST = r"C:\Users\brian\Documents\Revolute_Robotics\ESC_thermal_testing\orbbec_feed\openni2\sdk\libs"

openni2.initialize(REDIST)
print("OpenNI2 version:", openni2.get_version())

dev = openni2.Device.open_any()
info = dev.get_device_info()
print("Opened device:")
print("  name   :", info.name.decode() if isinstance(info.name, bytes) else info.name)
print("  vendor :", info.vendor.decode() if isinstance(info.vendor, bytes) else info.vendor)
print("  uri    :", info.uri.decode() if isinstance(info.uri, bytes) else info.uri)
print("  usbVID :", hex(info.usbVendorId), "usbPID:", hex(info.usbProductId))

# what sensors / video modes are available?
for stype, label in [(openni2.SENSOR_DEPTH, "DEPTH"),
                     (openni2.SENSOR_COLOR, "COLOR"),
                     (openni2.SENSOR_IR, "IR")]:
    sinfo = dev.get_sensor_info(stype)
    if sinfo is None:
        print(f"  {label}: not present")
        continue
    modes = sinfo.videoModes
    print(f"  {label}: {len(modes)} modes; sample: "
          + ", ".join(f"{m.resolutionX}x{m.resolutionY}@{m.fps}" for m in list(modes)[:4]))

dev.close()
openni2.unload()
print("OK")

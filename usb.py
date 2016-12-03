import os
import tkinter as tk
from tkinter import ttk
import threading
from time import sleep


class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.table = ttk.Treeview()
        self.table["columns"] = ("#1", "#2", "#3", "#4", "#5")
        self.table.heading("#0", text="Номер устройства")
        self.table.heading("#1", text="Адрес устройства")
        self.table.heading("#2", text="Точка монтирования")
        self.table.heading("#3", text="Свободно")
        self.table.heading("#4", text="Занято")
        self.table.heading("#5", text="Всего")
        self.devices = []

        self.table.pack(expand=tk.TRUE, fill=tk.BOTH)
        self.unmount = tk.Button(self, text="Размонтировать", command=self.umount)
        self.unmount.pack(side=tk.BOTTOM, expand=tk.TRUE, fill=tk.X)

        self.update_thread = threading.Thread(target=self.update)
        self.update_thread.daemon = True
        self.update_thread.start()

        self.mainloop()

    def umount(self):
        index = int(self.table.selection()[0][1:]) - 1
        if self.devices[index][1] != "НЕ БЛОЧНОЕ УСТРОЙСТВО":
            for current in self.devices[index][2]:
                os.system("umount {}".format(current))
            print(self.devices[index][2])

    def update(self):
        while True:
            devices = self.get_devices()
            for connected in devices:
                if connected not in self.devices:
                    print("{} has been connected.".format(connected[0]))
                    self.table.insert("", tk.END, text=connected[0], values=tuple(connected[1:]))

            for disconnected in self.devices:
                if disconnected not in devices:
                    print("{} has been disconnected.".format(disconnected[0]))
                    self.table.delete(disconnected[0])
            self.devices = devices
            sleep(1)

    def get_devices(self):
        devices = []
        mount_point = {string.split()[0]: string.split()[1].replace("\\040", " ") for string in
                       open('/proc/mounts')}

        for device in os.listdir("/sys/bus/usb/devices/"):
            if "usb" in device:
                device_number = open("/sys/bus/usb/devices/" + device + "/dev", "r").read()
                device_path = "НЕ БЛОЧНОЕ УСТРОЙСТВО"
                mount_points = []
                free = 0
                total = 0
                for dirpath, dirnames, filenames in os.walk("/sys/bus/usb/devices/" + device):
                    if 'block' in dirnames:
                        for block_device in os.listdir(dirpath + "/block"):
                            if "sd" in block_device:
                                device_path = "/dev/" + block_device
                                for partition in os.listdir("/sys/block/{}/".format(block_device)):
                                    if block_device in partition:
                                        mount_points.append(mount_point.get("/dev/" + partition, ""))
                                        try:
                                            stat = os.statvfs(mount_point['/dev/{}'.format(partition)])
                                            free += stat.f_bfree * stat.f_bsize
                                            total += stat.f_blocks * stat.f_bsize
                                        except KeyError:
                                            pass

                devices.append((device_number, device_path, mount_points, free, total - free, total))
        return devices


if __name__ == "__main__":
    MainWindow()
"""
devices = []
block_devises = []
for device in os.listdir("/sys/bus/usb/devices/"):
    if "usb" in device:
        devices.append("/sys/bus/usb/devices/" + device)
        for dirpath, dirnames, filenames in os.walk("/sys/bus/usb/devices/" + device):
            if 'block' in dirnames:
                block_devises.append(dirpath + '/block')
print(block_devises)
"""
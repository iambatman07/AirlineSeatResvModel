from qrtools import QR
import subprocess
f= open("qrcode.txt", "r")
data=f.readline()
my_QR=QR(data)
my_QR.encode()
subprocess.call(['xdg-open' , my_QR.filename])
my_QR2 = QR(filename = "home/user/Desktop/qr.png")
my_QR2.decode()
print my_QR2.data
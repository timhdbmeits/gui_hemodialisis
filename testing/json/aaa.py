from PyQt5.QtCore import QTime

current_time = QTime.currentTime()
print(current_time)
now = current_time.addSecs(3600)
print(now)

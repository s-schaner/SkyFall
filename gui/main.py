import json
import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_data.json')
MAP_HTML = os.path.join(os.path.dirname(__file__), 'map.html')


def load_data(path=DATA_FILE):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []


def discover_hardware():
    wifi = []
    gps = []
    for root, dirs, files in os.walk('/sys/class/net'):
        for d in dirs:
            if d.startswith('wlan') or d.startswith('wifi'):
                wifi.append(d)
    if os.path.exists('/dev'):
        for f in os.listdir('/dev'):
            if 'gps' in f.lower() or f.startswith('ttyUSB'):
                gps.append(f)
    return {'wifi': wifi, 'gps': gps}


n_dark = QtGui.QColor('#2b2b2b')

class MapView(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.load(QtCore.QUrl.fromLocalFile(MAP_HTML))

    def add_marker(self, lat, lon, info):
        js = f"addMarker({lat}, {lon}, '{info}')"
        self.page().runJavaScript(js)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SkyFall GUI')
        self.resize(1200, 800)
        self.setStyleSheet('background-color: #121212; color: #fff;')

        self.sidebar = QtWidgets.QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet('background-color: #1e1e1e;')
        side_layout = QtWidgets.QVBoxLayout(self.sidebar)
        side_layout.addWidget(QtWidgets.QLabel('Filters / Stats'))
        self.hw_label = QtWidgets.QLabel('Hardware:')
        side_layout.addWidget(self.hw_label)
        side_layout.addStretch(1)

        self.map_view = MapView()

        self.bottom = QtWidgets.QFrame()
        self.bottom.setFixedHeight(150)
        self.bottom.setStyleSheet('background-color: #1e1e1e;')
        bottom_layout = QtWidgets.QVBoxLayout(self.bottom)
        self.target_info = QtWidgets.QLabel('Target info')
        bottom_layout.addWidget(self.target_info)

        central = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.sidebar)

        map_container = QtWidgets.QVBoxLayout()
        map_container.addWidget(self.map_view)
        map_container.addWidget(self.bottom)
        main_layout.addLayout(map_container)
        self.setCentralWidget(central)

        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)
        self.update_status()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(5000)

        self.load_markers()

    def update_status(self):
        hw = discover_hardware()
        self.hw_label.setText(f"Hardware: wifi={len(hw['wifi'])} gps={len(hw['gps'])}")
        self.status.showMessage('Mesh Active | Nodes Online: 2 | Packets/sec: 0 | Time: ' +
                                QtCore.QDateTime.currentDateTime().toString())

    def load_markers(self):
        data = load_data()
        for node in data:
            gps = node['gps']
            info = f"Node {node['node_id']}"
            self.map_view.add_marker(gps['lat'], gps['lon'], info)
            for t in node.get('targets', []):
                info = f"Target {t['mac']} RSSI {t['rssi']}"
                self.map_view.add_marker(gps['lat'] + 0.0005, gps['lon'] + 0.0005, info)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

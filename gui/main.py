import os
import sys
import subprocess
from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
from database import init_db, get_nodes_with_targets

# Ensure the project root is on the module search path so wifi.py can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from wifi import scan_networks, start_monitor_mode, stop_monitor_mode
from hardware import discover_hardware

MAP_HTML = os.path.join(os.path.dirname(__file__), 'map.html')




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
        hw_btn = QtWidgets.QPushButton('Select Hardware')
        hw_btn.clicked.connect(self.choose_hardware)
        side_layout.addWidget(hw_btn)
        wifi_ctrl_btn = QtWidgets.QPushButton('WiFi Control')
        wifi_ctrl_btn.clicked.connect(self.open_wifi_dialog)
        side_layout.addWidget(wifi_ctrl_btn)
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

        self.selected_wifi = None
        self.selected_gps = None
        self.update_status()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(5000)

        self.load_markers()

    def open_wifi_dialog(self):
        hw = discover_hardware()
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle('WiFi Control')
        layout = QtWidgets.QVBoxLayout(dlg)

        iface_combo = QtWidgets.QComboBox()
        iface_combo.addItems(hw['wifi'])
        if self.selected_wifi in hw['wifi']:
            iface_combo.setCurrentText(self.selected_wifi)
        layout.addWidget(QtWidgets.QLabel('Interface'))
        layout.addWidget(iface_combo)

        scan_btn = QtWidgets.QPushButton('Scan Networks')
        layout.addWidget(scan_btn)

        table = QtWidgets.QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(['SSID', 'Channel', 'Encryption'])
        layout.addWidget(table)

        def do_scan():
            table.setRowCount(0)
            nets = scan_networks(iface_combo.currentText())
            for net in nets:
                row = table.rowCount()
                table.insertRow(row)
                table.setItem(row, 0, QtWidgets.QTableWidgetItem(net['ssid']))
                table.setItem(row, 1, QtWidgets.QTableWidgetItem(net['channel']))
                table.setItem(row, 2, QtWidgets.QTableWidgetItem(net['encryption']))

        def select_row(row, _column):
            ssid_edit.setText(table.item(row, 0).text())
            channel_edit.setText(table.item(row, 1).text())
            enc_edit.setText(table.item(row, 2).text())

        table.cellClicked.connect(select_row)

        scan_btn.clicked.connect(do_scan)

        channel_edit = QtWidgets.QLineEdit()
        ssid_edit = QtWidgets.QLineEdit()
        enc_edit = QtWidgets.QLineEdit()
        form = QtWidgets.QFormLayout()
        form.addRow('Channel', channel_edit)
        form.addRow('SSID', ssid_edit)
        form.addRow('Encryption', enc_edit)
        layout.addLayout(form)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                             QtWidgets.QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)

        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.selected_wifi = iface_combo.currentText() or None
            # Start monitor mode on selected channel
            if self.selected_wifi:
                start_monitor_mode(self.selected_wifi, channel_edit.text())

    def choose_hardware(self):
        hw = discover_hardware()
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle('Select Hardware')
        layout = QtWidgets.QFormLayout(dlg)

        wifi_combo = QtWidgets.QComboBox()
        wifi_combo.addItems(hw['wifi'])
        if self.selected_wifi in hw['wifi']:
            wifi_combo.setCurrentText(self.selected_wifi)
        layout.addRow('WiFi:', wifi_combo)

        gps_combo = QtWidgets.QComboBox()
        gps_combo.addItems(hw['gps'])
        if self.selected_gps in hw['gps']:
            gps_combo.setCurrentText(self.selected_gps)
        layout.addRow('GPS:', gps_combo)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                             QtWidgets.QDialogButtonBox.Cancel)
        layout.addRow(buttons)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)

        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.selected_wifi = wifi_combo.currentText() or None
            self.selected_gps = gps_combo.currentText() or None
            self.update_status()

    def update_status(self):
        hw = discover_hardware()
        wifi_text = self.selected_wifi or (hw['wifi'][0] if hw['wifi'] else 'none')
        gps_text = self.selected_gps or (hw['gps'][0] if hw['gps'] else 'none')
        self.hw_label.setText(f"WiFi: {wifi_text}  GPS: {gps_text}")
        self.status.showMessage('Mesh Active | Nodes Online: 2 | Packets/sec: 0 | Time: ' +
                                QtCore.QDateTime.currentDateTime().toString())

    def load_markers(self):
        data = get_nodes_with_targets()
        for node in data:
            gps = node['gps']
            info = f"Node {node['node_id']}"
            self.map_view.add_marker(gps['lat'], gps['lon'], info)
            for t in node.get('targets', []):
                info = f"Target {t['mac']} RSSI {t['rssi']}"
                self.map_view.add_marker(gps['lat'] + 0.0005, gps['lon'] + 0.0005, info)


def main():
    init_db()
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

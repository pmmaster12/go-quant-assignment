from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QGroupBox, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QDoubleValidator

class SignalEmitter(QObject):
    parameters_changed = pyqtSignal(dict)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trade Simulator")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1f29;
            }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QHBoxLayout(main_widget)
        layout.setSpacing(35)
        layout.setContentsMargins(50, 50, 50, 50)

        left_panel = self._create_input_panel()
        layout.addWidget(left_panel)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #444;")
        layout.addWidget(separator)

        right_panel = self._create_output_panel()
        layout.addWidget(right_panel)

        layout.setStretch(0, 2)
        layout.setStretch(2, 3)

    def _create_input_panel(self) -> QGroupBox:
        panel = QGroupBox("⚙️ Input Parameters")
        panel.setStyleSheet("""
            QGroupBox {
                font-size: 19px;
                font-weight: bold;
                color: #f8f8f2;
                border: 2px solid #8be9fd;
                border-radius: 10px;
                background-color: #282a36;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 8px 0 8px;
            }
            QLabel {
                color: #f8f8f2;
                font-size: 15px;
            }
            QLineEdit, QComboBox {
                background-color: #44475a;
                color: #f8f8f2;
                border: 1px solid #6272a4;
                border-radius: 5px;
                padding: 5px 8px;
                font-size: 15px;
            }
            QLineEdit:invalid {
                border: 1px solid #ff5555;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        def create_input_row(label_text, widget):
            row = QHBoxLayout()
            row.addWidget(QLabel(label_text))
            row.addWidget(widget)
            return row

        self.exchange_combo = QComboBox()
        self.exchange_combo.addItem("OKX")

        self.asset_combo = QComboBox()
        self.asset_combo.addItem("BTC-USDT-SWAP")

        self.quantity_input = QLineEdit()
        self.quantity_input.setText("100")
        self.quantity_input.setValidator(QDoubleValidator(0.0, 1000000.0, 2))

        self.volatility_input = QLineEdit()
        self.volatility_input.setText("0.02")
        self.volatility_input.setValidator(QDoubleValidator(0.0, 1.0, 4))

        self.fee_combo = QComboBox()
        self.fee_combo.addItems(["Tier 1", "Tier 2", "Tier 3"])

        layout.addLayout(create_input_row("Exchange:", self.exchange_combo))
        layout.addLayout(create_input_row("Asset:", self.asset_combo))
        layout.addLayout(create_input_row("Quantity (USD):", self.quantity_input))
        layout.addLayout(create_input_row("Volatility:", self.volatility_input))
        layout.addLayout(create_input_row("Fee Tier:", self.fee_combo))

        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        panel.setLayout(layout)
        return panel

    def _create_output_panel(self) -> QGroupBox:
        panel = QGroupBox("📊 Output Parameters")
        panel.setStyleSheet("""
            QGroupBox {
                font-size: 19px;
                font-weight: bold;
                color: #f8f8f2;
                border: 2px solid #50fa7b;
                border-radius: 10px;
                background-color: #282a36;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 8px 0 8px;
            }
            QLabel {
                color: #FFC0CB;
                font-size: 16px;
                padding: 6px;
                border-radius: 4px;
                background-color: #353947;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(30, 30, 30, 30)

        self.slippage_label = QLabel("Expected Slippage: --")
        self.fees_label = QLabel("Expected Fees: --")
        self.impact_label = QLabel("Market Impact: --")
        self.net_cost_label = QLabel("Net Cost: --")
        self.maker_taker_label = QLabel("Maker/Taker Ratio: --")
        self.latency_label = QLabel("Internal Latency: --")

        layout.addWidget(self.slippage_label)
        layout.addWidget(self.fees_label)
        layout.addWidget(self.impact_label)
        layout.addWidget(self.net_cost_label)
        layout.addWidget(self.maker_taker_label)
        layout.addWidget(self.latency_label)
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def update_outputs(self, data: dict):
        self.slippage_label.setText(f"Expected Slippage: {data.get('slippage', '--')}")
        self.fees_label.setText(f"Expected Fees: {data.get('fees', '--')}")
        self.impact_label.setText(f"Market Impact: {data.get('impact', '--')}")
        self.net_cost_label.setText(f"Net Cost: {data.get('net_cost', '--')}")
        self.maker_taker_label.setText(f"Maker/Taker Ratio: {data.get('maker_taker', '--')}")
        self.latency_label.setText(f"Internal Latency: {data.get('latency', '--')} ms")

import sys

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from converter import convert_text


class CoordinateConverterWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("WGS84 to Relative X/Y")
        self.resize(860, 620)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(
            "Origin: 3.8163243, 52.7022056\n"
            "P1 3.826240, 52.704478\n"
            "P2 3.818058, 52.695705"
        )

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        self.format_combo = QComboBox()
        self.format_combo.addItem("Decimal degrees", userData="decimal")
        self.format_combo.addItem("Degrees + decimal minutes", userData="dm")

        self.lon_positive_combo = QComboBox()
        self.lon_positive_combo.addItem("East positive", userData="E")
        self.lon_positive_combo.addItem("West positive", userData="W")

        self.lat_positive_combo = QComboBox()
        self.lat_positive_combo.addItem("North positive", userData="N")
        self.lat_positive_combo.addItem("South positive", userData="S")

        convert_button = QPushButton("Convert")
        convert_button.clicked.connect(self.convert)

        copy_button = QPushButton("Copy output")
        copy_button.clicked.connect(self.copy_output)

        controls = QGridLayout()
        controls.addWidget(QLabel("Coordinate format"), 0, 0)
        controls.addWidget(self.format_combo, 0, 1)
        controls.addWidget(QLabel("Longitude sign"), 1, 0)
        controls.addWidget(self.lon_positive_combo, 1, 1)
        controls.addWidget(QLabel("Latitude sign"), 2, 0)
        controls.addWidget(self.lat_positive_combo, 2, 1)

        button_row = QHBoxLayout()
        button_row.addWidget(convert_button)
        button_row.addWidget(copy_button)
        button_row.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(QLabel("Input (multi-line free format):"))
        layout.addWidget(self.input_text, 1)
        layout.addLayout(button_row)
        layout.addWidget(QLabel("Output (tab-separated, ready to copy):"))
        layout.addWidget(self.output_text, 1)

    def convert(self) -> None:
        try:
            text = convert_text(
                self.input_text.toPlainText(),
                self.format_combo.currentData(),
                self.lon_positive_combo.currentData(),
                self.lat_positive_combo.currentData(),
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Conversion error", str(exc))
            return

        self.output_text.setPlainText(text)

    def copy_output(self) -> None:
        QApplication.clipboard().setText(self.output_text.toPlainText())


def main() -> int:
    app = QApplication(sys.argv)
    widget = CoordinateConverterWidget()
    widget.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

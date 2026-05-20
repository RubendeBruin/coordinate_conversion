import sys

from PySide6.QtGui import QColor, QPainter, QPen
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

from converter import convert_rows


class PointsPlotWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._points: list[tuple[str, float, float]] = []
        self.setMinimumHeight(260)

    def set_points(self, points: list[tuple[str, float, float]]) -> None:
        self._points = points
        self.update()

    def _draw_cross(self, painter: QPainter, x: float, y: float, color: QColor, size: int = 5) -> None:
        painter.setPen(QPen(color, 2))
        painter.drawLine(int(x - size), int(y - size), int(x + size), int(y + size))
        painter.drawLine(int(x - size), int(y + size), int(x + size), int(y - size))

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("white"))

        draw_rect = self.rect().adjusted(16, 16, -16, -16)
        if draw_rect.width() <= 0 or draw_rect.height() <= 0:
            return

        all_points = [("Origin", 0.0, 0.0), *self._points]
        max_abs_x = max(abs(x) for _, x, _ in all_points)
        max_abs_y = max(abs(y) for _, _, y in all_points)

        sx = draw_rect.width() / (2.0 * max_abs_x) if max_abs_x > 0 else float("inf")
        sy = draw_rect.height() / (2.0 * max_abs_y) if max_abs_y > 0 else float("inf")
        scale = min(sx, sy)
        if scale == float("inf"):
            scale = 1.0

        center_x = draw_rect.left() + draw_rect.width() / 2.0
        center_y = draw_rect.top() + draw_rect.height() / 2.0

        painter.setPen(QPen(QColor("#c0c0c0"), 1))
        painter.drawRect(draw_rect)
        painter.drawLine(draw_rect.left(), int(center_y), draw_rect.right(), int(center_y))
        painter.drawLine(int(center_x), draw_rect.top(), int(center_x), draw_rect.bottom())

        def to_pixels(x: float, y: float) -> tuple[float, float]:
            return center_x + x * scale, center_y - y * scale

        origin_x, origin_y = to_pixels(0.0, 0.0)
        self._draw_cross(painter, origin_x, origin_y, QColor("#d32f2f"), size=6)
        painter.setPen(QPen(QColor("#d32f2f"), 1))
        painter.drawText(int(origin_x) + 8, int(origin_y) - 8, "Origin")

        for name, x, y in self._points:
            px, py = to_pixels(x, y)
            self._draw_cross(painter, px, py, QColor("#1976d2"))
            painter.setPen(QPen(QColor("#1a1a1a"), 1))
            painter.drawText(int(px) + 8, int(py) - 8, name)


class CoordinateConverterWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("WGS84 to Relative X/Y")
        self.resize(860, 700)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(
            "Origin: 3.8163243, 52.7022056\n"
            "P1 3.826240, 52.704478\n"
            "P2 3.818058, 52.695705"
        )

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.plot_widget = PointsPlotWidget()

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
        layout.addWidget(QLabel("Figure (to scale, origin marked):"))
        layout.addWidget(self.plot_widget, 1)

    def convert(self) -> None:
        try:
            results = convert_rows(
                self.input_text.toPlainText(),
                self.format_combo.currentData(),
                self.lon_positive_combo.currentData(),
                self.lat_positive_combo.currentData(),
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Conversion error", str(exc))
            return

        lines = ["Name\tX\tY"]
        for name, x, y in results:
            lines.append(f"{name}\t{x:.3f}\t{y:.3f}")
        text = "\n".join(lines)
        self.output_text.setPlainText(text)
        self.plot_widget.set_points(results)

    def copy_output(self) -> None:
        QApplication.clipboard().setText(self.output_text.toPlainText())


def main() -> int:
    app = QApplication(sys.argv)
    widget = CoordinateConverterWidget()
    widget.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

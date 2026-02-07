import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt6.uic import loadUi


class CoffeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Загружаем интерфейс из .ui файла
        loadUi('main.ui', self)

        self.load_data()

    def load_data(self):
        try:
            conn = sqlite3.connect('coffee.sqlite')
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, sort_name, roast_degree, 
                       ground_or_beans, taste_description, price, package_volume_ml
                FROM coffee
                ORDER BY id
            """)
            rows = cursor.fetchall()

            self.tableWidget.setRowCount(len(rows))
            self.tableWidget.setColumnCount(7)
            self.tableWidget.setHorizontalHeaderLabels([
                "ID", "Название сорта", "Степень обжарки",
                "Молотый/в зернах", "Описание вкуса", "Цена (руб)", "Объем упаковки (мл)"
            ])

            for row_idx, row_data in enumerate(rows):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    self.tableWidget.setItem(row_idx, col_idx, item)

            conn.close()

        except sqlite3.Error as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось загрузить данные:\n{e}")
        except FileNotFoundError:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Ошибка", "Файл базы данных 'coffee.sqlite' не найден.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = CoffeeApp()
    ex.show()
    sys.exit(app.exec())

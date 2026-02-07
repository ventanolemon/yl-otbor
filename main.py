import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem, QDialog, QMessageBox
)
from PyQt6.uic import loadUi


class AddEditCoffeeDialog(QDialog):
    def __init__(self, mode="add", coffee_data=None):
        super().__init__()
        loadUi('addEditCoffeeForm.ui', self)
        self.mode = mode  # "add" или "edit"
        self.coffee_id = None

        self.saveButton.clicked.connect(self.save)
        self.cancelButton.clicked.connect(self.reject)

        if mode == "edit" and coffee_data:
            self.coffee_id = coffee_data[0]
            self.sortNameEdit.setText(coffee_data[1])
            self.roastDegreeEdit.setText(coffee_data[2])
            self.groundOrBeansEdit.setText(coffee_data[3])
            self.tasteDescriptionEdit.setPlainText(coffee_data[4] or "")
            self.priceSpinBox.setValue(float(coffee_data[5]))
            self.volumeSpinBox.setValue(int(coffee_data[6]))

    def save(self):
        sort_name = self.sortNameEdit.text().strip()
        roast_degree = self.roastDegreeEdit.text().strip()
        ground_or_beans = self.groundOrBeansEdit.text().strip()
        taste_desc = self.tasteDescriptionEdit.toPlainText().strip()
        price = self.priceSpinBox.value()
        volume = self.volumeSpinBox.value()

        if not sort_name or not roast_degree or not ground_or_beans:
            QMessageBox.warning(self, "Ошибка ввода", "Поля 'Название сорта', 'Степень обжарки' и 'Молотый/в зернах' обязательны.")
            return

        self.accept()
        self.result_data = (
            self.coffee_id,
            sort_name, roast_degree, ground_or_beans,
            taste_desc, price, volume
        )


class CoffeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('main.ui', self)
        self.addButton.clicked.connect(self.add_coffee)
        self.editButton.clicked.connect(self.edit_coffee)
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
            conn.close()

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

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные:\n{e}")

    def add_coffee(self):
        dialog = AddEditCoffeeDialog(mode="add")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            _, sort_name, roast_degree, ground_or_beans, taste_desc, price, volume = dialog.result_data
            try:
                conn = sqlite3.connect('coffee.sqlite')
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO coffee (
                        sort_name, roast_degree, ground_or_beans,
                        taste_description, price, package_volume_ml
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (sort_name, roast_degree, ground_or_beans, taste_desc, price, volume))
                conn.commit()
                conn.close()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить запись:\n{e}")

    def edit_coffee(self):
        selected = self.tableWidget.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Выбор", "Выберите строку для редактирования.")
            return

        row = selected[0].row()
        coffee_data = []
        for col in range(7):
            item = self.tableWidget.item(row, col)
            coffee_data.append(item.text() if item else "")

        dialog = AddEditCoffeeDialog(mode="edit", coffee_data=coffee_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            coffee_id, sort_name, roast_degree, ground_or_beans, taste_desc, price, volume = dialog.result_data
            try:
                conn = sqlite3.connect('coffee.sqlite')
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE coffee SET
                        sort_name = ?, roast_degree = ?, ground_or_beans = ?,
                        taste_description = ?, price = ?, package_volume_ml = ?
                    WHERE id = ?
                """, (sort_name, roast_degree, ground_or_beans, taste_desc, price, volume, coffee_id))
                conn.commit()
                conn.close()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить запись:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())
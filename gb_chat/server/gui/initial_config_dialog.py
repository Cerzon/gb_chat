from pathlib import Path
from typing import Any, List, Optional

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QWidget


class InitialConfigDialog(QDialog):
    def __init__(
        self,
        listen_addresses: List[str],
        default_db_path: Path,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent=parent)

        ui_file = Path(__file__).parent / "initial_config_dialog.ui"
        self._ui: Any = uic.loadUi(ui_file, self)  # type: ignore

        self._ui.addressComboBox.addItems(listen_addresses)
        self._ui.dbPathLineEdit.setText(str(default_db_path))

        self._ui.dbMemoryCheckBox.toggled.connect(self._on_memory_check_toggled)
        self._ui.dbBrowseButton.clicked.connect(self._show_db_file_browse_dialog)
        self._ui.dbPathLineEdit.textChanged.connect(self._on_path_to_db_file_changed)

    def get_listen_address(self) -> str:
        return self._ui.addressComboBox.currentText()  # type:ignore

    def get_listen_port(self) -> int:
        return self._ui.portSpinBox.value()  # type:ignore

    def get_db_path(self) -> Optional[Path]:
        if self._ui.dbMemoryCheckBox.isChecked():
            return None

        return Path(self._ui.dbPathLineEdit.text())

    def _show_db_file_browse_dialog(self) -> None:
        db_path = self.get_db_path()
        if db_path is not None:
            dlg_dir = Path(db_path).parent
        else:
            dlg_dir = Path(".").absolute()

        selected_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Choose DB"),
            str(dlg_dir),
            self.tr("Database (*.db *.sqlite *.sqlite3)"),
        )
        self._ui.dbPathLineEdit.setText(selected_path)

    def _on_path_to_db_file_changed(self, value: str) -> None:
        path = Path(value).absolute()
        if path.exists():
            self._set_ok_btn_enabled(True)
        elif path.parent.is_dir():
            self._set_ok_btn_enabled(True)
        else:
            self._set_ok_btn_enabled(False)

    def _on_memory_check_toggled(self, checked: bool) -> None:
        if not checked:
            self._on_path_to_db_file_changed(self._ui.dbPathLineEdit.text())
        else:
            self._set_ok_btn_enabled(True)

    def _set_ok_btn_enabled(self, enabled: bool) -> None:
        ok_button = self._ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(enabled)

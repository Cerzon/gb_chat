from pathlib import Path

import pytest
from gb_chat.server.gui.initial_config_dialog import InitialConfigDialog
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


def test_init_args_default_values_in_ui(qapp):
    addresses = ["127.0.0.1", "0.0.0.0"]
    path = Path(__file__)
    sut = InitialConfigDialog(addresses, path)

    for idx, value in enumerate(addresses):
        assert sut._ui.addressComboBox.itemText(idx) == value

    assert sut._ui.dbPathLineEdit.text() == str(path)

    assert sut._ui.dbMemoryCheckBox.isChecked()
    assert not sut._ui.dbPathLineEdit.isEnabled()
    assert not sut._ui.dbBrowseButton.isEnabled()

    assert sut._ui.portSpinBox.value() == 7777
    assert sut._ui.addressComboBox.currentText() == addresses[0]

    assert sut.get_listen_address() == addresses[0]
    assert sut.get_listen_port() == 7777
    assert sut.get_db_path() is None


@pytest.fixture
def sut(qapp):
    return InitialConfigDialog(["0.0.0.0"], Path(__file__))


def test_disable_inmemory(sut):
    QTest.mouseClick(sut._ui.dbMemoryCheckBox, Qt.LeftButton)

    assert sut._ui.dbPathLineEdit.isEnabled()
    assert sut._ui.dbBrowseButton.isEnabled()

    assert sut.get_db_path() == Path(__file__)

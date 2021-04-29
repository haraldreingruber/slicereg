from abc import abstractmethod, ABC
from typing import Optional

from PySide2.QtWidgets import QWidget

from slicereg.commands.utils import Signal
from slicereg.gui.commands import CommandProvider
from slicereg.gui.model import AppModel


class BaseQtWidget(ABC):

    @property
    @abstractmethod
    def qt_widget(self) -> QWidget: ...


class BaseViewModel(ABC):

    def __init__(self, _model: AppModel, _commands: CommandProvider):
        self._model = _model
        self._model.updated.connect(self.update)
        self._commands = _commands
        self.updated = Signal()

    def update(self):
        self.updated.emit()


class BaseView(ABC):

    def __init__(self):
        self.model: Optional[BaseViewModel] = None
        self.updated = Signal()

    def update(self) -> None:
        self.updated.emit(model=self)

    def register(self, model: BaseViewModel) -> None:
        self.model = model
        self.model.updated.connect(self.update)

from spyke import application
from spyke.graphics import window


class EditorApplication(application.Application):
    def __init__(self) -> None:
        super().__init__(window.WindowSpec(1080, 720, 'Spyke Editor'))

if __name__ == '__main__':
    app = EditorApplication()
    app.run()

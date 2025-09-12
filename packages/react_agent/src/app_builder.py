class AppBuilder:
    """
    app を構築するファクトリ
    """

    def __init__(self):
        self.initialized = False

    def initialize(self):
        if self.initialized:
            raise RuntimeError("App was already initialized.")
        self.initialized = True

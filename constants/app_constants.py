from dataclasses import dataclass

@dataclass
class AppConstants:
    WINDOW_TITLE: str = "Conversor de Mídia + Download"
    WINDOW_SIZE: str = "800x550"
    GITHUB_URL: str = "https://github.com/joao-menezes"
    ICON_PATH: str = "./images/icons8-github-48.png"
    ICON_SIZE: tuple = (30, 30)
    SIDEBAR_WIDTH: int = 150
    PROGRESS_BAR_WIDTH: int = 400
    HISTORY_DISPLAY_LIMIT: int = 4
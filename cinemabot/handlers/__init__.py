from cinemabot.handlers.find import router as find_router
from cinemabot.handlers.help import router as help_router
from cinemabot.handlers.history import router as history_router
from cinemabot.handlers.start import router as start_router
from cinemabot.handlers.stats import router as stats_router


__all__ = [
    "help_router",
    "start_router",
    "stats_router",
    "find_router",
    "history_router",
]

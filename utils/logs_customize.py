from loguru import logger


def logs_customize():
    try:
        logger.remove(0)
        logger.add(
            sink='logs_loguru/loguru_{time:YYYY-MM-DD}.log',
            rotation='00:00',
            format="<g>{time:YYYY-MM-DD HH:mm:ss.SS!UTC}</g> <r>|</r> <y>{level}</y> <r>|</r> <w>{message}</w>",
            colorize=False
        )
    except Exception:
        pass

# logs_customize()

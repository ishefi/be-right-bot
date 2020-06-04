import logging
import sys

FORMAT = ("%(process)d.%(threadName)s %(filename)s:%(lineno)s "
          "%(asctime)s %(message)s")


def setup_logger():
    """ Setup the logger """
    the_logger = logging.getLogger("botserver")
    the_logger.setLevel(logging.DEBUG)

    logging.basicConfig(format=FORMAT, stream=sys.stderr)
    logging.captureWarnings(True)
    return the_logger


logger = setup_logger()

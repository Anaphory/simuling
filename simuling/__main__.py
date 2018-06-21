
from .cli import (argparser, prepare, run_and_write)


if __name__ == "__main__":
    # This should not be necessary, but py.test tries to import this and fails.
    parser = argparser()
    parameters = prepare(parser)
    for id, data in run_and_write(parameters):
        pass

import argparse
import json
import logging
import os
import sys
import threading
import time
from typing import Any, Callable

# On POSIX systems, input() prompts may be redirected to stderr instead of
# stdout due to an underlying C implementation from like 1993. Importing readline
# explicitly should resolve this, but a reliable readline doesn't exist on Windows,
# so we had to exclude it.
#
# See this Python discussion for more details:
# https://discuss.python.org/t/builtin-function-input-writes-its-prompt-to-sys-stderr-and-not-to-sys-stdout/12955
if sys.platform != "win32":
    import readline  # noqa: F401

import zmq

from cyrxnopt.apps._utilities import arg_validation as validate
from cyrxnopt.apps._utilities import common_args as parsers
from cyrxnopt.NestedVenv import NestedVenv
from cyrxnopt.OptimizerController import check_install
from cyrxnopt.utilities.train_server import train_server
from cyrxnopt.utilities.zmq import zmq_helpers
from cyrxnopt.utilities.zmq.zmq_obj_function import zmq_obj_function

logger = logging.getLogger(__name__)


def main(args: argparse.Namespace) -> int:
    optimizer = validate.optimizer(args.optimizer)
    location = validate.location(args.location)
    config_path = validate.config_path(args.config, location)

    logging.basicConfig(level=args.log_level)

    # Prepare virtual environment
    venv_path = os.path.join(location, f"venv_{optimizer}")
    venv = NestedVenv(venv_path)

    if not os.path.exists(venv_path) and not check_install(optimizer, venv):
        print(
            (
                "No optimizer install found at the given location. Run "
                "'install_optimizer --help' for more details on how to "
                "install an optimizer."
            )
        )
        return -1
    logger.info(f"Activating virtual environment at: {venv_path}")
    venv.activate()

    # Make sure the config file exists
    if not config_path.exists():
        print(f"Config file not found at {config_path}.")
        return -1

    with open(config_path, "r") as fin:
        logger.debug(f"Reading config to file: {config_path}")
        config_contents = json.load(fin)

    # address = config["ip_address"] + ":" + config["port"]
    address = "tcp://localhost:5555"
    socket = zmq_helpers.init_socket(address)

    # TODO: Update handling of directions when expanding to multi-objective
    obj_func = zmq_obj_function(
        socket,
        (
            config_contents["direction"][0]
            if isinstance(config_contents["direction"], list)
            else config_contents["direction"]
        ),
    )

    print("Beginning training...")
    # The training thread is never used here after being spun up
    _ = start_training_thread(
        optimizer,
        args.training_steps,
        location,
        config_contents,
        venv,
        obj_func,
    )
    user_input_thread = start_user_input_thread(args.training_steps)
    while user_input_thread.is_alive():
        time.sleep(1)

    print(
        (
            "Reminder: After training, you can start an optimization with "
            "'cyrxnopt predict'."
        )
    )

    return 0


def start_training_thread(*args: Any, **kwargs: Any) -> threading.Thread:
    # This thread is a daemon because the program should exit when no alive,
    # non-daemonic threads are left. Once the user input thread is done,
    # this thread should also exit and the program should terminate
    thread = threading.Thread(
        target=train_server,
        name="Training Thread",
        args=args,
        kwargs=kwargs,
        daemon=True,
    )
    thread.start()

    return thread


def start_user_input_thread(*args: Any, **kwargs: Any) -> threading.Thread:
    thread = threading.Thread(
        target=input_server,
        name="User Input Thread",
        args=args,
        kwargs=kwargs,
        daemon=False,
    )
    thread.start()

    return thread


def input_server(training_steps: int, endpoint: str = "tcp://*:5555") -> None:
    # Create the context and socket
    context = zmq.Context(1)
    socket = context.socket(zmq.REP)

    logger.debug(f"Binding to {endpoint}")
    socket.bind(endpoint)

    # Register the socket with a poller
    poll = zmq.Poller()
    poll.register(socket, zmq.POLLIN)

    steps = 1
    while steps <= training_steps:
        #  Wait for ready from the optimizer
        logger.debug("Waiting...")
        request = socket.recv()
        logger.debug(f"Received request: {request.decode(encoding='utf-8')}")

        reply = b"invalid_request"

        if type(json.loads(request)) == list:
            params = json.loads(request)

            # Empty param list, assume no training on this optimizer
            if len(params) == 0:
                print(
                    (
                        "Empty parameters received."
                        " Double-check that this optimizer needs training!"
                    )
                )
                reply = b"quit"
            else:
                print("Reaction to perform:", params)
                user_input = input(
                    f"Step {steps}: Enter reaction result ('q' to quit): "
                )

                if is_quit_request(user_input):
                    logger.info("Received quit input from user. Exitting...")
                    reply = b"quit"

                else:
                    reply = str(float(user_input)).encode("utf-8")

            steps += 1

        if reply == b"quit":
            socket.close()
            context.term()
            return

        logger.debug(f"Sending reply: {reply.decode(encoding='utf-8')}")
        socket.send(reply)

    print("Training complete!")


def is_quit_request(request: str) -> bool:
    """Checks if the request is one of the "quit" keywords.

    :param request: Request received through zmq socket.
    :type request: str
    :return: Whether the request is a quit request (True) or not (False).
    :rtype: bool
    """
    _request = request.lower()

    return _request in ["quit", "exit", "q"]


def get_parser(
    create_lambda: Callable[
        ..., argparse.ArgumentParser
    ] = argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    parser = create_lambda(
        parents=[
            parsers.optimizer(),
            parsers.config(),
            parsers.location(),
            parsers.logging(),
        ]
    )

    parser.add_argument(
        "-t",
        "--training-steps",
        dest="training_steps",
        default=20,
        type=int,
        help=(
            "Number of training steps to perform in each cycle if "
            "training is needed. Default: 20"
        ),
    )

    return parser


def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = get_parser()

    return parser.parse_args()


def run() -> int:
    return main(parse_args())


if __name__ == "__main__":
    sys.exit(run())

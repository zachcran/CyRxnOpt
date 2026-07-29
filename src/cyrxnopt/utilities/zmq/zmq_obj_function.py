import json
import logging
from typing import List, Union, cast

import zmq
from numpy.typing import NDArray

from cyrxnopt.utilities.zmq.AbortException import AbortException


class zmq_obj_function:
    """Objective function that forwards the parameters to evaluate to a remote
    ZeroMQ server and receives the evaluation result for the optimization.
    """

    def __init__(self, socket: zmq.Socket, direction: str = "min") -> None:
        """Initialize the class.

        :param socket: ZMQ socket to use for communication. Must already be
                       opened and ready to communicate.
        :type socket: zmq.Socket
        :param direction: Direction to optimize in, defaults to "min"
        :type direction: str, must be "min" or "max", optional
        """

        self.socket = socket
        self.direction = direction

    def __call__(self, x: List[float]) -> float:
        return self.request_evaluation(x)

    def request_evaluation(self, x: Union[List[float], NDArray]) -> float:
        """Objective function to send parameters to a remote socket and
        receive the result value.

        :param x: Parameters to evaluate.
        :type x: Union[List[float], NDArray]

        :raises AbortException: The optimization was aborted.

        :return: Result from the evaluated parameters.
        :rtype: float
        """

        logging.debug("Sending parameters: {}".format(x))

        if type(x) is not list:
            x = cast(NDArray, x)
            x = x.tolist()

        self.socket.send(json.dumps(x).encode("utf-8"))

        reply = self.socket.recv()
        logging.debug("Received reply: {}".format(reply))

        if reply == b"abort":
            raise AbortException()

        # Process reply
        function_value = float(reply)

        if self.direction == "max":
            function_value = -function_value

        return function_value

    @property
    def direction(self) -> str:
        """Getter for direction property.

        :return: Direction identifier.
        :rtype: str
        """

        return self.__direction

    @direction.setter
    def direction(self, value: str) -> None:
        """Setter for direction.

        Valid direction identifiers are "max" and "min".

        :param value: New value of direction.
        :type value: str

        :raises ValueError: Invalid direction keyword given.
        """

        terms = ["max", "min"]

        valid = [value.lower() == x for x in terms]

        if not any(valid):
            raise ValueError(
                "Invalid direction given. Valid directions are: {}".format(
                    ", ".join(terms)
                )
            )

        self.__direction = value

import asyncio

from asyncio import WindowsSelectorEventLoopPolicy

import zmq
from aioconsole import ainput
from zmq.asyncio import Context

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
context = Context()


async def main():
    socket = context.socket(zmq.REQ)
    with socket.connect("tcp://localhost:25000"):
        while True:
            input_string = await ainput("> ")
            print(f"Got {input_string}")
            input_string = input_string.strip()
            if not input_string:
                break
            print(f"Sending {input_string}")
            await socket.send_string(input_string)
            print(f"Waiting for response")
            result = await socket.recv_string()
            print(result)


if __name__ == "__main__":
    asyncio.run(main())

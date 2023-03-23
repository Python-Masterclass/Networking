import asyncio
import time

from asyncio import WindowsSelectorEventLoopPolicy

import zmq
from aioconsole import ainput
from zmq.asyncio import Context

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
context = Context()


async def work():
    socket = context.socket(zmq.REQ)
    socket.identity = b"long_requests"
    with socket.connect("tcp://localhost:25000"):
        while True:
            start = time.time()
            await socket.send_string("30")
            response = await socket.recv_string()
            end = time.time()
            print(f"{response} ({end - start} seconds)")


async def main():
    work_task = asyncio.create_task(work())
    await ainput()
    work_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())

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
    with socket.connect("tcp://localhost:25000"):
        while True:
            start = time.time()
            await socket.send_string("30")
            response = await socket.recv_string()
            end = time.time()
            print(f"{response} ({end - start} seconds)")


count = 0


async def monitor():
    global count
    while True:
        await asyncio.sleep(1)
        print(f"{count} request per second")
        count = 0


async def work():
    global count
    socket = context.socket(zmq.REQ)
    with socket.connect("tcp://localhost:25000"):
        while True:
            await socket.send_string("1")
            resp = await socket.recv_string()
            count += 1


async def main():
    tasks = [asyncio.create_task(work()), asyncio.create_task(monitor())]
    await ainput()
    for t in tasks:
        t.cancel()


if __name__ == "__main__":
    asyncio.run(main())

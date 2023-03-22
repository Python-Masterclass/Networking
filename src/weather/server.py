import asyncio
from asyncio import WindowsSelectorEventLoopPolicy
from random import randrange

from aioconsole import ainput

import zmq
from zmq.asyncio import Context

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
context = Context()


async def work(name, port):
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://*:{port}")
    print(f"{name} listening on port {port}")
    try:
        while True:
            zipcode = randrange(1000, 10000)
            temperature = randrange(-30, 40)
            humidity = randrange(10, 100)
            await socket.send_string(f"{zipcode} {temperature} {humidity}")
            await asyncio.sleep(0)
    except asyncio.CancelledError:
        print(f"{name} stopping")
        socket.setsockopt
        socket.close()


async def main(name, port):
    task = asyncio.create_task(work(name, port))
    await ainput()
    task.cancel()


if __name__ == "__main__":
    asyncio.run(main("weather update server", 5555))

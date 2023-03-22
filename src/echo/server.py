import asyncio
from asyncio import WindowsSelectorEventLoopPolicy
from aioconsole import ainput

import zmq
from zmq.asyncio import Context

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
context = Context()


async def work(name, port):
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{port}")
    print(f"{name} listening on port {port}")
    try:
        while True:
            message = await socket.recv_string()
            print(f"{name} received '{message}'")
            await socket.send_string(f"{name}: {message}")
            print(f"{name} sent '{name}: {message}'")
    except asyncio.CancelledError:
        print(f"{name} stopping")
        socket.close()


async def main1(name, port):
    task = asyncio.create_task(work(name, port))
    await ainput()
    task.cancel()


async def main2(name, port):
    tasks = [
        asyncio.create_task(work(f"{name}-{i}", port + i)) for i in range(3)
    ]
    await ainput()
    for t in tasks:
        t.cancel()


if __name__ == "__main__":
    asyncio.run(main2("echo", 5555))

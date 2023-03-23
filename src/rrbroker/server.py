import asyncio
import random
from asyncio import WindowsSelectorEventLoopPolicy

import zmq
from aioconsole import ainput
from zmq.asyncio import Context


asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
context = Context()


async def server(name):
    socket = context.socket(zmq.REP)
    socket.connect("tcp://localhost:5556")
    print(f"{name} connected")
    while True:
        message = await socket.recv_string()
        print(f"{name} received '{message}'")
        await asyncio.sleep(random.random())
        await socket.send_string(f"{name}: {message}")


async def main(nbr_servers):
    server_tasks = [asyncio.create_task(server(f"server-{i}")) for i in range(nbr_servers)]
    await ainput()
    for task in server_tasks:
        task.cancel()


if __name__=="__main__":
    asyncio.run(main(3))

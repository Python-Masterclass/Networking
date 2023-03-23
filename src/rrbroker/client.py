import asyncio
import random
from asyncio import WindowsSelectorEventLoopPolicy

import zmq
from aioconsole import ainput
from zmq.asyncio import Context


asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
context = Context()


async def client(name):
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    print(f"{name} connected")
    for i in range(10):
        await asyncio.sleep(random.random())
        print(f"{name} sending message {i}")
        await socket.send_string(f"{name} {i}")
        message = await socket.recv_string()
        print(f"{name} received '{message}'")


async def main(nbr_clients):
    client_tasks = [asyncio.create_task(client(f"client-{i}")) for i in range(nbr_clients)]
    await ainput()
    for task in client_tasks:
        task.cancel()



if __name__ == "__main__":
    asyncio.run(main(4))

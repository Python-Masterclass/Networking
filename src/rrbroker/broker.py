import asyncio
import random
from asyncio import WindowsSelectorEventLoopPolicy

import zmq
from aioconsole import ainput
from zmq.asyncio import Context, Poller


asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
context = Context()


async def broker():
    frontend_socket = context.socket(zmq.ROUTER)
    backend_socket = context.socket(zmq.DEALER)
    frontend_socket.bind("tcp://*:5555")
    backend_socket.bind("tcp://*:5556")
    print("broker ready")

    poller = Poller()
    poller.register(frontend_socket, zmq.POLLIN)
    poller.register(backend_socket, zmq.POLLIN)

    while True:
        sockets = dict(await poller.poll())
        if sockets.get(frontend_socket) == zmq.POLLIN:
            print("Received message from frontend")
            message = await frontend_socket.recv_multipart()
            await backend_socket.send_multipart(message)
        if sockets.get(backend_socket) == zmq.POLLIN:
            print("Received message from backend")
            message = await backend_socket.recv_multipart()
            await frontend_socket.send_multipart(message)


async def main():
    broker_task = asyncio.create_task(broker())
    await ainput()
    broker_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())

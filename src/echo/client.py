import asyncio
from asyncio import WindowsSelectorEventLoopPolicy


import zmq
from zmq.asyncio import Context

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
context = Context()


async def work(name, port, delay=0.2):
    print(f"{name}: connecting to server on port {port}")
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{port}")
    for i in range(10):
        print(f"{name}: sending request {i}")
        await socket.send_string(f"{name}, message {i}")
        reply = await socket.recv_string()
        print(f"{name}: received reply '{reply}'")
        await asyncio.sleep(delay)


async def main1(name, port):
    await work(name, port)


async def main2(name, port):
    tasks = [
        work(f"{name}-{i}", port, 0.2 + (i * 0.1)) for i in range(3)
    ]
    await asyncio.gather(*tasks)


async def work_multi(name, port, count):
    socket = context.socket(zmq.REQ)
    for i in range(count):
        print(f"{name}: connecting to server on port {port+i}")
        socket.connect(f"tcp://localhost:{port+i}")
    for i in range(10):
        print(f"{name}: sending request {i}")
        await socket.send_string(f"{name}, message {i}")
        reply = await socket.recv_string()
        print(f"{name}: received reply '{reply}'")
        await asyncio.sleep(0.2)


async def main3(name, port):
    await work_multi(name, port, 3)


if __name__ == "__main__":
    asyncio.run(main3("client", 5555))

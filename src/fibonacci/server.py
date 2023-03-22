import asyncio
from asyncio import WindowsSelectorEventLoopPolicy

import zmq
from aioconsole import ainput
from zmq.asyncio import Context, Poller

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
context = Context()


async def fib(n):
    if n <= 2:
        return 1
    return await fib(n - 1) + await fib(n - 2)


async def broker(server_addr, worker_addr):
    print(f"Starting broker, {server_addr=}, {worker_addr=}")
    client_socket = context.socket(zmq.ROUTER)
    print("Broker: created client socket")
    client_socket.bind(server_addr)
    print(f"Broker: client socket bound to {server_addr}")
    worker_socket = context.socket(zmq.ROUTER)
    print("Broker: created worker socket")
    worker_socket.bind(worker_addr)
    poller = Poller()
    free_workers = asyncio.Queue()
    worker_client_map = dict()
    poller.register(worker_socket, zmq.POLLIN)
    client_registered = False
    try:
        while True:
            sockets = dict(await poller.poll())
            if worker_socket in sockets:
                multipart_message = await worker_socket.recv_multipart()
                worker_id = multipart_message[0]
                print(f"Broker: received message from worker {worker_id}")
                client_id = worker_client_map.pop(worker_id, None)
                if client_id is None:
                    print(f"Broker: worker {worker_id} ready for work")
                else:
                    multipart_message[0] = client_id
                    print(f"Broker: forwarding message to client {client_id}")
                    await client_socket.send_multipart(multipart_message)
                await free_workers.put(worker_id)
                if not client_registered:
                    poller.register(client_socket, zmq.POLLIN)
                    client_registered = True
            if client_socket in sockets:
                multipart_message = await client_socket.recv_multipart()
                client_id = multipart_message[0]
                print(f"Broker: received message from client {client_id}")
                worker_id = await free_workers.get()
                if free_workers.empty():
                    poller.unregister(client_socket)
                    client_registered = False
                worker_client_map[worker_id] = client_id
                multipart_message[0] = worker_id
                print(f"Broker: forwarding message to worker {worker_id}")
                await worker_socket.send_multipart(multipart_message)
    except asyncio.CancelledError:
        print("Broker cancelled")
        worker_socket.close()
        client_socket.close()


async def worker(worker_addr, name):
    print(f"{name} starting")
    socket = context.socket(zmq.REQ)
    socket.identity = name.encode("utf-8")
    print(f"{name} connecting to {worker_addr}")
    try:
        with socket.connect(worker_addr):
            message = "ready"
            print(f"{name} ready")
            while True:
                await socket.send_string(message)
                job = await socket.recv_string()
                print(f"{name} received {job=}")
                n = int(job)
                result = await fib(n)
                message = f"{result}"
    except asyncio.CancelledError:
        print(f"{name} cancelled")
        socket.close()


async def main(server_addr):
    print(f"Starting fibonacci server on {server_addr}")
    worker_addr = "inproc://worker.ipc"
    print("Starting broker task")
    broker_task = asyncio.create_task(broker(server_addr, worker_addr))
    print("Starting worker tasks")
    worker_tasks = [asyncio.create_task(worker(worker_addr, f"worker-{i}")) for i in range(5)]
    await ainput()
    broker_task.cancel()
    for task in worker_tasks:
        task.cancel()


if __name__ == "__main__":
    asyncio.run(main("tcp://*:25000"))

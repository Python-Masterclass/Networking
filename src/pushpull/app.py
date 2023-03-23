import asyncio
import random
from asyncio import WindowsSelectorEventLoopPolicy
from datetime import datetime

import zmq
from aioconsole import ainput
from zmq.asyncio import Context


asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
context = Context()


async def source(source_addr):
    socket = context.socket(zmq.PUSH)
    socket.bind(source_addr)

    total_msec = 0
    for _ in range(100):
        workload = random.randint(1, 100)
        total_msec += workload
        await socket.send_string(f"{workload}")
    print(f"Total workload: {total_msec}")


async def sink(sink_addr):
    socket = context.socket(zmq.PULL)
    socket.bind(sink_addr)

    start_time = datetime.now()
    for task_nbr in range(100):
        _ = await socket.recv_string()
    print(f"Total time {(datetime.now() - start_time).microseconds / 1000} milliseconds")


async def worker(name, source_addr, sink_addr):
    source_socket = context.socket(zmq.PULL)
    source_socket.connect(source_addr)
    sink_socket = context.socket(zmq.PUSH)
    sink_socket.connect(sink_addr)

    job_count = 0
    try:
        while True:
            s = await source_socket.recv_string()
            job_count += 1
            await asyncio.sleep(int(s) * 0.001)
            await sink_socket.send_string("")
    except asyncio.CancelledError:
        print(f"{name} handled {job_count} jobs")


async def main(n_workers):
    source_addr = "inproc://source"
    sink_addr = "inproc://sink"

    sink_task = asyncio.create_task(sink(sink_addr))
    worker_tasks = [asyncio.create_task(worker(f"worker-{i}", source_addr, sink_addr)) for i in range(n_workers)]
    source_task = asyncio.create_task(source(source_addr))
    await ainput()
    source_task.cancel()
    for task in worker_tasks:
        task.cancel()
    sink_task.cancel()


if __name__ == "__main__":
    asyncio.run(main(10))

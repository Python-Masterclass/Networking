import asyncio

from asyncio import WindowsSelectorEventLoopPolicy

import zmq
from zmq.asyncio import Context

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
context = Context()


async def work(name, port, zipcode):
    print(f"{name}: connecting to server on port {port}")
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://localhost:{port}")

    # Filter zipcode
    socket.setsockopt_string(zmq.SUBSCRIBE, str(zipcode))
    temp_sum = 0
    humidity_sum = 0
    for update in range(10):
        received = await socket.recv_string()
        zipc, temp, hum = received.split()
        temp_sum += int(temp)
        humidity_sum += int(hum)
    print(f"Zipcode {zipcode}: average temperatur: {temp_sum / 10}, average humidity: {humidity_sum / 10}")


async def main(name, port):
    tasks = [
        work(f"{name} for {zipcode}", port, zipcode) for zipcode in (1220, 2400, 1000, 3400)
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main("weather update client", 5555))

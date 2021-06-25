import asyncio
from asyncio.base_events import Server
from typing import Set

writers = set()

events = []

async def handle_new_connection(reader, writer):
    task = asyncio.create_task(echo_response(reader,writer))
    events.append(task)
    

async def echo_response(reader, writer):
    while True:    
        response = await reader.read(100)
        responseData = response.decode()
        writer.write(response)
        await writer.drain()
        if responseData == "exit":
            break
    writer.close()
    

async def main():
    server = await asyncio.start_server(
        handle_new_connection, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
import asyncio
from asyncio.base_events import Server
import json
from message import Message
from node import Node

async def keepListeningToServer(node: Node):
    try:
        dataRead = await node.readFromNode(Message.MESSAGE_SIZE)
        message = json.loads(dataRead)
        messageText = message["message"]
        while messageText != Message.END_OF_BROADCAST:
            print(message["sender"],">>", messageText)
            dataRead = await node.readFromNode(Message.MESSAGE_SIZE)
            message = json.loads(dataRead)
            messageText = message["message"]
        node.closeConnection()
    except KeyboardInterrupt:
        messageDict = {"message": Message.QUIT_BROADCAST}
        await node.writeToNode(json.dumps(messageDict))
    except asyncio.CancelledError:
        print("Task cancelled")

    print("Quitting broadcast...")

async def main():
    identifier = input("Identifier >> ")
    role = Message.ROLE_LISTEN
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    node = Node(identifier, role, reader, writer)
    await node.writeToNode(node.toJson())
    response = await node.readFromNode(Message.MESSAGE_SIZE)
    response = json.loads(response)
    try:
        if response["response"] == Message.CONFIRM_ROLE :
            await keepListeningToServer(node)
        elif response["response"] == Message.DENY_ROLE :
            print("Server refused to grant access. Quitting...")
            node.closeConnection()
            exit(0)
    except:
        print("Error while reading server response. Quitting...")
        node.closeConnection()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Closing...")

"""
async def tcp_listen_client():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)

    writer.write(b'listen')
    await writer.drain()

    data = await reader.read(100)
    while data.decode() != "End Of Broadcast":
        print(f'Received: {data.decode()!r}')
        data = await reader.read(100)
    writer.close()

asyncio.run(tcp_listen_client())
"""
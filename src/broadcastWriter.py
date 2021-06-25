import asyncio
import json
from traceback import print_tb
from message import Message
from node import Node

async def keepListeningToServer(node: Node):
    try:
        print("Listening to server...")
        readData: bytes = await node.readFromNode(Message.MESSAGE_SIZE)
        if readData.__len__() == 0:
            print("Received zero length data from",)
            print("Broadcast ended. Quitting...")
            return
        data = json.loads(readData)
        message = data["message"]
        while message != Message.END_OF_BROADCAST:
            print(data)
            readData = await node.readFromNode(Message.MESSAGE_SIZE)
            if readData.__len__() == 0:
                print("Received zero length data from",)
                print("Broadcast ended. Quitting...")
                return
            data = json.loads(readData)
            message = data["message"]
        node.closeConnection()
        print("Broadcast ended. Quitting...")
    except ConnectionAbortedError:
        print("Server stopped responding")

async def keepWritingToServer(node: Node):
    try:
        message = input("Write message >> ")
        while message != Message.QUIT_BROADCAST and message != Message.END_OF_BROADCAST:
            messageDict = {"message": message, "sender": node.id}
            await node.writeToNode(json.dumps(messageDict))
            #ack = await node.readFromNode(Message.MESSAGE_SIZE)
            #print("Ack>",ack)
            #ackDict = json.loads(ack)
            #if ackDict["ack"] != Message.ACK:
            #    break
            message = input("Write message >> ")
        await node.writeToNode(json.dumps({"message": message}))
        node.closeConnection()
    except ConnectionAbortedError:
        print("The connection was aborted. Quitting...")
    except ConnectionResetError:
        print("The connection was reset. QUitting...")

async def main():
    identifier = input("Identifier >> ")
    role = Message.ROLE_WRITE
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    node = Node(identifier, role, reader, writer)
    await node.writeToNode(node.toJson())
    response = await node.readFromNode(Message.MESSAGE_SIZE)
    response = json.loads(response)
    #print(response)
    try:
        if response["response"] == Message.DENY_ROLE :
            print("Server refused to grant access. Quitting...")
            node.closeConnection()
            exit(0)
        #task_4 = asyncio.create_task(keepListeningToServer(node))
        task_5 = await asyncio.create_task(keepWritingToServer(node))
    except:
        raise
        print("Error while reading server response. Quitting...")
        node.closeConnection()
        exit(2)


if __name__ =="__main__":
    asyncio.run(main())


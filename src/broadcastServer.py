import asyncio
from asyncio.base_events import Server
from asyncio.tasks import create_task
from asyncio.windows_events import NULL
import json
from message import Message
from node import Node
import sys
import typing
import traceback

consumers: typing.List[Node] = []
producers: typing.List[Node] = []
listeningTasks = []
outputsQueue: asyncio.Queue = None

async def addNewConnection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    '''Add a producer or consumer when a new connection request is recevied.

    A node needs to write to the server a request containing a key `role` which can be set either to `listen` or `write`. If the role requested is
    valid then the node is added as a consumer or producer, respectively and a confirm message is sent back. Else the request is terminated and an
    error response is sent back to the client.
    '''
    message: bytes = await reader.read(Message.MESSAGE_SIZE)
    jsonEncoded: str = message.decode()
    dictEncoded: dict = json.loads(jsonEncoded)
    responseDict = {"response": None}
    try:
        node = Node(dictEncoded['id'],dictEncoded['role'],reader,writer)
        if node.role == Message.ROLE_LISTEN:
            consumers.append(node)
            print("Added listener",node)
            responseDict["response"] = Message.CONFIRM_ROLE
        elif node.role == Message.ROLE_WRITE:
            producers.append(node)
            print("Added writer",node)
            responseDict["response"] = Message.CONFIRM_ROLE
        else:
            raise KeyError
        task_1 = asyncio.create_task(keepListeningForMessageFromNode(node, outputsQueue))
        listeningTasks.append(task_1)
        await node.writeToNode(json.dumps(responseDict))
    except KeyError:
        responseDict["response"] = Message.KEY_ERROR
        writer.write(json.dumps(responseDict))
        writer.close()

async def informEndOfBroadcast(node: Node):
    message = json.dumps({"message": Message.END_OF_BROADCAST})
    print("Closing",node.id)
    await node.writeToNode(message)
    node.closeConnection()
    print("Closed",node.id)

async def closeConnectionToNodes(nodes: typing.List[Node]):
    for task in listeningTasks:
        try:
            print("Cancelling producer")
            task.cancel()
        except:
            print("Cannot close this producer")
    await asyncio.gather(*[asyncio.create_task(informEndOfBroadcast(node)) for node in nodes], return_exceptions=True)
    

async def keepListeningForMessageFromNode(node: Node, ouputQueue: asyncio.Queue) -> None:    
    '''Keep listening to a node until they send a message `quit` or `endOfBroadcast`

    The data read from the node will contain a key `message` which will contain the message
    '''
    try:
        dataRead: str = await node.readFromNode(Message.MESSAGE_SIZE)
        if dataRead.__len__() == 0:
            print("Connection with", node.id,"has been terminated.")
            return
        message:dict = json.loads(dataRead)
        messageText = message["message"]
        while messageText != Message.QUIT_BROADCAST and messageText != Message.END_OF_BROADCAST:
            await ouputQueue.put(message)
            dataRead = await node.readFromNode(Message.MESSAGE_SIZE)
            message = json.loads(dataRead)
            messageText = message["message"]
        
        if messageText == Message.QUIT_BROADCAST:
            print(node.id,"decided to quit")
            node.closeConnection()
            producers.remove(node)
            pass
        else:
            producers.remove(node)
            await ouputQueue.put(message)
    except asyncio.CancelledError:
        #print("Some error for node", node.id)
        pass

async def keepListeningFromAllNodes(nodes: typing.List[Node], ouputsQueue: asyncio.Queue):
    '''Ctreate tasks to listen from all the nodes in the list of nodes
    '''
    print("Started listening from all nodes...")
    await asyncio.gather(*[asyncio.create_task(keepListeningForMessageFromNode(node, ouputsQueue)) for node in nodes], return_exceptions=True)

async def writeMessageToAllTheNodes(message: dict, nodes: typing.List[Node]):
    enocdedMessage = json.dumps(message)
    listOfNodes = [asyncio.create_task(node.writeToNode(enocdedMessage)) for node in nodes]
    await asyncio.gather(*listOfNodes, return_exceptions= True)

async def startBroadcasting(server: Server , consumers: typing.List[Node], producers: typing.List[Node]):
    global outputsQueue
    outputsQueue = asyncio.Queue(loop=asyncio.get_event_loop())
    newMessage: dict = await outputsQueue.get()
    messageText = newMessage["message"]
    while messageText != Message.END_OF_BROADCAST:
        writeToAllListeners = [asyncio.create_task(writeMessageToAllTheNodes(newMessage, consumers))]
        await asyncio.gather(*writeToAllListeners,return_exceptions=True)
        outputsQueue.task_done()
        newMessage = await outputsQueue.get()
        messageText = newMessage["message"]
    await closeConnectionToNodes(consumers+producers)
    server.close()

async def main():
    server = await asyncio.start_server(addNewConnection, '127.0.0.1', 8888)

    task_3 = asyncio.create_task(startBroadcasting(server, consumers, producers))

    print('Starting broadcast...')
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except asyncio.CancelledError:
        print("Closing script....")
import asyncio
from message import Message
import json
import typing

class Node:
    def __init__(self, id: str, role: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        '''Create a new node with the given specification
        Parameters
        ----------
        id: str
            an alphanumeric string describing the node
        role: str
            a string representing the role of the node
        reader: StreamReader
            the StreamReader object associated with the node
        writer: StreamWriter
            the StreamWriter object associated with the node
        '''
        self.id = id
        self.role = role
        self.reader = reader
        self.writer = writer
        self.nonce = 0
    
    async def writeToNode(self, data: str):
        '''Write a message to the node
        Parameters
        ----------
        data: str
            a json string representing the data to be sent to the node
        '''
        self.writer.write(data.encode())
        await self.writer.drain()
        self.nonce += 1
    
    async def readFromNode(self, numBytes: int) -> str:
        '''Read any meessage sent by the node
        Parameters
        ----------
        numBytes : int
            number of bytes to read from the node
        '''
        data = await self.reader.read(numBytes)
        return data.decode()

    def closeConnection(self):
        '''Close the connection with the node
        '''
        self.writer.close()
    
    def __str__(self) -> str:
        return f'Node {self.id} ({self.role})'
    
    def toJson(self) -> str:
        dic: dict = {'id':self.id,'role':self.role,'nonce':self.nonce}
        return json.dumps(dic)
    
    def get_id(self) -> str:
        return self.id
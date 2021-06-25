Run the scripts in the following sequence

```cmd
virtualenv -p python3 venv
scripts\venv\activate
pip install -r requirements.txt
python src\broadcastServer.py # run them in different window
python src\broadcastWriter.py # run them in different window
python src\broadcastReader.py # run them in different window
```

**Always** start with running the `src\broadcastServer.py` then the other two broadcast scripts can be run in any order. All the requests are served at `127.0.0.1:8888`.

### broadcastWriter.py
Running this script will give you a console to write messages to the server and broadcast it to all the listeners. After running the script you'll be asked to enter an identifier before establishing a connection with server. This identifier will be shown to all the listeners whenever you enter a message.

Enter *quit* to exit the writer or *eob* to close the entire broadcast session.

### broadcastReader.py
Running this script will give you a console where you will see all the messages sent by the writers. You will be asked to enter an identifier before connecting with the server. To close the listener press `ctrl+c` but you will have to wait for at least one message from the server for the listener to close down.

server.py and cient.py were experimental scripts. They can be used to understand the general structure of the asyncio streams. 
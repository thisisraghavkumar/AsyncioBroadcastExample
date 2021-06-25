import json
import time

class Message:
    END_OF_BROADCAST = "eob"
    ROLE_LISTEN = "listen"
    ROLE_WRITE = "write"
    QUIT_BROADCAST = "quit"
    INVALID_ROLE = "Invalid role! Allowed values are 'read' and 'write'."
    CONFIRM_ROLE = "confirm"
    DENY_ROLE = "denied"
    KEY_ERROR = "key error"
    ACK = "acknowledge"
    MESSAGE_SIZE = 100
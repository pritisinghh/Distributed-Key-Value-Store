For this programming assignment, my task was to design and implement a distributed multi consistency key value store which shows the different consistency schemes that use the underlying key-value store replicas.
I have used the key vaue store from the first assignment which takes the input in the following manner
Set
The set command is whitespace delimited, and consists of two lines:
set <key> <value> \r\n
The server should respond with either "STORED\r\n", or "NOT-STORED\r\n".
Get
Retrieving data is simpler: get <key>\r\n
The server should respond with two lines: VALUE <key> <bytes> \r\n
<data block>\r\n
I have spawned multiple processes for multiple servers that could handle multiple clients. The following are the architecture , design and test cases for each of the model. Architecture – Eventual Consistency
I have implemented the broadcasting method to achieve this. I have spawned multiple servers for this and these servers can be connected to multiple clients. The server which gets connected to client writes to its local copy first and then broadcast it to other servers which keep listening.
Once they receive the broadcast message, they update their key value store.
For read the client can be connected to any server and there are also chances that it may receive stale reads On a high level, the following steps were taken to achieve eventual consistency

# How to run 

## Eventual
`
## Server

`
python ServerEventual.py
`

## Client

`
python ClientEventual.py

## Causal
`
## Server

`
python ServerCau.py
`

## Client

`
python ClientCau.py

## Sequential
`
## Server

`
python ServerSeq.py
`

## Client

`
python ClientSeq.py

## Primary
`
python Primary.py

## Linearizibility
`
## Server

`
python ServerLin.py
`

## Client

`
python ClientLin.py

## Primary
`
python PrimaryLin.py

`
`
To test with different ports change the constants.py file

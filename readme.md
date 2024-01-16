# Distributed Multi-Consistency Key-Value Store

## Introduction

This repository contains the implementation of a distributed multi-consistency key-value store. The goal of this programming assignment was to design and implement a system that showcases different consistency schemes using underlying key-value store replicas. I have used zeroMQ PUB-SUB architecture to achieve all this consistency model.

## Key-Value Store Specification

The key-value store accepts commands in the following format:

### Set
The set command is whitespace delimited and consists of two lines:
```
set <key> <value> \r\n
```
The server responds with either "STORED\r\n" or "NOT-STORED\r\n".

### Get
Retrieving data is done using the following command:
```
get <key>\r\n
```
The server responds with two lines:
```
VALUE <key> <bytes> \r\n
<data block>\r\n
```

## Architecture - Eventual Consistency

The system achieves eventual consistency by implementing a broadcasting method. Multiple servers are spawned to handle multiple clients. When a server receives a write request from a client, it first updates its local copy and then broadcasts the update to other servers. Clients may connect to any server for reads, but there's a possibility of receiving stale reads.

## Architecture - Sequential Consistency

Sequential consistency is implemented using a primary-based model. Write requests (set) are sent to the primary, which updates its key-value store and broadcasts the message to other server replicas. After receiving the broadcast, replicas send an acknowledgement to the primary and respond to the client.

## Architecture - Linearizability

Linearizability is achieved using the primary-based protocol with the added feature that reads (get) are blocking. Read requests are also sent to the primary, and replicas respond to the client only after obtaining the appropriate value from the primary, ensuring clients receive a coherent view at all times.

## Architecture - Causal Consistency

Causal consistency is implemented by ensuring the order of operations (updates and reads) is consistent with the causal dependencies between them. Vector clocks are used to track causal dependencies between operations.

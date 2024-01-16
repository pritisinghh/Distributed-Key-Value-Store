import multiprocessing
import zmq
import threading
import os
from constants import DATA_DIR, SERVER_CNT, START_SERVER_PORT, HOST, START_BROADCAST_PORT
from random import random
from time import sleep
from datetime import datetime


class VectorClock:
    def __init__(self, server_cnt):
        self.clocks = [0] * server_cnt

    def increment(self, server_id):
        self.clocks[server_id] += 1

    def compare(self, other_clocks):
        for i in range(len(self.clocks)):
            if self.clocks[i] < other_clocks[i]:
                return -1
            elif self.clocks[i] > other_clocks[i]:
                return 1
        return 0

    def to_string(self):
        return ','.join(str(x) for x in self.clocks)

class Server:
    def __init__(self, server_id, host, port, kv_file_name, broadcastPort, vector_clock):
        self.server_id = server_id
        self.host = host
        self.port = port
        self.kv_file_name = kv_file_name
        self.broadcastPort = broadcastPort
        self.vector_clock = vector_clock

    def handle_client(self, socket, lock, publisher):
        while True:
            msg = socket.recv_string()
            if not msg:
                break
            parts = msg.split(" ")
            action = parts[0].lower()
            response = ""
            file_path = os.path.join(DATA_DIR, self.kv_file_name)
            if action == "set":
                key = parts[1]
                value = parts[2]
                self.vector_clock.increment(self.server_id)
                clock = self.vector_clock.clocks.copy()
                with open(file_path, "a+") as f:
                    sleep(random())
                    f.seek(0)
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if line.startswith(key + ":"):
                            old_value = line.strip().split(":")[1]
                            old_clock = [int(c) for c in line.strip().split(":")[2].split(",")]
                            if self.vector_clock.compare(old_clock) > 0:
                                pairwise_max = tuple(max(x, y) for x, y in zip(clock, old_clock))
                                lines[i] = f"{key}:{value}:{','.join(str(c) for c in pairwise_max)}\n"
                                f.writelines(lines[i])
                                print("key found again , storing it with updated vector clock")
                                response = "STORED"
                                break
                            else:
                                f.seek(0)
                                pairwise_max = tuple(max(x, y) for x, y in zip(clock, old_clock))
                                lines[i] = f"{key}:{value}:{','.join(str(c) for c in pairwise_max)}\n"
                                f.writelines(lines[i])
                                response = "STORED"
                                break
                    else:
                        f.write(f"{key}:{value}:{','.join(str(c) for c in clock)}\n")
                        response = "STORED"
            elif action == "get":
                key = parts[1]
                with open(file_path, "r") as f:
                    sleep(random())
                    data = f.readlines()
                    if len(data) == 0:
                        response = "KEY NOT FOUND"
                    for line in reversed(data):
                        k, v, clock_str = line.strip().split(":")
                        clock = [int(c) for c in clock_str.split(",")]
                        if k == key:
                            if self.vector_clock.compare(clock) > 0:
                                print("mutiple values found returning the latest one")
                                response = f"VALUE {key} {len(v)}\r\n{v}\r\nEND\r\n"
                            else:
                                response = f"VALUE {key} {len(v)}\r\n{v}\r\nEND\r\n"
                            break
                    else:
                        response = "KEY NOT FOUND"
            else:
                response = "Invalid"
            socket.send_string(response)
            self.broadcast(msg, publisher)

        socket.close()

    def broadcast(self, msg, publisher):
        self.vector_clock.increment(self.server_id)
        msg = f"{self.vector_clock.to_string()} {msg}"
        for i in range(SERVER_CNT-1):
            publisher.send_string(msg)
        print(f"Server {self.server_id} broadcasted message '{msg}'")

    def handle_subscriber(self, subscriber):
        while True:
            for i in range(SERVER_CNT):
                if START_SERVER_PORT+i!=self.port:
                    message = subscriber.recv_string()
                    port=START_SERVER_PORT+i
                    print(f"Server {port} received broadcasted message '{message}' " )
                    parts = message.split(" ")
                    action = parts[1].lower()
                    fileName="key_value_store_"+str(port)+".txt"
                    # print(fileName)
                    file_path = os.path.join(DATA_DIR, fileName)
                    if action == "set":
                        key = parts[2]
                        value = parts[3]
                        self.vector_clock.increment(self.server_id)
                        clock = self.vector_clock.clocks.copy()

                        with open(file_path, "a+") as f:
                            sleep(random())
                            f.seek(0)
                            lines = f.readlines()
                            for i, line in enumerate(lines):
                                if line.startswith(key + ":"):
                                    old_value = line.strip().split(":")[1]
                                    old_clock = [int(c) for c in line.strip().split(":")[2].split(",")]
                                    if self.vector_clock.compare(old_clock) > 0:
                                        pairwise_max = tuple(max(x, y) for x, y in zip(clock, old_clock))
                                        lines[i] = f"{key}:{value}:{','.join(str(c) for c in pairwise_max)}\n"
                                        f.writelines(lines[i])
                                        print("key found again , storing it with updated vector clock")
                                        response = "STORED"
                                        break
                                    else:
                                        f.seek(0)
                                        pairwise_max = tuple(max(x, y) for x, y in zip(clock, old_clock))
                                        lines[i] = f"{key}:{value}:{','.join(str(c) for c in pairwise_max)}\n"
                                        f.writelines(lines[i])
                                        response = "STORED"
                                        del lines[i]
                                        break
                            else:
                                f.write(f"{key}:{value}:{','.join(str(c) for c in clock)}\n")
                                response = "STORED"
                    elif action == "get":
                        key = parts[2]
                        with open(file_path, "r") as f:
                            sleep(random())
                            data = f.readlines()
                            if len(data) == 0:
                                response = "KEY NOT FOUND"
                            for line in reversed(data):
                                k, v, clock_str = line.strip().split(":")
                                clock = [int(c) for c in clock_str.split(",")]
                                if k == key:
                                    if self.vector_clock.compare(clock) > 0:
                                        print("mutiple values found returning the latest one")
                                        response = f"VALUE {key} {len(v)}\r\n{v}\r\nEND\r\n"
                                    else:
                                        response = f"VALUE {key} {len(v)}\r\n{v}\r\nEND\r\n"
                                    break
                            else:
                                response = "KEY NOT FOUND"
                    else:
                        response = "Invalid"
                    print(response)
    def start_server(self):
        # create context and sockets
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        publisher = context.socket(zmq.PUB)

        print(f"Server started listening on {self.port} " )
        # bind sockets to ports
        socket.bind(f"tcp://*:{self.port}")
        publisher.bind(f"tcp://*:{self.broadcastPort}")

        # create lock for thread safety
        lock = threading.Lock()

        # start client handler thread
        client_thread = threading.Thread(target=self.handle_client, args=(socket, lock, publisher,))
        client_thread.start()

        # wait for threads to finish
        client_thread.join()
        # subscriber_thread.join()

if __name__ == "__main__":
    if not  os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    print("Listening ...")
    servers = []
    processes = []
    for i in range(SERVER_CNT):
        KV_file_name = f"key_value_store_{START_SERVER_PORT+i}.txt"
        vector=VectorClock(SERVER_CNT)
        server = Server(i,HOST, START_SERVER_PORT+i, KV_file_name,START_BROADCAST_PORT+i,vector)
        servers.append(server)
        p = multiprocessing.Process(target=server.start_server)
        processes.append(p)
        p.start()

        contextSub = zmq.Context()
        subscriber = contextSub.socket(zmq.SUB)
        subscriber.connect(f"tcp://{HOST}:{START_BROADCAST_PORT+i}")
        subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        subscriber_thread = threading.Thread(target=server.handle_subscriber, args=(subscriber,))
        subscriber_thread.start()

    for p in processes:
        p.join()
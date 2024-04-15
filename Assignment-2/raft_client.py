

import logging

import grpc
import raft_pb2
import raft_pb2_grpc
import json
import random

from concurrent import futures

def run(node_ip_adds, leader_id):

    
    print("Client is active ...")
    while(True):
        print("Welcome to Client interface")
        print("Please choose one of the following options: ")
        print("1 -> SET operation \n2 -> GET operation")
        inp = int(input())
        if inp == 1:
            key = input("Enter the key: ")
            value = input("Enter the value: ")
            operation = "SET " + str(key) + " " + str(value)
            last_leader = leader_id
            while True:
                leader = 0
                suc = False
                try:
                    channel = grpc.insecure_channel(node_ip_adds[leader_id])
                    stub = raft_pb2_grpc.RaftNodeStub(channel)
                    response = stub.ServeClient(raft_pb2.ServeClientArgs(request = operation))
                    suc = response.success
                    leader = response.leaderId
                except:
                    leader_id = random.choice(list(node_ip_adds.keys()))
                if not suc:
                    leader_id = leader
                else:
                    break
            print(f"Data: {response.data}, leader id: {response.leaderId}, success: {response.success}")

        elif inp == 2:
            
            key = input("Enter the key: ")
            operation = "GET " + str(key)
            value = ""
            while True:
                suc = False
                leader = 0
                try:
                    channel = grpc.insecure_channel(node_ip_adds[leader_id])
                    stub = raft_pb2_grpc.RaftNodeStub(channel)
                    response = stub.ServeClient(raft_pb2.ServeClientArgs(request = operation))
                    suc = response.success
                    leader = response.leaderId
                except:
                    print("Error connecting to node. Retrying...")
                    leader_id = random.choice(list(node_ip_adds.keys()))
                if not suc:
                    leader_id = leader
                    print("Failed. Retrying....")
                
                else:
                    value = response.data
                    break
            print(f"Data: {response.data}, leader id: {response.leaderId}, success: {response.success}")
            

if __name__ == "__main__":
    logging.basicConfig()

    server_ip_ports = {}
    ip_port = input("Enter your IP port: ")
    # id = int(input("Enter your ID: "))

    server_ip_ports = {}

    f = open("ip_ports.json")
    data = json.load(f)
    for val in data["ip_ports"]:
        server_ip_ports[val["nodeId"]] = val["nodeIpPort"]
    # server_ip_ports[id] = ip_port
    f.close()

    leader_id = 1
    # port = 50001
    # server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # raft_pb2_grpc.add_ClientServiceServicer_to_server(ClientServicer(), server)
    # server.add_insecure_port('[::]:' + str(port))
    # server.start()
    # print("Client started...")
    
    run(server_ip_ports, leader_id)

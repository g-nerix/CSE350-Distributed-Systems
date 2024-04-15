import grpc
from concurrent import futures

import time
import raft_pb2
import raft_pb2_grpc
import random
import threading
import json


class RaftNode(raft_pb2_grpc.RaftNodeServicer):
    def __init__(self, id, ip_port, server_ip_ports, reset_logs):
        self.clientIpAdd = None
        self.serverIpAdds = server_ip_ports
        self.leaderId = None
        self.nodeId = id
        self.currentTerm = 0
        self.votedFor = None
        self.keyValueCommits = {}
        self.log = [] # Each term* is a dictionary - {"command": [Key, value], "term": No}, Key -> None and value -> None means No  OP
        
        self.ackedIndex = {}
        self.commitIndex = -1
        self.lastApplied = -1

        self.totalServers = 4
        
        self.lastLeaseStartTime = None
        self.leaseDuration = 10
        self.leaseTimer = None
        self.electionTimeout = random.randint(5, 10)
        self.heartbeatTimeout = 1
        
        self.nextIndex = {}
        self.matchIndex = {}

        self.electionTimer = None
        self.heartbeatTimer = None
        
        prefix = "logs_node_" + str(self.nodeId) + "/"
        self.logFile = prefix + "logs.txt"
        self.dumpFile = prefix + "dumps.txt"
        self.metadataFile = prefix + "metadata.txt"

        self.state = 0 # 0 -> follower, 1 -> candidate, 2 -> leader
        

        if reset_logs:
            self.clearFile(self.logFile)
            self.clearFile(self.dumpFile)
            self.clearFile(self.metadataFile)
        else:
            try:
                f = open(self.logFile, "r")
                logs = f.readlines()
                f.close()
                f = open(self.metadataFile, "r")
                metadata = f.readlines()
                f.close()
            


                for i in logs:
                    log_entry = i
                    if len(log_entry) >= 1 and log_entry[-1] == "\n":
                        log_entry = log_entry[:-1]
                    commands = log_entry.split()

                    entry = {}
                    entry["term"] = int(commands[-1])
                    if commands[0] == "SET":
                        entry["command"] = [commands[1], commands[2]]
                    else:
                        entry["command"] = [None, None]
                    self.log.append(entry)
                
                for i in metadata:
                    temp = i
                    if len(temp) >= 1 and temp[-1] == "\n":
                        temp = temp[:-1]
                    vals = temp.split()

                    if vals[0].lower() == "commitindex":
                        self.commitIndex = int(vals[1])
                    elif vals[0].lower() == "term":
                        self.currentTerm = int(vals[1])
                    else:
                        self.votedFor = int(vals[1])
                print(self.log)
                print(self.commitIndex, self.votedFor, self.currentTerm)
            except Exception as e:
                print(e)
                print("Error in opening file")
                self.clearFile(self.logFile)
                self.clearFile(self.dumpFile)
                self.clearFile(self.metadataFile)
            
        self.resetElectionTimer()





    def clearFile(self, file):
        open(file, "w").close()

    def ServeClient(self, request, context):
        if self.state != 2:
            # return False
            return raft_pb2.ServeClientReply(data = "Failed. Node is not the leader", leaderId = self.leaderId, success = False)
        
        else:
            text = f"Node {self.nodeId} (leader) received a {request.request} request."
            print(text)
            self.appendToFile(self.dumpFile, text + "\n")
            client_req = request.request.split()
            command = client_req[0]

            
            if command == "SET":
                # Adding log entry
                entry = {"term": self.currentTerm, "command": client_req[1:]}
                self.log.append(entry)
                self.ackedIndex[self.nodeId] = len(self.log) - 1
                self.addToLog(entry)
                self.sendHeartbeats()
                while True:
                    if self.commitIndex == len(self.log) - 1:
                        break
                    time.sleep(1.5)
                return raft_pb2.ServeClientReply(data = "Entry committed successfully", leaderId = self.leaderId, success = True)
                # if self.state != 2:
                #     return raft_pb2.ServeClientReply(data = "", leaderId = self.leaderId, success = False)
                # elif self.commitIndex == len(self.log) - 1:
                #     return raft_pb2.ServeClientReply(data = "", leaderId = self.leaderId, success = True)
                # else:
                #     return raft_pb2.ServeClientReply(data = "", leaderId = self.leaderId, success = False)
            
            elif command == "GET":
                if client_req[1] not in self.keyValueCommits:
                    out = ""
                    out2 = self.keyValueCommits[client_req[1]] 
                    print(out2)
                else:
                    out = self.keyValueCommits[client_req[1]]
                    # print(out)
                return raft_pb2.ServeClientReply(data = out, leaderId = self.leaderId, success = True)
                 



    def appendToFile(self, file_path, text):
        f = open(file_path, "a")
        f.write(text)   
        f.close() 
    
    def cancelTimers(self):
        if self.electionTimer:
            self.electionTimer.cancel()
        if self.heartbeatTimer:
            self.heartbeatTimer.cancel()
        if self.leaseTimer:
            self.leaseTimer.cancel()
    
    def resetElectionTimer(self):
        if self.electionTimer:
            self.electionTimer.cancel()
        self.electionTimer = threading.Timer(self.electionTimeout, self.startElection)
        self.electionTimer.start()
    
    def resetLeaseTimer(self):
        if self.leaseTimer:
            self.leaseTimer.cancel()
        self.leaseTimer = threading.Timer(self.leaseDuration, self.leaseTimeout)
        self.lastLeaseStartTime = time.time()
        self.leaseTimer.start()
    
    def leaseTimeout(self):
        if self.state == 2:
            text = f"Leader {self.nodeId} lease renewal failed. Stepping Down."
            print(text)
            self.appendToFile(self.dumpFile, text + "\n")
            self.becomeFollower(self.currentTerm)
    
    def startElection(self):
        text = f"Node {self.nodeId} election timer timed out, Starting election."
        print(text)
        self.appendToFile(self.dumpFile, text + "\n")
        # self.cancelTimers()
        self.becomeCandidate()

    def becomeCandidate(self):
        self.state = 1
        self.currentTerm += 1
        self.votedFor = self.nodeId
        self.writeMetadata()
        self.resetElectionTimer()
        self.requestVotesFromAll()
    
    def addNoOptoLog(self):
        entry = {"term": self.currentTerm, "command": [None, None]}
        self.log.append(entry)
        self.addToLog(entry)
        self.ackedIndex[self.nodeId] = len(self.log) - 1
    
    def becomeLeader(self):
        print(self.nodeId , " became Leader.")
        self.state = 2
        self.addNoOptoLog()
        self.cancelTimers()
        self.resetLeaseTimer()
        # self.resetElectionTimer()
        self.resetHeartbeatTimer()
        # Initialize next_index and match_index for all servers (including self)
        for server_id in range(self.totalServers):  # Replace with actual server IDs
            if server_id == self.nodeId:
                continue
            self.nextIndex[server_id] = 0
            self.matchIndex[server_id] = len(self.log) - 1
            self.ackedIndex[server_id] = -1
        
        self.writeMetadata()
        self.sendHeartbeats()

    def becomeFollower(self, term):
        self.state = 0
        self.currentTerm = term
        self.votedFor = None
        self.cancelTimers()
        self.resetElectionTimer()
        self.writeMetadata()
    
    def resetHeartbeatTimer(self):
        if self.heartbeatTimer:
            self.heartbeatTimer.cancel()
        self.heartbeatTimer = threading.Timer(self.heartbeatTimeout, self.sendHeartbeats)
        self.heartbeatTimer.start()
    
    def sendHeartbeats(self):
        
        self.resetHeartbeatTimer()
        if self.state != 2:
            return
        text = f"Leader {self.nodeId} sending heartbeat & Renewing Lease"
        print(text)
        self.appendToFile(self.dumpFile, text + "\n")
        trueCount = 1
        for server_id in range(self.totalServers):
            if server_id == self.nodeId:
                continue

            try:
                print(f"Sending heartbeat to {server_id} from leader {self.nodeId}")
                prev_log_index = self.matchIndex[server_id]
                prev_log_term = 0
                if len(self.log) > 0:
                    prev_log_term = self.log[prev_log_index]["term"]
                entries = []
                if prev_log_index < len(self.log) - 1:
                    entries = self.log[prev_log_index + 1:]
                # entries = self.log[prev_log_index + 1:]
                channel = grpc.insecure_channel(self.serverIpAdds[server_id])  # Replace port appropriately
                stub = raft_pb2_grpc.RaftNodeStub(channel)

                entries_rpc_arg = []
                for i in entries:
                    entries_rpc_arg.append(raft_pb2.LogEntry(term = i["term"], command = raft_pb2.Command(key = i["command"][0], value = i["command"][1])))
                response = stub.ServeLogRequest(raft_pb2.AppendEntriesRequest(
                    term=self.currentTerm,
                    leaderId=self.nodeId,
                    prevLogIndex=prev_log_index,
                    prevLogTerm=prev_log_term,
                    entries=entries_rpc_arg,
                    leaderCommitIndex=self.commitIndex,
                    leaseDuration = self.leaseDuration
                ))
                if response.success:
                    trueCount += 1
                self.logReplyProcess(response)
                # if response.currentTerm > self.currentTerm:
                #     self.becomeFollower()  # Step down if higher term received
                #     return
                # if not response.success:
                #     # Handle unsuccessful heartbeat (e.g., follower log out of sync)
                #     self.updateNextIndex(server_id, next_index - 1)  # Decrement next_index for retry
            except grpc.RpcError as e:
                # Handle potential gRPC errors (e.g., connection issues)
                text = f"Error occurred while sending RPC to Node {server_id}."
                print(e)
                print(text)
                self.appendToFile(self.dumpFile, text + "\n")
                
            if trueCount >= (self.totalServers // 2) + 1:
                self.resetLeaseTimer()


    def updateNextIndex(self, server_id, new_next_index):
        """Updates the next_index for a follower server."""
        self.nextIndex[server_id] = max(new_next_index, 0)  # Ensure non-negative next_index
    
    def requestVotesFromAll(self):
        """Sends RequestVote RPCs to all servers and gathers responses."""
        votes_granted = 1  # Count our own vote
        max_lease_remaining  = -1
        for server_id in range(self.totalServers):  # Replace with actual server IDs
            if server_id == self.nodeId:
                continue

            
            try:
                channel = grpc.insecure_channel(self.serverIpAdds[server_id])  # Replace port appropriately
                stub = raft_pb2_grpc.RaftNodeStub(channel)
                last_log_index = len(self.log) - 1
                last_log_term = 0
                if len(self.log) > 0:
                    last_log_term = self.log[-1]["term"]
                response = stub.ServeVoteRequest(raft_pb2.GetVoteRequest(
                    term=self.currentTerm,
                    nodeId=self.nodeId,
                    lastLogIndex=last_log_index,
                    lastLogTerm=last_log_term
                ))
                if response.term > self.currentTerm:
                    if self.state == 2:
                        text = f"{self.nodeId} Stepping down"
                        print(text)
                        self.appendToFile(self.dumpFile, text + "\n")
                    self.becomeFollower(response.term)  # Step down if higher term received
                    return
                if response.success:
                    votes_granted += 1
                    remaining_time = 0
                    if self.lastLeaseStartTime != None:
                        remaining_time = max(0, self.leaseDuration - (time.time() - self.lastLeaseStartTime))
                    max_lease_remaining = max(max_lease_remaining, response.leaseDurationRemaining, remaining_time)
                if votes_granted > self.totalServers // 2:  # Majority check
                    text = "New Leader waiting for Old Leader Lease to timeout."
                    print(text)
                    self.appendToFile(self.dumpFile, text + "\n")
                    time.sleep(max_lease_remaining)
                    text = f"Node {self.nodeId} became the leader for term {self.currentTerm}."
                    print(text)
                    self.appendToFile(self.dumpFile, text + "\n")
                    self.becomeLeader()
                    return
            except grpc.RpcError as e:
                # Handle potential gRPC errors (e.g., connection issues)
                print(e)
                text = f"Error occurred while sending RPC to Node {server_id}."
                print(text)
                self.appendToFile(self.dumpFile, text + "\n")
    
    
    def writeMetadata(self):
        f = open(self.metadataFile, "w")
        f.write(f"CommitIndex {self.commitIndex}\nTerm {self.currentTerm}\nVotedFor {self.votedFor}")
        f.close()

    def ServeVoteRequest(self, request, context):
        if request.term > self.currentTerm:
            self.currentTerm = request.term
            self.state = 0
            self.votedFor = None
            self.resetElectionTimer()
        lastTerm = 0
        if len(self.log) > 0:
            lastTerm = self.log[-1]["term"]
        logCheck = (request.lastLogTerm > lastTerm) or (request.lastLogTerm == lastTerm and request.lastLogIndex + 1 >= len(self.log))

        if request.term == self.currentTerm and logCheck and (self.votedFor == request.nodeId or self.votedFor == None):
            self.votedFor = request.nodeId
            self.resetElectionTimer()
            text = f"Vote granted for Node {request.nodeId} in term {request.term}"
            print(text)
            self.appendToFile(self.dumpFile, text + "\n")
            remaining_time = 0
            if self.lastLeaseStartTime != None:
                remaining_time = max(0, self.leaseDuration - (time.time() - self.lastLeaseStartTime))
            self.writeMetadata()
            return raft_pb2.VoteRequestReply(nodeId = self.nodeId, term = self.currentTerm, leaseDurationRemaining = remaining_time, success = True)
        else:
            text = f"Vote denied for Node {request.nodeId} in term {request.term}"
            print(text)
            self.appendToFile(self.dumpFile, text + "\n")
            remaining_time = 0
            self.writeMetadata()
            if self.lastLeaseStartTime != None:
                remaining_time = max(0, self.leaseDuration - (time.time() - self.lastLeaseStartTime))
            return raft_pb2.VoteRequestReply(nodeId = self.nodeId, term = self.currentTerm, leaseDurationRemaining = remaining_time, success = False)

    def ServeLogRequest(self, request, context):
        self.resetElectionTimer()
        term = request.term 
        leaderId = request.leaderId 
        previousLogIndex = request.prevLogIndex 
        prevLogTerm = request.prevLogTerm
        leaseDuration = request.leaseDuration
        self.leaseDuration = leaseDuration
        self.resetLeaseTimer()

        entries = []
        for i in request.entries:
            key = i.command.key
            value = i.command.value
            if key == '':
                key = None
            if value == '':
                value = None
            entries.append({"term": i.term, "command": [key, value]})
        leaderCommit = request.leaderCommitIndex
        if term > self.currentTerm:
            if self.state == 2:
                text = f"{self.nodeId} Stepping down"
                print(text)
                self.appendToFile(self.dumpFile, text + "\n")
            self.becomeFollower(term)
            # self.currentTerm = term
            # self.votedFor = None
            

        if term == self.currentTerm:
            self.state = 0
            self.leaderId = leaderId
        
        logCheck = (len(self.log) >= previousLogIndex + 1) and (previousLogIndex + 1 == 0 or prevLogTerm == self.log[previousLogIndex]["term"])
        if term == self.currentTerm and logCheck:
            
            self.appendEntries(previousLogIndex, entries, leaderCommit)
            ack = previousLogIndex + 1 + len(entries)
            text = f"Node {self.nodeId} accepted AppendEntries RPC from {self.leaderId}."
            print(text)
            self.appendToFile(self.dumpFile, text + "\n")
            
            
            return raft_pb2.LogRequestReply(nodeId = self.nodeId, currentTerm = self.currentTerm, ack = ack, success = True)
            # send response with (nodeId, currentTerm, ack, true) to leaderId
        
        else:
            # send response with (nodeId, currentTerm, 0,False) to leaderId
            text = f"Node {self.nodeId} rejected AppendEntries RPC from {self.leaderId}."
            print(text)
            self.appendToFile(self.dumpFile, text + "\n")
            return raft_pb2.LogRequestReply(nodeId = self.nodeId, currentTerm = self.currentTerm, ack = 0, success = False)

    def logReplyProcess(self, response):
        nodeId = response.nodeId
        followerTerm = response.currentTerm 
        ackLength = response.ack
        success = response.success

        if followerTerm == self.currentTerm and self.state == 2:
            if success and ackLength - 1 >= self.ackedIndex[nodeId]:
                self.matchIndex[nodeId] = ackLength - 1
                self.ackedIndex[nodeId] = ackLength - 1
                self.commitLogEntries()
            elif self.matchIndex[nodeId] + 1 > 0:
                self.matchIndex[nodeId] -= 1
                # self.nextIndex[nodeId] -= 1
                # prev_log_index = len(self.log) - 1
                # prev_log_term = 0
                # if len(self.log) > 0:
                #     prev_log_index = self.log[-1]["term"]
                # entries_rpc_arg = []
                # for i in entries:
                #     entries_rpc_arg.append(raft_pb2.LogEntry(term = i["term"], command = raft_pb2.Command(key = i["command"][0], value = i["command"][1])))
                # entries = self.log[len(self.log):]
                # channel = grpc.insecure_channel(self.serverIpAdds[nodeId])  # Replace port appropriately
                # stub = raft_pb2_grpc.RaftNodeStub(channel)
                # response = stub.ServeLogRequest(raft_pb2.AppendEntriesRequest(
                #     term=self.currentTerm,
                #     leaderId=self.nodeId,
                #     prevLogIndex=prev_log_index,
                #     prevLogTerm=prev_log_term,
                #     entries=entries_rpc_arg,
                #     leaderCommitIndex=self.commitIndex,
                #     leaseDuration = self.leaseDuration
                # ))

                # self.logReplyProcess(response)
        
        elif followerTerm > self.currentTerm:
            if self.state == 2:
                text = f"{self.nodeId} Stepping down"
                print(text)
                self.appendToFile(self.dumpFile, text + "\n")
            self.becomeFollower(followerTerm)
        

    
    def addToLog(self, entry):
        term = entry["term"]
        key = entry["command"][0]
        value = entry["command"][1]

        text = ""
        if key == None and value == None:
            text = "NO-OP " + str(term)
        else:
            text = f"SET {key} {value} " + str(term)
        f = open(self.logFile, "a")
        f.write(text + "\n")
        f.close()
    
    def appendEntries(self, previousLogIndex, entries, leaderCommit):
        if len(entries) > 0 and len(self.log) > previousLogIndex + 1:
            index = min(len(self.log), previousLogIndex + 1 + len(entries)) - 1
            if self.log[index]["term"] != entries[index - previousLogIndex - 1]["term"]:
                self.log = self.log[:previousLogIndex]
        if previousLogIndex + len(entries) + 1 > len(self.log):
            for i in range(len(self.log) - previousLogIndex - 1, len(entries)):
                self.log.append(entries[i])
                self.addToLog(entries[i])
        
        if leaderCommit > self.commitIndex:
            # Commit all entries using for loop
            for i in range(self.commitIndex + 1, leaderCommit):
                key = i["command"][0]
                value = i["command"][1]
                self.keyValueCommits[key] = value

                entry_type = ""
                if key == None and value == None:
                    entry_type = f"NO-OP"
                
                else:
                    entry_type = f"SET {key} {value}"

                print(f"Node {self.nodeId} (follower) committed the entry {entry_type} to the state machine")
            self.commitIndex = leaderCommit
            self.writeMetadata()



    
    def getAcks(self, length):
        count = 0
        for i in self.ackedIndex:
            if self.ackedIndex[i] + 1 >= length:
                count += 1
        return count

    def commitLogEntries(self):
        minAcks = (self.totalServers // 2) + 1
        ready_len = []
        for i in range(1, len(self.log) + 1):
            acks = self.getAcks(i)
            if acks >= minAcks:
                ready_len.append(i)
        if ready_len != [] and max(ready_len) > self.commitIndex + 1 and self.log[max(ready_len) - 1]["term"] == self.currentTerm:
            for i in range(self.commitIndex + 1, max(ready_len)):
                entry_type = ""
                key = self.log[i]["command"][0]
                value = self.log[i]["command"][1]
                if key == None and value == None:
                    entry_type = f"NO-OP"
                else:
                    entry_type = f"SET {key} {value}"
                text = f"Node {self.nodeId} (leader) committed the entry {entry_type} to the state machine."
                print(text)
                self.appendToFile(self.dumpFile, text + "\n")
        
            self.commitIndex = max(ready_len) - 1
        self.writeMetadata()            

def serve():
    
    # ip_port = '[::]:50051'
    id = int(input("Enter your ID: "))
    server_ip_ports = {}

    f = open("ip_ports.json")
    data = json.load(f)
    for val in data["ip_ports"]:
        server_ip_ports[val["nodeId"]] = val["nodeIpPort"]
    # server_ip_ports[id] = ip_port
    f.close()
    ip_port = server_ip_ports[id]
    print(server_ip_ports)
    while True:
        s = int(input("Enter 1 to start (2 to clear logs): "))
        if s == 1 or s==2:
            break
    rlogs = False
    if s == 2:
        rlogs = True
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_pb2_grpc.add_RaftNodeServicer_to_server(RaftNode(id, ip_port, server_ip_ports, reset_logs = rlogs), server)
    server.add_insecure_port(ip_port)
    server.start()
    print("Raft node started...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
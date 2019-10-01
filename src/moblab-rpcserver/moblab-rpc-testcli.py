import grpc
import moblabrpc_pb2
import moblabrpc_pb2_grpc

if __name__ == '__main__':
    channel = grpc.insecure_channel('localhost:6002')
    stub = moblabrpc_pb2_grpc.MoblabRpcServiceStub(channel)
    print dir(stub)
    request = moblabrpc_pb2.ListConnectedDutsRequest()
    print stub.list_connected_duts(request)

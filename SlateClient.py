import cmd_pb2
import socket
import msgpack
import zlib
import hashlib


class SlateClient:
    def __init__(self, ip='192.168.2.2', cmd_port=1002):
        self.ip = ip
        self.cmd_port = cmd_port
        self.connected = False
        self.cmd_sock = None
        self.seq = 0
        self.slates = {}
        self.name = None
        self.version = None

    def __enter__(self):
        return self

    def connect(self):
        self.cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.query_slate_info()

        for slate_hash, slate in self.slates.items():
            slate['socket'] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            slate['socket'].bind(('', 0))
            self.request_udp_stream(
                slate_hash, slate['socket'].getsockname()[1])
            self.query_metaslate(slate_hash)

        self.connected = True

# query the device for the metaslate associated with a particular hash
    def query_metaslate(self, slate_hash):
        print(
            f"Requesting metaslate for slate \"{self.slates[slate_hash]['name']}\" ({hex(slate_hash)})")
        self.seq += 1
        msg = cmd_pb2.Message()
        msg.sequence = self.seq
        msg.request_metaslate.SetInParent()
        msg.request_metaslate.hash = slate_hash
        self.cmd_sock.sendto(msg.SerializeToString(), (self.ip, self.cmd_port))

        data = self.cmd_sock.recv(1024)
        read_msg = cmd_pb2.Message()
        read_msg.ParseFromString(data)
        assert read_msg.sequence == self.seq
        assert read_msg.WhichOneof('message') == 'response_metaslate'
        check_hash = int.from_bytes(hashlib.sha256(
            read_msg.response_metaslate.metaslate).digest()[:8], 'little')
        assert check_hash == slate_hash
        metaslate_data = zlib.decompress(read_msg.response_metaslate.metaslate)
        metaslate_data = msgpack.unpackb(metaslate_data)
        assert metaslate_data['slate'] == self.slates[slate_hash]['name']
        self.slates[slate_hash]['metaslate'] = metaslate_data
        print(
            f"Received valid metaslate for slate \"{self.slates[slate_hash]['name']}\" ({hex(slate_hash)}), describing {len(metaslate_data['channels'])} channels")


# request the device target a specific slate at the provided address and port

    def request_udp_stream(self, slate_hash, targetPort, targetAddr=0):
        print(
            f"Requesting UDP feed of slate \"{self.slates[slate_hash]['name']}\" ({hex(slate_hash)}) to {targetAddr}:{targetPort}")
        self.seq += 1
        msg = cmd_pb2.Message()
        msg.sequence = self.seq
        msg.start_udp.SetInParent()
        msg.start_udp.hash = slate_hash
        msg.start_udp.addr = targetAddr
        msg.start_udp.port = targetPort
        self.cmd_sock.sendto(msg.SerializeToString(), (self.ip, self.cmd_port))

        data = self.cmd_sock.recv(1024)
        read_msg = cmd_pb2.Message()
        read_msg.ParseFromString(data)
        assert read_msg.sequence == self.seq
        assert read_msg.WhichOneof('message') == 'ack'

# qeries the device for a list of available slates, and populates the results into self.slates
    def query_slate_info(self):
        print(f"Requesting slate list from {self.ip}")
        self.seq += 1
        msg = cmd_pb2.Message()
        msg.sequence = self.seq
        msg.query_info.SetInParent()
        self.cmd_sock.sendto(msg.SerializeToString(), (self.ip, self.cmd_port))

        data = self.cmd_sock.recv(1024)
        read_msg = cmd_pb2.Message()
        read_msg.ParseFromString(data)
        assert read_msg.sequence == self.seq
        assert read_msg.WhichOneof('message') == 'respond_info'
        self.name = read_msg.respond_info.name
        self.version = read_msg.respond_info.version
        print(f"Board name: {self.name}")
        print(f"Firmware build: {self.version}")
        for slate in read_msg.respond_info.slates:
            self.slates[slate.hash] = {
                'size': slate.size,
                'name': slate.name,
                'hash': slate.hash
            }
            print(
                f"Registered new slate \"{slate.name}\" with hash {hex(slate.hash)}")

    def __exit__(self, exc_type, exc_value, traceback):
        if cmd_sock:
            cmd_sock.close()
        if slate_sock:
            slate_sock.close()


if __name__ == "__main__":
    client = SlateClient()
    client.connect()

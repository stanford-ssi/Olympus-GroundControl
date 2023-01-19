import cmd_pb2
import socket
import msgpack
import zlib
import hashlib
from SlateClient import SlateClient
import asyncudp

class SnorkelClient:
    def __init__(self, ip, cmd_port):
        self.ip = ip
        self.cmd_port = cmd_port
        self.cmd_sock = None
        self.seq = 0
        self.slates = {}
        self.name = None
        self.version = None

    def __enter__(self):
        return self

    async def connect(self):
        while True:
            try:
                self.cmd_sock = await asyncio.wait_for(asyncudp.create_socket(remote_addr=(self.ip, self.cmd_port)), timeout=1.0)
                await asyncio.wait_for(self.query_slate_info(), timeout=1.0)
            except Exception as e:
                print(f"Device \"{self.name}\" at {self.ip}:{self.cmd_port} failed to connect with \"{e}\". Retrying in {1 if self.cmd_sock else 5} seconds.")
                await asyncio.sleep(1 if self.cmd_sock else 5)
                continue
            else:
                print(f"Device \"{self.name}\" at {self.ip}:{self.cmd_port} connected.")
                break


# query the device for the metaslate associated with a particular hash
    async def query_metaslate(self, slate_hash):
        self.seq += 1
        msg = cmd_pb2.Message()
        msg.sequence = self.seq
        msg.request_metaslate.SetInParent()
        msg.request_metaslate.hash = slate_hash
        self.cmd_sock.sendto(msg.SerializeToString())

        data, _ = await self.cmd_sock.recvfrom()
        read_msg = cmd_pb2.Message()
        read_msg.ParseFromString(data)
        assert read_msg.sequence == self.seq
        assert read_msg.WhichOneof('message') == 'response_metaslate'
        check_hash = int.from_bytes(hashlib.sha256(
            read_msg.response_metaslate.metaslate).digest()[:8], 'little')
        assert check_hash == slate_hash
        metaslate_data = zlib.decompress(read_msg.response_metaslate.metaslate)
        metaslate_data = msgpack.unpackb(metaslate_data)
        return metaslate_data
        
# request the device target a specific slate at the provided address and port
    async def request_udp_stream(self, slate_hash, targetPort, targetAddr=0):
        self.seq += 1
        msg = cmd_pb2.Message()
        msg.sequence = self.seq
        msg.start_udp.SetInParent()
        msg.start_udp.hash = slate_hash
        msg.start_udp.addr = targetAddr
        msg.start_udp.port = targetPort
        self.cmd_sock.sendto(msg.SerializeToString())

        data, _ = await self.cmd_sock.recvfrom()
        read_msg = cmd_pb2.Message()
        read_msg.ParseFromString(data)
        assert read_msg.sequence == self.seq
        assert read_msg.WhichOneof('message') == 'ack'
    
    async def write_cmd(self, cmd_msg):
        assert cmd_msg.WhichOneof('message') == 'set_field'
        self.seq += 1
        cmd_msg.sequence = self.seq
        self.cmd_sock.sendto(cmd_msg.SerializeToString())

        data, _ = await self.cmd_sock.recvfrom()
        read_msg = cmd_pb2.Message()
        read_msg.ParseFromString(data)
        assert read_msg.sequence == self.seq
        assert read_msg.WhichOneof('message') == 'ack'

# qeries the device for a list of available slates, and populates the results into self.slates
    async def query_slate_info(self):
        print(f"Requesting slate list from {self.ip}")
        self.seq += 1
        msg = cmd_pb2.Message()
        msg.sequence = self.seq
        msg.query_info.SetInParent()
        self.cmd_sock.sendto(msg.SerializeToString())
        data, _ = await self.cmd_sock.recvfrom()
        read_msg = cmd_pb2.Message()
        read_msg.ParseFromString(data)
        assert read_msg.sequence == self.seq
        assert read_msg.WhichOneof('message') == 'respond_info'
        self.name = read_msg.respond_info.name
        self.version = read_msg.respond_info.version
        print(f"Board name: {self.name}")
        print(f"Firmware build: {self.version}")
        for slate in read_msg.respond_info.slates:
            self.slates[slate.name] = SlateClient(self,slate.hash,slate.name,slate.size)
            print(
                f"Registered new slate \"{slate.name}\" with hash {hex(slate.hash)}")

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cmd_sock:
            self.cmd_sock.close()

'''This example works, but if the watchdog is on, the test might be interrupted'''
async def test():
    s = SnorkelClient('192.168.2.2',1002)
    await s.connect()
    key = "telemetry"
    await s.slates[key].connect()

    for _ in range(10):
        slate = await s.slates[key].recv_slate()
        print(
            f'tick {slate["tick"]} s1_pulse: {slate["s1_pulse"]} s1: {slate["s1"]} pt3: {slate["pt3"]}')

    await s.slates[key].set_field("s1_pulse",500)

    for _ in range(20):
        slate = await s.slates[key].recv_slate()
        print(
            f'tick {slate["tick"]} s1_pulse: {slate["s1_pulse"]} s1: {slate["s1"]} pt3: {slate["pt3"]}')

import asyncio
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test())
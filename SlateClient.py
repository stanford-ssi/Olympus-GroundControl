
import asyncudp
import struct
import cmd_pb2

class SlateClient:
    def __init__(self, snorkel, slate_hash, slate_name, slate_size):
        self.snorkel = snorkel
        self.hash = slate_hash
        self.name = slate_name
        self.size = slate_size
        self.metaslate = None
        self.udp_sock = None
        self.connected = False

    async def connect(self):
        if self.metaslate is None:
            self.fetch_metaslate()
        self.udp_sock = await asyncudp.create_socket(local_addr=('0', 0))
        port = self.udp_sock._transport._sock.getsockname()[1]
        self.start_udp(port)
        self.connected = True

    async def recv_slate(self):
        message, _ = await self.udp_sock.recvfrom()

        slate = {}
        for name, el in self.metaslate["channels"].items():
            if el["type"] == "int16_t":
                slate[name] = int.from_bytes(
                    message[el["offset"]:el["offset"]+el["size"]], "little", signed=True)
            elif el["type"] == "uint32_t":
                slate[name] = int.from_bytes(
                    message[el["offset"]:el["offset"]+el["size"]], "little", signed=False)
            elif el["type"] == "bool":
                slate[name] = (message[el["offset"]] != 0b0)
            elif el["type"] == "float":
                slate[name] = struct.unpack('f', message[el["offset"]:el["offset"]+el["size"]])[0]

        return slate

    def set_field(self,channel,value):
        channel_meta = self.metaslate["channels"][channel]
        msg = cmd_pb2.Message()
        msg.set_field.SetInParent()
        msg.set_field.hash = self.hash
        msg.set_field.offset = channel_meta["offset"]

        if channel_meta["type"] == "int16_t":
            msg.set_field.data_int16 = value
        elif channel_meta["type"] == "bool":
            msg.set_field.data_bool = value
        else:
            print("don't know how to write!")

        self.snorkel.write_cmd(msg)

    def fetch_metaslate(self):
        print(f"Requesting metaslate for slate \"{self.name}\" ({hex(self.hash)})")
        self.metaslate = self.snorkel.query_metaslate(self.hash)
        print(f"Received valid metaslate for slate \"{self.name}\" ({hex(self.hash)}), describing {len(self.metaslate['channels'])} channels")

    def start_udp(self,port):
        print(f"Requesting UDP feed of slate \"{self.name}\" ({hex(self.hash)}) to {port}")
        self.snorkel.request_udp_stream(self.hash,port)


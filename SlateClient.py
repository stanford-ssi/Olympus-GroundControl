
import asyncudp
import asyncio
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

    async def connect(self):
        if self.udp_sock is None:
            self.udp_sock = await asyncudp.create_socket(local_addr=('0', 0))

        try:
            await asyncio.wait_for(self.fetch_metaslate(), timeout=1.0)
            port = self.udp_sock._transport._sock.getsockname()[1]
            await asyncio.wait_for(self.start_udp(port), timeout=1.0)
        except Exception as e:
            print(f"Slate \"{self.snorkel.name}.{self.name}\" Disconnected")
        else:
            print(f"Slate \"{self.snorkel.name}.{self.name}\" Connected")

    async def recv_slate(self):
        while True:
            try:
                recv = await asyncio.wait_for(self.udp_sock.recvfrom(), timeout=1.0)
                message, _ = recv
            except Exception as e:
                await self.connect()
                continue

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

    async def set_field(self,channel,value):
        channel_meta = self.metaslate["channels"][channel]
        msg = cmd_pb2.Message()
        msg.set_field.SetInParent()
        msg.set_field.hash = self.hash
        msg.set_field.offset = channel_meta["offset"]

        if channel_meta["type"] == "int16_t":
            msg.set_field.data_int16 = int(value)
        elif channel_meta["type"] == "bool":
            msg.set_field.data_bool = int(value)
        elif channel_meta["type"] == "uint32_t":
            msg.set_field.data_uint32 = int(value)
        elif channel_meta["type"] == "float":
            msg.set_field.data_float = float(value)
        else:
            print("don't know how to write!")

        try:
            await asyncio.wait_for(self.snorkel.write_cmd(msg), timeout=1.0)
        except Exception as e:
            print(repr(e))
            print('Failed to Send')

    async def fetch_metaslate(self):
        print(f"Requesting metaslate for slate \"{self.name}\" ({hex(self.hash)})")
        self.metaslate = await self.snorkel.query_metaslate(self.hash)
        print(f"Received valid metaslate for slate \"{self.name}\" ({hex(self.hash)}), describing {len(self.metaslate['channels'])} channels")

    async def start_udp(self,port):
        print(f"Requesting UDP feed of slate \"{self.name}\" ({hex(self.hash)}) to {port}")
        await self.snorkel.request_udp_stream(self.hash,port)


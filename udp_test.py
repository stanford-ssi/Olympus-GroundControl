
import socket
import json
import asyncio 
import asyncudp
 
localPort   = 8000

bufferSize  = 10_000

    
async def udp_loop():
    # udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    udp_socket = await asyncudp.create_socket(local_addr=("0.0.0.0", localPort))

    # udp_socket.bind((localIP, localPort))
    # udp_socket.setblocking(False)
    print("UDP server up and listening")

    while(True):
        # message, _ = udp_socket.recvfrom(bufferSize)
        message, addr = await udp_socket.recvfrom()
        
        try:
            json_object = json.loads(message)
        except ValueError:
            print("Invalid JSON")
            pass # invalid json
        else:
            print("Message from Client: ", json_object)
            print()

async def print_loop():
    i = 0
    while True:
        print("test", i)
        i += 1
        await asyncio.sleep(1)

async def main():
    task1 = asyncio.create_task(print_loop())
    task2 = asyncio.create_task(udp_loop())
    await task2
    await task1

if __name__ == "__main__":
    asyncio.run(main())
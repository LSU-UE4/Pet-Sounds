import argparse
import random
import time

from pythonosc import udp_client

NUM_SENT = 60

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="127.0.0.1",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=5005,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)

  for x in range(NUM_SENT):
    randx = random.randrange(50,550,1)
    randy = random.randrange(50,550,1) - 50;
    randy = int(randx/100 + 1)
    print(str(randx) + " " + str(randy))
    client.send_message("/filter", randx)
    client.send_message("/filter", randy)
    time.sleep(1)
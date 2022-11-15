from server_impl.server import Server
import json
import sys

def main():
    with open("config.json") as config_file:
        config = json.load(config_file)
    # Host and Port
    if len(sys.argv) == 3:
        host, port = sys.argv[1], int(sys.argv[2])
    else:
        host = config["host"]
        port = config["port"]

    # Initialize the server
    server = Server(host, port, config)
    # Loop ...
    server.loop()

if __name__ == "__main__":
    main()

from MC_Random.client_MC_random import Agent
from MC_Random import HOST, PORT


def main():
    agt = Agent(HOST, PORT)
    agt.run()


if __name__ == "__main__":
    main()
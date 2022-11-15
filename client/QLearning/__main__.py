from QLearning.client_QL import Agent
from QLearning import HOST, PORT


def main():
    agt = Agent(HOST, PORT)
    agt.run()


if __name__ == "__main__":
    main()
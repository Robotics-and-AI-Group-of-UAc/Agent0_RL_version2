from MC_FirstVisit.client_MC_FirstVisit import Agent
from MC_FirstVisit import HOST, PORT

def main():
    agt = Agent(HOST,PORT)
    agt.run()


if __name__ == "__main__":
    main()
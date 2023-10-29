### This is a program that stores the infromation and trade history of a set
###     of stocks and provides suggestions on future trades base on several
###     trading strategies.


import src.runner
from src.runner import Runner

if __name__ == "__main__":
    runner = Runner("configs.json")
    runner.run()
    runner.save_data()
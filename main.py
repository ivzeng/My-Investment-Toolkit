### This is a program that stores the infromation and trade history of a set
###     of stocks and provides suggestions on future trades base on several
###     trading strategies.


from src.runner import Runner
from src.data_processing.my_json import MyJson

if __name__ == "__main__":
    my_json = MyJson()
    runner = Runner("configs.json", my_json)
    runner.run()
    runner.save_data()
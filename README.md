# This is my investment journal program.

### The program provides a simple user interface that allow you to
-   use a menu based interface for easy io operations
-   handle multiple accounts
-   record the account information and trading history
-   request stock data from internet
-   visualize the stock data as well as some other account information
-   obtain suggestion from various trading strategies

### TODO:
-   enable simulations that test the effectiveness for each trading strategy
-   develop better strategies with statistical learning and forecasting
-   add improved user interfaces for better user experience (consider using ncurses or some GUI tools)


###     Requirement:
####    Python > 3.7
####    Libraries:
```
matplotlib==3.7.1
pandas==2.0.3
Requests==2.31.0
```

for linux environment:
```
PyQt5==5.15.10
PyQt5_sip==12.13.0
```

### Demo:

####    Startup
![Startup](./demo/startup.png)

####    Get helps

![help](./demo/help_1.png)
![help](./demo/help_2.png)

####    View configuations and create/switch an account
![setting](./demo/set_details.png)
![new account](./demo/new_account.png)


####   Set account budget, transfer, add stock & make a trade
![set budget & transfer](./demo/set_budget_transfer.png)
![add & trade](./demo/add_trade.png)


####    Undo & remove a stock
![undo](./demo/undo.png)
![remove](./demo/remove.png)


####    Plot stock price
![plot](./demo/plot.png)


####    Get suggestion
![suggestion](./demo/suggestion1.png)
![suggestion](./demo/suggestion2.png)


#### Ivan Zeng ;)

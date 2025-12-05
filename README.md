# Windows-Time-Command
This is the Time Command in Winodws inspired by Linux and added extra functionality  like plotting, live analyze and writing reports to csv.


## Setup Instructions

### Clone project

```sh
git clone https://github.com/AminJml81/Windows-Time-Command.git
```

### Installing Prerequisites

```sh
pip install -r requirements.txt
```

## Simple Run 
```
python main.py
```

### flags(switches)(args)
<img width="1207" height="337" alt="flags" src="https://github.com/user-attachments/assets/621e5e23-dd2f-454a-acc8-fcf89e389ecd" />

### execution examples
```
python main.py -p explorer.exe -i 1
```
this code monitors the first explorer.exe process found and analyze it each 1 second until the user quit.
<img width="830" height="326" alt="execution1" src="https://github.com/user-attachments/assets/296baad3-4ba7-4714-bb1d-2bf2bdc1020d" />

```
python main.py -p explorer.exe -l
```
<img width="455" height="110" alt="execution1 1" src="https://github.com/user-attachments/assets/2e83f5b8-74bf-4e78-8dcd-d93b6b49fa46" />

```
python main.py -p explorer.exe -i 1 -id 5192 --csv reports.csv
```
this code does the same as previous example, plus it writes the results in reports.csv file
<img width="970" height="333" alt="execution2" src="https://github.com/user-attachments/assets/78a1c77a-b264-4d87-bf3f-6586c0e79084" />


```
python main.py -p explorer.exe -i 1 -id 5192 --csv reports.csv -g
```
this code does the same as previous example, plus it opens a plot file which plot the parameters live.
<img width="1248" height="805" alt="execution3" src="https://github.com/user-attachments/assets/319e39d8-bd31-41d0-a8c5-7dadd34eab33" />

```
python main.py -p explorer.exe -i 1 -id 5192 --csv reports.csv -g -t 10
```
this code does the same as previous example, plus it analyze it within 10 seconds.



# MultiCrawler
Get SETI user's anonymous information (Multiprocessing)

# Prerequests(Python3):
- bs4
- csv
- lxml
- requests
- multiprocessing

# Usage:
### Edit the SETICrawler.py to config:
- UIDs: User ID range that you would like to obtain
- N_PROCESS: The number of processes for multiprocessing
- OUT_FILE_NAME: Output csv file name and path
### Run the program:
- On Ubuntu: python3 SETICrawler.py
- On Ubuntu(in background): nohup python3 SETICrawler.py &
### Output:
- stdout/nohup.out: a list of User IDs that has been covered
- XXXX.csv: the obtained user information

import os
from trello import TrelloClient

client = TrelloClient(
    api_key = os.getenv('TRELLO_API_KEY'),
    api_secret = os.getenv('TRELLO_API_TOKEN'),
)

all_boards = client.list_boards()
last_board = all_boards[-1]
print(last_board.name)

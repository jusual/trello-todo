import os
from operator import attrgetter
from datetime import date, timedelta, datetime
from random import randint, sample
from trello import TrelloClient

client = TrelloClient(
    api_key = os.getenv('TRELLO_API_KEY'),
    api_secret = os.getenv('TRELLO_API_TOKEN'),
)


def find_last_date(board):
    all_lists = board.get_lists("open")
    last_list = all_lists[0]

    #TODO check for lists that are not either "Free" or in right date format
    if last_list.name == "Free":
        last_date = datetime.today() - timedelta(days=1)
    else:
        last_date = datetime.strptime(last_list.name, "%a, %d %B")
        last_date = last_date.replace(year=(datetime.today().year))

    return last_date


def create_random_list(board):
    length = randint(2, 4)
    due_date = datetime.today() + timedelta(days=length-1)
    random_list = board.add_list(due_date.strftime("%a, %d %B"))

    return random_list, length


#       effort  impact
# high  red     purple
# low   green   blue
#
# 1 high effort = 3 low effort
# day = 3 points
#
# high impact first
#
# TODO implement priority:
# low effort high impact
# high effort high impact
# low effort low impact
# high effort low impact

def list_switch(color, points, cards, list_id):
    for card in cards:
        if points <= 0:
            return points

        colors = [label.color for label in card.labels]
        if color in colors:
            # high effort tasks worth 3 points
            if "red" in colors and points >= 3:
                card.change_list(list_id)
                points -= 3
                print(card.name, 3)
            elif points >= 1:
                card.change_list(list_id)
                points -= 1
                print(card.name, 1)

    return points


def assign_tasks(length, free_list, random_list):
    cards = free_list.list_cards()
    for card in cards:
        for label in sorted(card.labels, key=attrgetter('color')):
            print(label.color)

    # spend 3 effort points in a day
    points = length * 3
    print(points)

    shuffled_cards = sample(cards, len(cards))

    # check high impact fisrt
    points = list_switch("purple", points, shuffled_cards, random_list.id)
    points = list_switch("blue", points, shuffled_cards, random_list.id)

    return points


#TODO choose board better
all_boards = client.list_boards()
board = all_boards[-1]

last_date = find_last_date(board)

if (datetime.today() > last_date):
    #TODO move tasks that are left from due date back to free

    (random_list, length) = create_random_list(board)

    #TODO find free list by name
    free_list = board.get_lists("open")[-1]
    points = assign_tasks(length, free_list, random_list)

#TODO make list of finished tasks
import os
import argparse
from operator import attrgetter
from datetime import date, timedelta, datetime
from random import randint, sample, choice
from trello import TrelloClient

#TODO add dependent tasks (can be included in current sprint only if previous or dependent tasks were completed)

client = TrelloClient(
    api_key = os.getenv('TRELLO_API_KEY'),
    api_secret = os.getenv('TRELLO_API_TOKEN'),
)

def handle_hobby_card(board, card):
    all_lists = board.get_lists("open")
    hobby_list = next(filter(lambda x: x.name == "Hobby", all_lists))
    hobby_card = choice([x for x in hobby_list.list_cards() if not x.name.startswith('---')])
    card.attach(url=hobby_card.short_url)

# Find non-expired list

def need_new_list(board):
    all_lists = board.get_lists("open")

    for last_list in all_lists:
        try:
            list_date = datetime.strptime(last_list.name, "%a, %d %B '%y").date()

            if (list_date >= date.today()):
                return False

        except ValueError:
            pass

    return True


def create_random_list(board):
    length = randint(2, 4)
    due_date = datetime.today() + timedelta(days=length-1)
    random_list = board.add_list(due_date.strftime("%a, %d %B '%y"))

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

def list_switch(board, color, points, cards, list_id):
    for card in cards:
        if points <= 0:
            return points

        if card.name == "hobby":
            handle_hobby_card(board, card)

        colors = [label.color for label in card.labels]
        if color in colors:
            # high effort tasks worth 3 points
            if "red" in colors and points >= 3:
                card.change_list(list_id)
                points -= 3
            elif points >= 1:
                card.change_list(list_id)
                points -= 1

    return points


def assign_tasks(board, length, free_list, random_list):
    cards = free_list.list_cards()

    # spend 3 effort points in a day
    points = length * 3

    shuffled_cards = sample(cards, len(cards))

    # check high impact fisrt
    points = list_switch(board, "purple", points, shuffled_cards, random_list.id)
    points = list_switch(board, "blue", points, shuffled_cards, random_list.id)

    return points

#TODO remake need_new_list to rely on cleaning expired first
def clean_expired_lists(board, free_list, need_refresh):
    for last_list in all_lists:
        try:
            list_date = datetime.strptime(last_list.name, "%a, %d %B '%y").date()

            if (list_date < date.today() or need_refresh):
                for card in last_list.list_cards():
                    #TODO find better way to check if the task is done
                    if card.member_id:
                        card.change_list(free_list.id)
                    else:
                        card.set_closed(True)

                last_list.close()

        except ValueError:
            pass


# start of main code
#TODO put separately

parser = argparse.ArgumentParser(prog='trello-todo')
parser.add_argument('-r', '--refresh', action='store_true', help='create new todo list')

args = parser.parse_args()

#TODO choose board better
all_boards = client.list_boards()
board = all_boards[-1]

all_lists = board.get_lists("open")
free_list = next(filter(lambda x: x.name == "Free", all_lists))

# for all expired lists:
#   put unfulfilled tasks back to the Free list, archive? everything left
# if refresh is selected, do that to all dated lists
clean_expired_lists(board, free_list, args.refresh)

if (need_new_list(board)):
    (random_list, length) = create_random_list(board)
    points = assign_tasks(board, length, free_list, random_list)

#TODO make list of finished tasks

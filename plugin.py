from plugin_base import *
from base import *


@Prelaunch()
def record_starting_state():
    """
    This method looks at the trello board and records its state in a local file.
    This allows us to react to changes in it with triggers.
    """
    recordStateToFile('state.json')


@Trigger(name="Trello: Any board created", description="Fires when a new board is created",
         generated_arg_types=['board:str|[str]|none'])
def board_created_trigger():
    """
    This will fire when a new trello board is detected.
    :return: The json {'fire': 'true', 'board': <boardName>} or {'fire': 'false'}
             If there is more than one board difference, the 'board_name' will be an array of board_names.
    """

    # Check the current state and how it compares to the last saved one
    now_json = getJsonState(depth=0)
    loaded_json = loadJsonFromFile('state.json')

    names = [y['name'] for y in loaded_json]
    extra = [x for x in now_json if x['name'] not in names]

    if len(extra) > 0:
        # We do have a board, so we want to fire
        board_names = [x['name'] for x in extra]
        recordStateToFile('state.json')  # We want to update the file so we only fire once
        if len(board_names) > 1:
            print(json.dumps({'fire': 'true', 'board': board_names}))
        else:
            print(json.dumps({'fire': 'true', 'board': board_names[0]}))
    else:
        if len(now_json) != len(loaded_json):
            # Even though we have no new boards, let's update our state now.
            recordStateToFile('state.json')
        print(json.dumps({'fire': 'false'}))


@Trigger(name="Trello: Specific board(s) created",
         description="Fires when a specific board (or multiple boards) is/are created",
         required_arg_types=['board_name:str|[str]'], generated_arg_types=['board:str|[str]|none'])
def spec_board_created_trigger(board_name):
    """
    This will fire when a new trello board is detected that matches our specified parameters
    :return: The json {'fire': 'true'} or {'fire': 'false'}
    """

    if isinstance(board_name, list):
        matching = board_name
    else:
        # Presume it is a string
        matching = [board_name]

    # Check the current state and how it compares to the last saved one
    now_json = getJsonState(depth=0)
    loaded_json = loadJsonFromFile('state.json')

    names = [y['name'] for y in loaded_json]
    extra = [x for x in now_json if x['name'] not in names and x['name'] in matching]

    if len(extra) > 0:
        # We do have a board, so we want to fire
        board_names = [x['name'] for x in extra]
        recordStateToFile('state.json')  # We want to update the file so we only fire once
        if len(board_names) > 1:
            print(json.dumps({'fire': 'true', 'board': board_names}))
        else:
            print(json.dumps({'fire': 'true', 'board': board_names[0]}))
    else:
        if len(now_json) != len(loaded_json):
            # Even though we have no new boards, let's update our state now.
            recordStateToFile('state.json')
        print(json.dumps({'fire': 'false'}))


@Action(name="Trello: Create board(s)", description="Create a board on Trello",
        required_arg_types=['board_names:str|[str]', 'permissions:str|[str]|none'])
def create_board_action(board_names, permissions=None):
    """
    Fire this action to create one or more boards on trello
    :param board_names: One or more string indicating the titles of the boards to create
    :param permissions: One or more string indicating permission level. Defaults to private if not supplied. Must be of
                        the same length as board_names.
    """

    perm = None
    if isinstance(board_names, list):
        names = board_names
        if permissions:
            perm = permissions
    else:
        names = [board_names]
        if permissions:
            perm = [perm]

    client = createClient()
    if perm:
        for name, p in zip(names, perm):
            client.add_board(name, permission_level=p)
        recordStateToFile('state.json')
        print(json.dumps({}))
    else:
        for name in names:
            client.add_board(name)
        recordStateToFile('state.json')
        print(json.dumps({}))


@Action(name="Trello: Does board exist?", description="Return whether or not a board exists",
        required_arg_types=['board_name:str'], generated_arg_types=['exists:bool'])
def does_board_exist_action(board_name):
    """
    This action determines whether a given board exists or not.
    :param board_name: The board's name as a string
    :return: {'exists': True} if it does and {'exists': False} if not
    """
    client = createClient()

    for b in client.list_boards():
        if b.name == board_name:
            print(json.dumps({"exists": True}))
            return

    print(json.dumps({"exists": False}))

@Action(name="Trello: Does list exist?", description="Return whether or not a particular list exists",
        required_arg_types=['board_name:str', 'listname:str'], generated_arg_types=['exists:bool'])
def does_list_exist_action(board_name, listname):
    """
    This action determines whether a given list exists or not.
    :param board_name: The board's name as a string
    :param listname: The list's name as a string
    :return: {'exists': True} if it does and {'exists': False} if not
    """
    client = createClient()

    for b in client.list_boards():
        if b.name == board_name:
            for list in b.list_lists():
                if list.name == listname:
                    print(json.dumps({"exists": True}))
                    return

    print(json.dumps({"exists": False}))

@Action(name="Trello: Does card exist?", description="Return whether or not a particular card exists",
        required_arg_types=['board_name:str', 'listname:str', 'cardname:str'], generated_arg_types=['exists:bool'])
def does_card_exist_action(board_name, listname, cardname):
    """
    This action determines whether a given card exists or not.
    :param board_name: The board's name as a string
    :param listname: The list's name as a string
    :param cardname: The card's name as a string
    :return: {'exists': True} if it does and {'exists': False} if not
    """
    client = createClient()

    for b in client.list_boards():
        if b.name == board_name:
            for list in b.list_lists():
                if list.name == listname:
                    for card in list.list_cards():
                        if card.name == cardname:
                            print(json.dumps({"exists": True}))
                            return

    print(json.dumps({"exists": False}))

@Action(name="Trello: Get link to board", description="Get a url for a given trello board",
        required_arg_types=['board_name:str'], generated_arg_types=['link:str'])
def get_link_for_board_action(board_name):
    """
    Obtains a link to the given board, presuming it exists.
    :param board_name: The board's name as a string
    :return: {'link': <url>} or {'link': 'notfound'} if the board does not exist.
    """
    client = createClient()

    for b in client.list_boards():
        if b.name == board_name:
            print(json.dumps({'link': 'https://trello.com/b/' + b.id}))
            return

    print(json.dumps({'link': 'notfound'}))


@Action(name="Trello: Get link to card", description="Get a url for a card given its board and list",
        required_arg_types=['board_name:str', 'listname:str', 'cardname:str'], generated_arg_types=['link:str'])
def get_link_for_card_action(board_name, listname, cardname):
    """
    Obtains a link to the specified card
    :param board_name: The name of the board the card is in
    :param listname: The name of the list the card is under
    :param cardname: The name of the card
    :return: {'link': <url>} or {'link': 'notfound'} if the board does not exist.
    """
    client = createClient()

    for b in client.list_boards():
        if b.name == board_name:
            for l in b.list_lists():
                if l.name == listname:
                    for c in l.list_cards():
                        if c.name == cardname:
                            print(json.dumps({'link': 'https://trello.com/c/' + c.id}))
                            return
    print(json.dumps({'link': 'notfound'}))


@Action(name="Trello: Create comment on card", description="Given the path to a card, make a comment there.",
        required_arg_types=['board_name:str', 'listname:str', 'cardname:str', 'comment_string:str'])
def make_comment_on_card_action(board_name, listname, cardname, comment_string):
    """
    Obtains a link to the specified card
    :param board_name: The name of the board the card is in
    :param listname: The name of the list the card is under
    :param cardname: The name of the card
    """
    client = createClient()

    for b in client.list_boards():
        if b.name == board_name:
            for l in b.list_lists():
                if l.name == listname:
                    for c in l.list_cards():
                        if c.name == cardname:
                            c.comment(comment_string)
                            print(json.dumps({}))
                            return

    print(json.dumps({}))


@Action(name="Trello: Add label to card", description="Given the path to a card, add a label to it.",
        required_arg_types=['board_name:str', 'listname:str', 'cardname:str', 'label_string:str'])
def add_label_on_card_action(board_name, listname, cardname, label_string):
    """
    Adds a label to a specified card
    :param board_name: The name of the board the card is in
    :param listname: The name of the list the card is under
    :param cardname: The name of the card
    """
    client = createClient()

    for b in client.list_boards():
        if b.name == board_name:
            chosen_label = None
            for lab in b.get_labels():
                if lab.name == label_string:
                    chosen_label = lab
                    break
            if chosen_label is None:
                continue
            for l in b.list_lists():
                if l.name == listname:
                    for c in l.list_cards():
                        if c.name == cardname:
                            c.add_label(chosen_label)
                            print(json.dumps({}))
                            return

    print(json.dumps({}))


@Action(name="Trello: Get labels on card", description="Given the path to a card, get the labels on it.",
        required_arg_types=['board_name:str', 'listname:str', 'cardname:str'],
        generated_arg_types=['labels:str|[str]|none'])
def get_label_on_card_action(board_name, listname, cardname):
    """
    Get all labels attached to a specified card
    :param board_name: Name of the board the card is in
    :param listname: Name of the list the card is in
    :param cardname: Name of the card
    :return: {'labels': <label>} if the card is found, otherwise {'labels': none}
    """
    client = createClient()

    for b in client.list_boards():
        if b.name == board_name:
            board_labels = b.get_labels()
            if board_labels is None:
                continue
            for l in b.list_lists():
                if l.name == listname:
                    for c in l.list_cards():
                        if c.name == cardname:
                            labels = [x.name for x in (c.labels if c.labels else [])]
                            if len(labels) == 1:
                                labels = labels[0]
                            print(json.dumps({'labels': labels}))
                            return

    print(json.dumps({}))


@Action(name="Trello: Set item on card checklist", description="Mark a given item on a checklist on or off.",
        required_arg_types=['board_name:str', 'listname:str', 'cardname:str', 'checklist:str', 'item:str',
                            'onoff:bool|none'])
def check_item_card_checklist_action(board_name, listname, cardname, checklist, item, onoff=None):
    """
    Sets a checklist item to a given value on a card
    :param board_name: The board the card is in
    :param listname: The list the card is in
    :param cardname: The card
    :param checklist: The name of the checklist
    :param item: The item we're targeting
    :param onoff: Whether it should be turned on or off. Defaults to on if not supplied
    """

    client = createClient()

    check_on = True
    if onoff is not None:
        check_on = onoff

    for b in client.list_boards():
        if b.name == board_name:
            board_labels = b.get_labels()
            if board_labels is None:
                continue
            for l in b.list_lists():
                if l.name == listname:
                    for c in l.list_cards():
                        if c.name == cardname:
                            for check in c.checklists:
                                if check.name == checklist:
                                    check.set_checklist_item(item, check_on)
                            print(json.dumps({}))
                            return

    print(json.dumps({}))


@Action(name="Trello: Remove item on card checklist", description="Remove a given item from a checklist",
        required_arg_types=['board_name:str', 'listname:str', 'cardname:str', 'checklist:str', 'item:str'])
def remove_item_card_checklist_action(board_name, listname, cardname, checklist, item):
    """
    Remove a checklist item from a card
    :param board_name: The board the card is in
    :param listname: The list the card is in
    :param cardname: The card
    :param checklist: The name of the checklist
    :param item: The item we're targeting
    """

    client = createClient()

    for b in client.list_boards():
        if b.name == board_name:
            board_labels = b.get_labels()
            if board_labels is None:
                continue
            for l in b.list_lists():
                if l.name == listname:
                    for c in l.list_cards():
                        if c.name == cardname:
                            for check in c.checklists:
                                if check.name == checklist:
                                    check.delete_checklist_item(item)
                            print(json.dumps({}))
                            return

    print(json.dumps({}))


@Action(name="Trello: Add item on card checklist", description="Add an item to a given checklist",
        required_arg_types=['board_name:str', 'listname:str', 'cardname:str', 'checklist:str', 'item:str',
                            'checked:bool|none'])
def add_item_card_checklist_action(board_name, listname, cardname, checklist, item, checked=False):
    """
    Add a checklist item to a card
    :param board_name: The board the card is in
    :param listname: The list the card is in
    :param cardname: The card
    :param checklist: The name of the checklist
    :param item: The item we're targeting
    :param checked: Whether it should be turned on or off. Defaults to off if not supplied.
    """

    client = createClient()

    check_on = False
    if checked is not None:
        check_on = checked

    for b in client.list_boards():
        if b.name == board_name:
            board_labels = b.get_labels()
            if board_labels is None:
                continue
            for l in b.list_lists():
                if l.name == listname:
                    for c in l.list_cards():
                        if c.name == cardname:
                            for check in c.checklists:
                                if check.name == checklist:
                                    check.add_checklist_item(item, checked)
                            print(json.dumps({}))
                            return

    print(json.dumps({}))


@Action(name="Trello: Add checklist to card", description="Add a new checklist to a card",
        required_arg_types=['board_name:str', 'listname:str', 'cardname:str', 'checklist:str'])
def add_checklist_to_card_action(board_name, listname, cardname, checklist):
    """
    Add a checklist to a given card
    :param board_name: The board the card is in
    :param listname: The list the card is in
    :param cardname: The card
    :param checklist: The name of the checklist
    """

    client = createClient()

    for b in client.list_boards():
        if b.name == board_name:
            board_labels = b.get_labels()
            if board_labels is None:
                continue
            for l in b.list_lists():
                if l.name == listname:
                    for c in l.list_cards():
                        if c.name == cardname:
                            c.add_checklist(checklist, [])
                            print(json.dumps({}))
                            return

    print(json.dumps({}))


@Action(name="Trello: Create label", description="Creates a new label for a given board",
        required_arg_types=['board_name:str', 'color:str', 'name:str'])
def create_label_action(board_name, color, name):
    """
    Creates a new label with the given parameters
    :param board_name: The board the card is in
    :param color: the color, either green, yellow, orange
            red, purple, blue, sky, lime, pink, or black
    :param name: The name of the label
    """

    client = createClient()

    for b in client.list_boards():
        if b.name == board_name:
            b.add_label(name, color)
            print(json.dumps({}))
            return

    print(json.dumps({}))

#does_card_exist_action('Suave - Flow Code', 'Plugins', 'TrelloPlugin TODO')
#does_card_exist_action('Suave - Flow Code', 'Plugins', 'TrelloPlugin TODdafO')
# add_checklist_to_card_action('Suave - Flow Code', 'Plugins', 'TrelloPlugin TODO', 'Automation checklist')
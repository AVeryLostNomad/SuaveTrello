import os.path
from trello import TrelloClient
import json

def getKey(val):
	with open('keys.txt', 'r') as f:
		try:
			lines = f.readlines()
			for line in lines:
				parts = line.split('=')
				if parts[0] == val:
					return parts[1][1:-2]
		except Exception as e:
			return None
	return None

# print(getKey('api_key'))
# print(getKey('api_secret'))

def createClient():
	token = getKey('token')
	if token != '' and token != 'your-oauth-token-key':
		return TrelloClient(
			api_key=getKey('api_key'),
			api_secret=getKey('api_secret'),
			token=token,
			token_secret=getKey('token_secret')
		)
	return TrelloClient(
		api_key=getKey('api_key'),
		api_secret=getKey('api_secret')
	)

def getBoardByName(name):
	client = createClient()

	for board in client.list_boards():
		if board.name == name:
			return board
	return None

def getJsonState(depth=None):
	client = createClient()

	total_json = []

	for board in client.list_boards():
		json_obj = {
			'name': board.name,
			'id': board.id,
			'lists': [],
			'closed': board.closed
		}
		if depth is None or depth >= 1:
			for list in board.list_lists():
				list_obj = {
					'name': list.name,
					'closed': list.closed,
					'id': list.id,
					'cards': []
				}
				if depth is None or depth >= 2:
					for card in list.list_cards():
						card_obj = {
							'name': card.name,
							'description': card.description,
							'attachments': card.attachments,
							'badges': card.badges,
							'closed': card.closed,
							'creation_date': card.card_created_date.strftime('%c'),
							'last_activity': card.date_last_activity.strftime('%c'),
							'idmembers': card.idMembers,
							'labels': [],
							'checklists': [],
							'comments': []
						}
						if depth is None or depth >= 3:
							for label in (card.labels if card.labels else []):
								label_obj = {
									'name': label.name,
									'color': label.color,
									'id': label.id
								}
								card_obj['labels'].append(label_obj)
							for checklist in (card.checklists if card.checklists else []):
								check_obj = {
									'name': checklist.name,
									'id': checklist.id,
									'items': []
								}
								if depth is None or depth >= 4:
									for item in (checklist.items if checklist.items else []):
										item_obj = {
											'name': item['name'],
											'checked': item['checked']
										}
										check_obj['items'].append(item_obj)
								card_obj['checklists'].append(check_obj)
							for comment in (card.comments if card.comments else []):
								card_obj['comments'].append(comment)
						list_obj['cards'].append(card_obj)
				json_obj['lists'].append(list_obj)
		total_json.append(json_obj)

	return total_json

def recordStateToFile(filepath):
	total_json = getJsonState()

	with open(filepath, 'w+') as f:
		f.write(json.dumps(total_json))

def loadJsonFromFile(filepath):
	with open(filepath, 'r') as f:
		return json.loads(f.readline())
import vk_api, time

auth_vk = vk_api.VkApi(token='8822d5a01ce498eb6eb9885e05196b23ecc01a88afa86c187eaf443de9a3e2dd5d4e886b7db597b999f7a')


values = {'out': 0, 'count': 100, 'time_offset': 60}
responce = auth_vk.method('messages.get', values)


def write_msg(user_id, s):
    auth_vk.method('messages.send', {'user_id': user_id, 'message': s})

while True:
    responce = auth_vk.method('messages.get', values)
    if responce['items']:
        values['last_message_id'] = responce['items'][0]['id']
    for items in responce['items']:
        if responce['items'][0]['body'] == 'Привет':   
            write_msg(items['user_id'], 'Привет, человек')
        else:
            write_msg(items['user_id'], 'Я тебя не понимаю')
    time.sleep(1)
    

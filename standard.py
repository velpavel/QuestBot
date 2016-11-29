from telebot import types

start_quest_command = ['найти квест', ]
add_quest_command = ['add_quest', 'добавить квест']

def standard_keyboard(user_id=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #@!Так не работает markup.row не принимает словарь.
    # for row_commands in [russia_commands, regions_commands]:
    #     row=[]
    #     for c in row_commands:
    #         row.append(types.KeyboardButton(c.capitalize()))
    #     print(row)
    #     markup.row(row)
    markup.row(*start_quest_command)
    return markup
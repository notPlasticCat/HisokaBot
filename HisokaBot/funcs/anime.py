import requests
from HisokaBot.helpers.constants import ANILIST_GRAPHQL_URI, searchAnime, ANIME_STR
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import CallbackQueryHandler, CallbackContext
from HisokaBot import dp

user_anime_dict = {}


def search_anime(name):
    name = {
        'search': name,
        'page': 1,
        'perPage': 5,
        'type': 'ANIME'
    }
    r = requests.post(ANILIST_GRAPHQL_URI, json={'query': searchAnime, 'variables': name}).json()
    return r['data']['Page']['media']


def anime(update: Update, context: CallbackContext, name):
    data = search_anime(name)
    user = update.effective_user
    user_anime_dict[user.id] = data
    no_of_buttons = len(data)
    btn_list = []
    for i in range(no_of_buttons):
        btn_list.append(
            [
                InlineKeyboardButton(
                    text=data[i]['title']['english'] if data[i]['title']['english'] else data[i]['title']['romaji'],
                    callback_data=f"animesearch_{i}_{user.id}")
            ]
        )
    update.message.reply_text(text="Your Search Result(s) :", reply_markup=InlineKeyboardMarkup(btn_list))


def anime_when_clicked(update: Update, context: CallbackContext):
    query = update.callback_query
    match = query.data.split('_')  # match[0] = anime, match[1] = the anime's serial no., match[2] = user_id
    s_no = int(match[1])
    user = update.effective_user
    if user.id != int(match[2]):
        query.answer(text="Not allowed!", show_alert=True)
        return -1
    query.answer("Wait..")
    query.message.delete()
    data = user_anime_dict[int(match[2])][s_no]
    caption = ANIME_STR.format(
        data['title']['english'],
        data['title']['romaji'],
        data['title']['native'],
        f"https://img.anili.st/media/{data['id']}",
        data['type'],
        ', '.join(data['genres']),
        data['status'],
        data['episodes'],
        data['meanScore'],
        data['averageScore'],
        data['duration'],
        ', '.join([data['studios']['nodes'][i]['name'] for i in range(len(data['studios']['nodes']))]),
        f"{data['startDate']['day']}-{data['startDate']['month']}-{data['startDate']['year']}",
        ', '.join(data['tags'][i]['name'] for i in range(len(data['tags']))),
        data['description'])
    caption = caption.replace('<b>', '*').replace('</b>', '*'). \
        replace('<pre>', '`').replace('</pre>', '`'). \
        replace('<i>', '`_').replace('</i>', '_`'). \
        replace('<br>', '\n').replace('.', '\\.'). \
        replace('(', '\\(').replace(')', '\\)'). \
        replace(f"\(https://img\.anili\.st/media/{data['id']}\)",
                f"(https://img\.anili\.st/media/{data['id']})"). \
        replace("None", "").replace("-", "\-")
    #    print(caption)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=caption,
                             parse_mode=ParseMode.MARKDOWN_V2,
                             reply_markup=InlineKeyboardMarkup(
                                 [
                                     [InlineKeyboardButton('More Information', url=data['siteUrl'])],
                                 ]
                             ))


dp.add_handler(CallbackQueryHandler(anime_when_clicked, pattern=r"animesearch_"))
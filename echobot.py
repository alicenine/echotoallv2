from telethon import TelegramClient, events
from telethon.tl.custom import Button
import json
from urllib.request import urlopen 
from urllib.parse import urlencode
from LiteSQL import lsql
from time import time
import asyncio

condition = asyncio.Condition()

sql = lsql("echo")
try:
    a = sql.select_data("1", "id")
except:
    sql.create("id, time, anon, podp, podpanon, mess, deanon")
    sql.insert_data([(0, 0, 0, 0, "0", "", 0)], 7)

list_of_user = sql.get_all_data()

for i in range(len(list_of_user)):
    list_of_user[i] = list_of_user[i][0]

client = TelegramClient('echo', 
    "appid",
    "apphash").start(bot_token="токен") 

client.parse_mode = 'html'
def command(*args):
    return '|'.join([i for i in [
        rf'^\/({i})+(\@echoall2bot\w*(_\w+)*)?([ \f\n\r\t\v\u00A0\u2028\u2029].*)?$' for i in args
    ]])

async def new_user(user):
    if user not in list_of_user:
        sql.insert_data([(int(user), 0, 1, 0, str(user), "", 1)], 7)
        list_of_user.append(user)

async def echo_all(users, message, inline):
    for user in users:
        try:
            mess = await client.send_message(user, message, buttons=inline) 
            sql.edit_data("id", user, "mess", f"/{(mess).id}"+"/".join(sql.select_data(user, "id")[0][5].split("/")[:100]))
        except Exception as e:
            if str(e)[:31] in ["Could not find the input entity", "User is blocked (caused by Send", "The specified user was deleted "]:
                try:
                    sql.delete_data(user, "id")
                    list_of_user.pop(user)
                except: pass
            else:
                print(e, str(e)[:31])

class Telegraph:
    def make_request(method, **params):
        url = 'https://api.telegra.ph/' + method
        params = {k: v if isinstance(v, str) else json.dumps(v) for k, v in params.items()}
        r = json.loads(urlopen(url + '?' + urlencode(params)).read())
        if not r['ok']:
            raise ValueError(str(r))
        return r['result']

    def get_access_token(short_name):
        return Telegraph.make_request('createAccount',
            short_name=short_name)['access_token']
            
    def create_page(**params):
        return Telegraph.make_request('createPage', **params)

class Bot:
    @client.on(events.NewMessage())
    async def send(event):
        await new_user(event.from_id)
        Flag = False
        if event.message.message == "" or event.message.message.split()[0] not in [
"/start@echoall2bot", "/help@echoall2bot", "source@echoall2bot", "/menu@echoall2bot", "/edit@echoall2bot", "/del@echoall2bot",
"/start", "/help", "/source", "/menu", "/edit", "/del"
                                        ] and not event.message.out:
            us = sql.select_data(event.from_id, "id")[0]
            for i in ['href=', "дрочаг","@", "cheliizlead","dr04ag_bot","neareye", "dr04","dro4","mil_lana","raikirigamebot","https://", "(собачка)","(собака)","echoall3bot","менязовутмилана","мил_лана", "ссылканамойканал","llxeya","писатьвлс","statie","экскорт","http://", "t.me/", ".com", ".ru", "tg://"]:
                if i in event.message.text.replace(" ","").lower():
                    if us[3] != 0:
                        sql.edit_data("id", event.from_id, "podp", us[3]-1)
                        break
                    else:
                        await client.send_message(event.chat.id, "У тебя не осталось прав на отправку сообщений с сылками!\n\
купить безлимитное количество отправок сообщений с сылками можно за 30 руб у @Error_mak25")
                        Flag = True
            Flag2 = False
            for i in range(3, len(event.message.message), 3):
                if event.message.message.count(event.message.message[i-3:i]) > 7:
                    Flag2 = True
                    break
            if Flag2 or len(event.message.message) >= 2000:
                await client.send_message(event.chat.id, "Сообщение слишком большое (боллее 2000 символов) или содержит повторяющиеся элементы")
                Flag = True
            if not Flag:
                time1 = time()
                if int(us[1])+300 <= time1 or us[1] == 0:
                    sql.edit_data("id", event.from_id, "time", time1)
                    inline = []
                    if us[2] == 0:
                        inline.append(Button.inline(f"Autor: {us[4]}".replace("861999825", "ADMIN")))
                    if event.message.is_reply:
                        reply = await event.message.get_reply_message()
                        if len(f"n{reply.message}".encode("utf-8")) <= 64:
                            inline.append(Button.inline(f"{reply.message[:20]}...", f"n{reply.message}"))
                        else:
                            tok = Telegraph.get_access_token("bot")
                            link = Telegraph.create_page(access_token=tok, content=[{"tag": "p", "children": [reply.message]}], title="reply")
                            inline.append(Button.url(f"{reply.message[:20]}...", link["url"]))
                    if us[6]:
                        await client.send_message(861999825, str(event.from_id)) 
                    mess = await client.send_message(event.chat.id, "Ваше сообщение прошло проверку на рекламу и готово к отправке. Отправляем...")
                    if inline == []: inline = None 
                    t = time()
                    await echo_all(list_of_user, event.message, inline)
                    await mess.edit(f"Ваше сообщение было отправлено {len(list_of_user)} пользователям за {round(time()-t, 2)} секунд!")
                else:
                    await client.send_message(event.chat.id, f"Вы уже отправляли сообщение! Отправить следующее можно через {int((300 - time1 + int(us[1]))//60)}\
 минут(-у) {int((300 - time1 + int(us[1]))%60)} секунд(-ы).", reply_to=event.message)

    @client.on(events.NewMessage(pattern=command("start", "help")))
    async def start(event):
        await client.send_message(event.chat.id, "Обязательно внимательно прочитай <a href='https://telegra.ph/Polzovatelskie-soglashenie-07-31'>Пользовательское соглашение</a> перед началом использования бота\nПросто отправь мне сообщение\n/source - исходный код бота\n/menu - меню настроек")

    @client.on(events.CallbackQuery())
    async def callback(event):
        txt = event.data.decode("utf-8")
        user = await event.get_sender()
        await new_user(user.id)
        us = sql.select_data(user.id, "id")[0]
        if txt[0] == "a":
            if us[2] == 1:
                sql.edit_data("id", user.id, "anon", 0)
                await client.send_message(event.chat.id, "Теперь ваши сообщения будут подписываться вашим id")
            else:
                sql.edit_data("id", user.id, "anon", 1)
                await client.send_message(event.chat.id, "Теперь ваши сообщения НЕ будут подписываться вашим id, да вы Анонимус!")
        elif txt[0] == "s":
            if us[4][0].isdigit():
                sql.edit_data("id", user.id, "podpanon", user.username)
                await client.send_message(event.chat.id, "Теперь ваши сообщения будут подписываться вашим коротким именем, если вы не Анонимус")
            else:
                sql.edit_data("id", user.id, "podpanon", str(user.id))
                await client.send_message(event.chat.id, "Теперь ваши сообщения будут подписываться вашим id/коротким именем, если вы не Анонимус")
        elif txt[0] == "n":
            await event.answer(txt[1:], alert=True)
        elif txt[0] == "d":
            sql.edit_data("id", user.id, "deanon", (1 if us[6] == 0 else 0)
            await client.send_message(event.chat.id, f"Теперь вы {'не ' if us[6] == 1 else ' '}аноним") 
            
    @client.on(events.NewMessage(pattern=command("source")))
    async def source(event):
        await client.send_message(event.chat.id, "Ссылка на репозиторий - https://gitlab.com/Ma-Mush/echoall")

    @client.on(events.NewMessage(pattern=command("menu")))
    async def menu(event):
        await new_user(event.from_id)
        us = sql.select_data(event.from_id, "id")[0]
        await client.send_message(
            event.chat.id, "Меню настроек пользователя (для изменения - нажмите)",
            buttons=[
            [Button.inline(f"Вы {'Анонимус' if us[2] == 1 else 'не Анонимус'}", "a")],
            [Button.url(f"У вас {us[3]} доступных сообщений с сылкой (тап - купить безлимит)", "t.me/Error_mak25")],
            [Button.inline(f"Подпись в случае неанонимности (id/короткое имя) - {us[4]}", "s")], 
            [Button.inline(f"Админ {'не ' if us[6] == 0 else ' ' }видит ваше id, если вы отправили это сообщение", "d"]
                ]
        )

    @client.on(events.NewMessage(pattern=command("edit")))
    async def edit(event):
        if event.from_id == 861999825:
            txt = event.message.message.split()
            sql.edit_data(txt[1], int(txt[2]), txt[3], int(txt[4]))
            await client.send_message(861999825, f"{txt[1]}, {txt[2]}, {txt[3]}, {txt[4]}")
    
    @client.on(events.NewMessage(pattern=command("del")))
    async def delete(event):
        if event.from_id == 861999825 and event.message.is_reply:
            mess = (await event.message.get_reply_message()).id
            ids = sql.select_data(861999825, "id")[0][5].split("/")
            try:
                index = ids.index(mess)
            except:
                return 0
            for i in sql.get_all_data():
                try:
                    if len(i[5].split("/")) >= index:
                        await client.edit_message(i[0], int(i[5].split("/")[index]), f"Сообщение удалено по причине - {event.message.message.replace('/del ', '')}")
                    else:
                        continue
                except:
                    pass 
            await client.send_message(861999825, "все")

client.run_until_disconnected()

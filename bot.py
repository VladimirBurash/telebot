# -*- coding: utf-8 -*-
import config
import telebot,requests,datetime,aiohttp,asyncio,json


bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=["hello"])
def repeat_all_messages(message): # Название функции не играет никакой роли, в принципе
    bot.send_message(message.chat.id, 'Hi')

async def loading(messege):
    bot.send_message(messege.chat.id,'Loading...')

async def friends_ages(message):
    await loading(message)
    try:
        username = message.text.split(' ')[1]
    except:
        bot.send_message(message.chat.id,'Вы забыли ввести id пользователя')
        return 0
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.vk.com/method/users.get?user_ids="+username+"&fields=bdate&v=5.58") as resp:
            req_id = await resp.json()
            try:
                user_id = req_id['response'][0].get('id')
            except:
                bot.send_message(message.chat.id,'Такого пользователя не существует')
                return 0
            async with session.get("https://api.vk.com/method/friends.get?user_id="+str(user_id)+"&fields=bdate&v=5.58") as resp:
                req = await resp.json()
                count = req['response'].get('count')
                i = 0
                bArr = []
                while i < count:
                    bdate = req['response']['items'][i].get('bdate')

                    if bdate:
                        if len(bdate) > 5:
                            bdate = datetime.datetime.strptime(bdate, "%d.%m.%Y")
                            bArr.insert(i, bdate)
                    i += 1
                diag = [0 for i in range(150)]
                count1 = len(bArr)
                i = 0
                a = []
                while i < count1:
                    result = (datetime.datetime.today() - bArr[i]) / 365
                    result = str(result).split(' ')
                    j = int(result[0])
                    diag[j] += 1
                    i += 1

                i = 0
                cnt = len(diag)
                answer = [' ']
                while i < cnt:
                    if diag[i] != 0:
                        j = 0
                        answer.append(str(i))
                        answer.append('-')
                        while j < diag[i]:
                            answer.append(".")
                            j += 1
                        answer.append("\n")

                    i += 1
                bot.send_message(message.chat.id,' '.join(answer))

@bot.message_handler(commands=["friends_ages"])
def loop(message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Blocking call which returns when the display_date() coroutine is done
    loop.run_until_complete(friends_ages(message))
    loop.close()

if __name__ == '__main__':
    bot.polling()
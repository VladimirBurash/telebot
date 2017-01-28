# -*- coding: utf-8 -*-
import config
import telebot,datetime,aiohttp,asyncio


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
                            try:
                                bdate = datetime.datetime.strptime(bdate, "%d.%m.%Y")
                                bArr.insert(i, bdate)
                            except:
                                print('1')
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

async def group_ages(message):
    offset = 0
    await loading(message)
    try:
        groupname = message.text.split(' ')[1]
    except:
        bot.send_message(message.chat.id,'Вы забыли ввести id группы')
        return 0
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.vk.com/method/groups.getMembers?group_id="+groupname+"&offset="+str(offset)+"&fields=bdate&fields=bdate&v=5.58") as resp:
            req_id =  await resp.json()
            count = req_id['response'].get('count')
            loops= count/1000
            i = 0
            bArr=[]
            while i < loops:
                async with session.get("https://api.vk.com/method/groups.getMembers?group_id=" + groupname + "&offset=" + str(offset) + "&fields=bdate&fields=bdate&v=5.58") as resp:
                    j = 0
                    req = await resp.json()
                    if count-((i+1)*1000)>0:
                        con = 1000
                    else:
                        con = 1000-abs(count-(i+1)*1000)
                    while j < con:
                        bdate = req['response']['items'][j].get('bdate')
                        if bdate:
                            if len(bdate) > 5:
                                try:
                                    bdate = datetime.datetime.strptime(bdate, "%d.%m.%Y")
                                    bArr.insert(j, bdate)
                                    # bot.send_message(message.chat.id,bdate)
                                except:
                                    print("wrong")
                        j += 1
                i += 1
                offset += 1000
            diag = [0 for i in range(120)]
            count1 = len(bArr)
            i = 0
            a = []
            while i < count1:
                result = (datetime.datetime.today() - bArr[i]) / 365
                result = str(result).split(' ')
                j = int(result[0])
                diag[j] += 1
                i += 1
            answer = [" "]
            i = 0
            cnt = len(diag)
            answer.append("Возраст - Кол-во"+ "\n")
            while i < cnt:
                if diag[i] != 0:
                    answer.append(str(i))
                    answer.append('    -    ')
                    answer.append(str(diag[i]))
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

@bot.message_handler(commands=["group_ages"])
def groups(message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Blocking call which returns when the display_date() coroutine is done
    loop.run_until_complete(group_ages(message))
    loop.close()

if __name__ == '__main__':
    bot.polling()
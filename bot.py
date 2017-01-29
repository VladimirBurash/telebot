import config
import telebot,datetime,aiohttp,asyncio


bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=["help"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, 'Введите "/friends_ages id_пользователя" для просмотра статистики '
                                      'друзей пользователя \n'
                                      ' Введите "/group_ages id_группы" для просмотра статистики '
                                      'возраста подписчиков группы ')

async def loading(messege):
    bot.send_message(messege.chat.id,'Loading...')

def get_bdate(req,con,bArr):
    for j in range(con):
        bdate = req['response']['items'][j].get('bdate')
        if bdate:
            if len(bdate) > 5:
                try:
                    bdate = datetime.datetime.strptime(bdate, "%d.%m.%Y")
                    bArr.append(bdate)
                except ValueError:
                    print("wrong")
    return bArr

def make_gist(bArr,message):
    diag = [0 for i in range(120)]
    count1 = len(bArr)
    for i in range(count1):
        result = (datetime.datetime.today() - bArr[i]) / 365
        result = str(result).split(' ')
        j = int(result[0])
        diag[j] += 1
    answer = [" "]
    cnt = len(diag)
    answer.append("Возраст - Кол-во" + "\n")
    for i in range(cnt):
        if diag[i] != 0:
            answer.append(str(i))
            answer.append('    -    ')
            answer.append(str(diag[i]))
            answer.append("\n")

    bot.send_message(message.chat.id, ' '.join(answer))



async def friends_ages(message):
    await loading(message)
    try:
        username = message.text.split(' ')[1]
    except IndexError:
        bot.send_message(message.chat.id,'Вы забыли ввести id пользователя')
        return 0
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.vk.com/method/users.get?user_ids="+username+"&fields=bdate&v=5.58") as resp:
            req_id = await resp.json()
            try:
                user_id = req_id['response'][0].get('id')
            except IndexError:
                bot.send_message(message.chat.id,'Такого пользователя не существует')
                return 0
            async with session.get("https://api.vk.com/method/friends.get?user_id="+str(user_id)+"&fields=bdate&v=5.58") as resp:
                req = await resp.json()
                count = req['response'].get('count')
                bArr = []
                get_bdate(req,count,bArr)
                make_gist(bArr,message)

async def group_ages(message):
    offset = 0
    await loading(message)
    try:
        groupname = message.text.split(' ')[1]
    except IndexError:
        bot.send_message(message.chat.id,'Вы забыли ввести id группы')
        return 0
    with aiohttp.ClientSession() as session:
        async with session.get("https://api.vk.com/method/groups.getMembers?group_id="+groupname+"&offset="+str(offset)+"&fields=bdate&fields=bdate&v=5.58") as resp:
            req_id = await resp.json()
            count = req_id['response'].get('count')
            loops = int(count/1000)
            bArr = []
            for i in range(loops):
                async with session.get("https://api.vk.com/method/groups.getMembers?group_id=" + groupname + "&offset=" + str(offset) + "&fields=bdate&fields=bdate&v=5.58") as resp:
                    req = await resp.json()
                    if count-((i+1)*1000)>0:
                        con = 1000
                        per = int(100*1000*(i+1)/count)
                    else:
                        con = 1000-abs(count-(i+1)*1000)
                        per = 100
                    get_bdate(req,con,bArr)
                offset += 1000
                print("Выполнено: "+str(per)+"%")
            make_gist(bArr,message)



@bot.message_handler(commands=["friends_ages"])
def friends(message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(friends_ages(message))
    loop.close()

@bot.message_handler(commands=["group_ages"])
def groups(message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(group_ages(message))
    loop.close()

if __name__ == '__main__':
    bot.polling(none_stop=True)

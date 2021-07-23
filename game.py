import discord
import hgtk
import random
import requests
import os
from discord.ext import commands

# ///Discord/// #
# Discord Bot command prefix
bot = commands.Bot(command_prefix='!')
# !도움말을 위한 기존에 있는 help 제거
bot.remove_command('help')
commandList = ['!도움말', '!시작', '!그만', '!다시']
# ///끝말잇기/// #
whiteList = []
answord = ''
sword = ''
wordOK = False
playing = False
# 이미 있는 단어 알기위해 단어목록 저장
history = []
# 좀 치사한 한방단어 방지 목록
blacklist = ['즘', '틱', '늄', '슘', '퓸', '늬', '뺌', '섯', '숍', '튼', '름', '늠', '쁨']
# 키 발급은 https://krdict.korean.go.kr/openApi/openApiInfo
# apikey = os.environ["DIC_TOKEN"]
apikey = '47EB43C7CE5F26EC1C29499CA4C35D18'


# Discord Bot Ready
@bot.event
async def on_ready():  # 디스코드 봇 로그인
    print('Logged in as \nName: {}\n  ID: {}'.format(bot.user.name, bot.user.id))
    print('=' * 10)  # 상태 메세지 생성
    guilds = await bot.fetch_guilds(limit=150).flatten()
    print(guilds)
    await bot.change_presence(activity=discord.Activity(name="!도움말", type=0))


# 지정한 두 개의 문자열 사이의 문자열을 리턴하는 함수
# string list에서 단어, 품사와 같은 요소들을 추출할때 사용됩니다
def midReturn(val, s, e):
    if s in val:
        val = val[val.find(s) + len(s):]
        if e in val:
            val = val[:val.find(e)]
    return val


# 지정한 두 개의 문자열 사이의 문자열 여러개를 리턴하는 함수
# string에서 XML 등의 요소를 분석할때 사용됩니다
def midReturn_all(val, s, e):
    if s in val:
        tmp = val.split(s)
        val = []
        for i in range(0, len(tmp)):
            if e in tmp[i]:
                val.append(tmp[i][:tmp[i].find(e)])
    else:
        val = []
    return val


def findword(query):
    url = 'https://krdict.korean.go.kr/api/search?key=' + apikey + '&part=word&pos=1&q=' + query
    response = requests.get(url)
    ans = []

    # 단어 목록을 불러오기
    words = midReturn_all(response.text, '<item>', '</item>')
    for w in words:
        # 이미 쓴 단어가 아닐때
        if not (w in history):
            # 한글자가 아니고 품사가 명사일때
            word = midReturn(w, '<word>', '</word>')
            pos = midReturn(w, '<pos>', '</pos>')
            if len(word) > 1 and pos == '명사' and word not in history and not word[len(word) - 1] in blacklist:
                ans.append(w)
    if len(ans) > 0:
        return random.choice(ans)
    else:
        return ''


def checkexists(query):
    url = 'https://krdict.korean.go.kr/api/search?key=' + apikey + '&part=word&sort=popular&num=100&pos=1&q=' + query
    response = requests.get(url)
    ans = ''

    # 단어 목록을 불러오기
    words = midReturn_all(response.text, '<item>', '</item>')
    for w in words:
        # 이미 쓴 단어가 아닐때
        if not (w in history):
            # 한글자가 아니고 품사가 명사일때
            word = midReturn(w, '<word>', '</word>')
            pos = midReturn(w, '<pos>', '</pos>')
            if len(word) > 1 and pos == '명사' and word == query:
                ans = w

    if len(ans) > 0:
        return ans
    else:
        return ''


# Game Play Issue
def PlayIssuse(query):
    global wordOK
    # print('PlayIssue')
    if len(query) == 1:
        # print('up to 2words')
        wordOK = False
        return '적어도 두 글자가 되어야 합니다'

    if query in history:
        # print('overlap')
        wordOK = False
        return '이미 입력한 단어입니다'

    if query[len(query) - 1] in blacklist:
        # print("cheating")
        wordOK = False
        return '아.. 좀 치사한데요..\n다시 입력해주세요!'

    if wordOK:
        # print("wordOK")
        # 단어의 유효성을 체크
        ans = checkexists(query)
        if ans == '':
            # print("유효한")
            wordOK = False
            return '유효한 단어를 입력해 주세요'
        else:
            return '(' + midReturn(ans, '<definition>', '</definition>') + ')\n'


# Command '!도움말'
@bot.command()
async def 도움말(ctx):
    await ctx.message.delete()
    await ctx.send("=============파이썬 끝말잇기=============\n" +
                   "사전 데이터 제공: 국립국어원 한국어기초사전\n" +
                   "                                 - - - 게임 방법 - - -\n" +
                   "'!시작'을 입력하면 게임이 시작됩니다. 단어를 입력해 주세요.\n" +
                   "'!그만'을 입력하면 게임이 종료되며\n'!다시'를 입력하여 게임을 바로 다시 시작할 수 있습니다.\n" +
                   "                                  - - - 게임 규칙 - - -\n" +
                   "1. 사전에 등재된 명사여야 합니다\n" +
                   "2. 적어도 단어의 길이가 두 글자 이상이어야 합니다\n" +
                   "3. 이미 사용한 단어를 다시 사용할 수 없습니다\n" +
                   "4. 두음법칙 적용 가능합니다 (ex. 리->니)\n" +
                   "======================================\n", delete_after=30.0)


# Game Start
@bot.command()
async def 시작(ctx):
    global playing
    await ctx.message.delete()
    # Is Ready
    if not playing:
        await ctx.send('게임을 시작합니다. 단어를 입력하여 끝말잇기를 시작합니다.', delete_after=5.0)
        # !시작을 입력하면 whileList에 추가
        whiteList.append(ctx.author.id)
        # print(whiteList)
        playing = True
    # Is In game
    elif playing:
        await ctx.send('이미 게임중입니다', delete_after=3.0)


# Game Stop
@bot.command()
async def 그만(ctx):
    await ctx.message.delete()
    global history, answord, playing
    await ctx.send('컴퓨터의 승리!', delete_after=3.0)
    playing = False
    history = []
    answord = ''


# Game Restart
@bot.command()
async def 다시(ctx):
    await ctx.message.delete()
    global history, answord
    await ctx.send('게임을 다시 시작합니다.', delete_after=3.0)
    history = []
    answord = ''


# !단어를 입력받지 않기 위해 on_message 활용
@bot.event
async def on_message(ctx):
    # print(ctx.content)
    if ctx.author == bot.user:
        return
    # 미리 함수로 지정된 함수들의 이름이 있으면 process_commands를 통해 출력
    if ctx.content in commandList:
        for firstMessage in commandList:
            if ctx.content.startswith(firstMessage):
                await bot.process_commands(ctx)
    else:
        # !참가 한 사람만 게임을 시작 할 수 있습니다.
        if ctx.author.id in whiteList:
            global answord, sword, wordOK, history, blacklist, playing
            # !'단어'를 입력할 시 !를 제거합니다.
            if ctx.content[0] in '!' and playing:
                query = ctx.content.replace("!", "")
            else:
                query = ctx.content
            # Playing True
            if playing:
                await ctx.delete()
                wordOK = True
                # 첫 글자의 초성 분석하여 두음법칙 적용 -> 규칙에 아직 완벽하게 맞지 않으므로 차후 수정 필요
                if not len(history) == 0 and not query[0] == sword and not query == '':
                    sdis = hgtk.letter.decompose(sword)
                    qdis = hgtk.letter.decompose(query[0])
                    if sdis[0] == 'ㄹ' and qdis[0] == 'ㄴ':
                        await ctx.channel.send('두음법칙 적용됨', delete_after=3.0)
                    elif (sdis[0] == 'ㄹ' or sdis[0] == 'ㄴ') and qdis[0] == 'ㅇ' and qdis[1] in (
                            'ㅣ', 'ㅑ', 'ㅕ', 'ㅛ', 'ㅠ', 'ㅒ', 'ㅖ'):
                        await ctx.channel.send('두음법칙 적용됨', delete_after=3.0)
                    else:
                        wordOK = False
                        await ctx.channel.send(sword + '(으)로 시작하는 단어여야 합니다.', delete_after=15.0)
                # 문제가 있는 단어인지 확인
                await ctx.channel.send(PlayIssuse(query), delete_after=3.0)
                # 단어에 문제가 없으면 봇이 쓸 단어 검색 및 결과 출력
                if wordOK:
                    history.append(query)
                    start = query[len(query) - 1]
                    ans = findword(start + '*')
                    # ㄹ -> ㄴ 검색
                    if ans == '':
                        sdis = hgtk.letter.decompose(start)
                        if sdis[0] == 'ㄹ':
                            newq = hgtk.letter.compose('ㄴ', sdis[1], sdis[2])
                            # print(start + '->' + newq)
                            start = newq
                            ans = findword(newq + '*')
                    # (ㄹ->)ㄴ -> ㅇ 검색
                    if ans == '':
                        sdis = hgtk.letter.decompose(start)
                        if sdis[0] == 'ㄴ' and sdis[1] in ('ㅣ', 'ㅑ', 'ㅕ', 'ㅛ', 'ㅠ', 'ㅒ', 'ㅖ'):
                            newq = hgtk.letter.compose('ㅇ', sdis[1], sdis[2])
                            # print(start + '->' + newq)
                            ans = findword(newq + '*')
                    # 찾을 단어가 없을 때
                    if ans == '':
                        await ctx.channel.send('당신의 승리!', delete_after=3.0)
                        playing = False
                        history = []
                        answord = ''
                    else:
                        answord = midReturn(ans, '<word>', '</word>')  # 단어 불러오기
                        ansdef = midReturn(ans, '<definition>', '</definition>')  # 품사 불러오기
                        history.append(answord)
                        await ctx.channel.send(query + '>' + answord + '\n(' + ansdef + ')\n', delete_after=3.0)
                        sword = answord[len(answord) - 1]

                        # 컴퓨터 승리여부 체크
                        # if findword(sword) == '':
                        #    print('tip: \'/다시\'를 입력하여 게임을 다시 시작할 수 있습니다')
                        await ctx.channel.send(sword + '(으)로 시작하는 단어를 입력해 주세요.', delete_after=15.0)


# bot.run(os.environ["BOT_TOKEN"])
bot.run('NDcyOTgxMTM4NjEzNDY5MTg0.W11AAw.iowk5N0IjhrZXytodkdKYIlTo_U')
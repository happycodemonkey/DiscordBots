import discord
import asyncio
import operator

class OpenPoll:
    """ Track and render an open poll """

    drawLength = 10
    drawPadding = 2

    def __init__(self, client, channel, id, title, initialOptions):
        self.id = id
        self.client = client                                                            # client to communicate to
        self.lock = asyncio.Lock()                                                      # concurrency control for internal data structures
        self.title = title.strip('*_-~` ')                                              # title of the poll
        self.channel = channel                                                          # channel to write message to
        self.message = None                                                             # client message used to write back to the channel
        self.options = {option.strip('*_-~` '):0 for option in initialOptions}          # dict of (option, vote count)
        if len(initialOptions) > 0:
            self.longestOption = max(len(option) for option in initialOptions)
        else:
            self.longestOption = 0
        self.votes = {}                                                                 # dict of (user, option)

    async def render_callertakeslock(self):
        lines = []

        lines.append("Open Poll! Vote with `!vote {0} <option>`\n".format(self.id))
        lines.append("**{0}**```".format(self.title)) # bold the poll title, and begin the multiline code block

        # scale the lines compared to the current winner
        if len(self.options) > 0:
            sortedOptions = sorted(self.options.items(), key=operator.itemgetter(1), reverse=True)
            winnerMagnitude = sortedOptions[0][1]

            for (option, voteCount) in sortedOptions:
                line = str(option)
                line = line + (' ' * ((self.longestOption + OpenPoll.drawPadding) - len(option))) + '[' # print the option and pad to where we will draw the bar
                if winnerMagnitude > 0:
                    scale = int((voteCount / winnerMagnitude) * OpenPoll.drawLength)
                else:
                    scale = 0

                if scale > 0:
                    line = line + ('*' * scale)
                if scale < OpenPoll.drawLength:
                    line = line + ('.' * (OpenPoll.drawLength - scale))
                
                line = line + ']  ({0} votes)'.format(voteCount)
                
                lines.append(line)
        else:
            lines.append("No options yet - add some with !vote")

        lines.append('```')

        if self.message is None:
            self.message = await self.client.send_message(self.channel, '\n'.join(lines))
        else:
            await self.client.edit_message(self.message, '\n'.join(lines))

    async def render(self):
        with await self.lock:
            await self.render_callertakeslock()

    async def handleVote(self, user, option):
        with await self.lock:
            userHasVoted = user in self.votes.keys()
            if not userHasVoted or self.votes[user] != option:
                if userHasVoted:
                    oldOption= self.votes[user]
                    self.options[oldOption] = self.options[oldOption] - 1
                    del self.votes[user]
                    
                self.votes[user] = option

                if option not in self.options.keys():
                    self.options[option] = 1
                else:
                    self.options[option] = self.options[option] + 1

                if len(option) > self.longestOption:
                    self.longestOption = len(option)

                await self.render_callertakeslock()

    async def clearVote(self, user, pollId):
        with await self.lock:
            userHasVoted = user in self.votes.keys()
            if userHasVoted:
                oldOption= self.votes[user]
                self.options[oldOption] = self.options[oldOption] - 1
                del self.votes[user]

                await self.render_callertakeslock()

class PollBot:
    """ Run open polls """

    def __init__(self, client):
        self.client = client
        self.lock = asyncio.Lock()
        self.nextPollId = 0
        self.polls = {}

    async def handleMessage(self, message):
        if message.content.startswith('!poll'):
            try:
                args = message.content.strip()[6:].split(',') # trim off the command

                if len(args) == 0 or args[0] == "":
                    raise Exception()

                if len(args) > 1:
                    options = args[1:]
                else:
                    options = []

                title = args[0]

                poll = None
                with await self.lock:
                    self.polls[self.nextPollId] = OpenPoll(self.client, message.channel, self.nextPollId, title, options)
                    poll = self.polls[self.nextPollId]
                    self.nextPollId = self.nextPollId + 1

                await poll.render()
            except Exception as err:
                await self.client.send_message(message.channel, 'Invalid format. try `!poll <title>[,<option1>,<option2>,...]`\n\nfor example: `!poll who is best godmin?,jessytang,notjessytang`')
        elif message.content.startswith('!vote'):
            try:
                line = message.content.strip()[6:]
                firstSpace = line.find(" ")
                id = int(line[0:firstSpace])
                option = line[firstSpace + 1:]

                poll = None
                with await self.lock:
                    poll = self.polls[id]

                await poll.handleVote(message.author, option)
            except Exception as err:
                await self.client.send_message(message.channel, 'Invalid format or poll id. try `!vote <poll id> <option>`\n\nfor example: `!vote 0 jessytang`')
        elif message.content.startswith('!clearvote'):
            try:
                line = message.content.strip()[11:]
                id = int(line)

                poll = None
                with await self.lock:
                    poll = self.polls[id]

                await poll.clearVote(message.author, id)
            except Exception as err:
                await self.client.send_message(message.channel, 'Invalid poll id or expired poll. try `!clearvote <poll id>`\n\nfor example: `!clearvote 0`')


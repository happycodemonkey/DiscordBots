import discord
import asyncio
import operator

class OpenPoll:
    """ Track and render an open poll """

    _drawLength = 10
    _drawPadding = 2

    def __init__(self, client, channel, id, title, initialOptions=[]):
        """
        Construct the poll instance.

        Args:
            client: The discord client to communicate with.
            channel: The discord channel to render the poll to as a message.
            id (int): The id of the poll.
            title (str): The title of the poll.
            initialOptions (list of str): The initial options with which to populate the poll (default: []).

        Attributes:
            self._client (discord.Client): The discord client to communicate with.
            self._channel (discord.Channel): The discord channel to render the poll to as a message.
            self.id (int): The id of the poll.
            self.title (str): The title of the poll. Markdown characters are removed.
            self._lock (asyncio.Lock): Concurrency control for internal data structures.
            self._message (discord.Message): The message to render to (owned by this poll).
            self._options (dict of str:int): Dictionary mapping options to the number of votes for that option.
                The vote count should equal the number of values in self._votes matching this key (option).
            self._votes (dict of discord.User:str): Dictionary mapping users to their vote in this poll.

        """
        self._client = client
        self._channel = channel 
        self.id = id
        self.title = title.strip().replace('*', '').replace('_', '').replace('-', '').replace('`', '')
        self._lock = asyncio.Lock()
        self._message = None
        self._options = {option.strip('*_-~` '):0 for option in initialOptions}
        self._longestOption = 0 if len(initialOptions) == 0 else max(len(option) for option in initialOptions)
        self._votes = {}

    async def _render_callertakeslock(self):
        lines = []

        lines.append("Open Poll! Vote with `!vote {0} <option>`\n".format(self.id))

        # bold the poll title, and begin the multiline code block
        lines.append("**{0}**```".format(self.title))

        # scale the lines compared to the current winner
        if len(self._options) > 0:

            # sort the options by descending vote count (winner first)
            sortedOptions = sorted(self._options.items(), key=operator.itemgetter(1), reverse=True)
            winnerMagnitude = sortedOptions[0][1]

            for (option, voteCount) in sortedOptions:
                line = str(option)
                line = line + (' ' * ((self._longestOption + OpenPoll._drawPadding) - len(option))) + '[' # print the option and pad to where we will draw the bar
                if winnerMagnitude > 0:
                    scale = int((voteCount / winnerMagnitude) * OpenPoll._drawLength)
                else:
                    scale = 0

                if scale > 0:
                    line = line + ('*' * scale)
                if scale < OpenPoll._drawLength:
                    line = line + ('.' * (OpenPoll._drawLength - scale))
                
                line = line + ']  ({0} votes)'.format(voteCount)
                
                lines.append(line)
        else:
            lines.append("No options yet - add some with !vote")

        lines.append('```')

        messageContent = '\n'.join(lines)
        if self._message is None:
            self._message = await self._channel.send(messageContent)
        else:
            await self._message.edit(content=messageContent)

    async def render(self):
        with await self._lock:
            await self._render_callertakeslock()

    async def handleVote(self, user, option):
        with await self._lock:
            userHasVoted = user in self._votes.keys()
            if not userHasVoted or self._votes[user] != option:
                if userHasVoted:
                    oldOption= self._votes[user]
                    self._options[oldOption] = self._options[oldOption] - 1
                    del self._votes[user]
                    
                self._votes[user] = option

                if option not in self._options.keys():
                    self._options[option] = 1
                else:
                    self._options[option] = self._options[option] + 1

                if len(option) > self._longestOption:
                    self._longestOption = len(option)

                await self._render_callertakeslock()

    async def clearVote(self, user, pollId):
        with await self._lock:
            userHasVoted = user in self._votes.keys()
            if userHasVoted:
                oldOption= self._votes[user]
                self._options[oldOption] = self._options[oldOption] - 1
                del self._votes[user]

                await self._render_callertakeslock()

class PollBot:
    """ Run open polls """

    def __init__(self, client):
        self._client = client
        self._lock = asyncio.Lock()
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
                with await self._lock:
                    self.polls[self.nextPollId] = OpenPoll(self._client, message.channel, self.nextPollId, title, options)
                    poll = self.polls[self.nextPollId]
                    self.nextPollId = self.nextPollId + 1

                await poll.render()
            except Exception as err:
                await message.channel.send('Invalid format. try `!poll <title>[,<option1>,<option2>,...]`\n\nfor example: `!poll who is best godmin?,jessytang,notjessytang`')
        elif message.content.startswith('!vote'):
            try:
                line = message.content.strip()[6:]
                firstSpace = line.find(" ")
                id = int(line[0:firstSpace])
                option = line[firstSpace + 1:]

                poll = None
                with await self._lock:
                    poll = self.polls[id]

                await poll.handleVote(message.author, option)
            except Exception as err:
                await message.channel.send('Invalid format or poll id. try `!vote <poll id> <option>`\n\nfor example: `!vote 0 jessytang`')
        elif message.content.startswith('!clearvote'):
            try:
                line = message.content.strip()[11:]
                id = int(line)

                poll = None
                with await self._lock:
                    poll = self.polls[id]

                await poll.clearVote(message.author, id)
            except Exception as err:
                await message.channel.send('Invalid poll id or expired poll. try `!clearvote <poll id>`\n\nfor example: `!clearvote 0`')


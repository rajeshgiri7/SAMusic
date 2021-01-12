import discord
# import delete
from discord.ext import commands, tasks
from discord.utils import get
from youtube_search import YoutubeSearch
import json
from discord import FFmpegPCMAudio
from random import choice
from pafy import new
import queue


class Music(commands.Cog):
    musicQueue = dict()
    current_song = dict()
    volumeSet = dict()
    voiceAttr = dict()
    ctxAttr = dict()

    def __init__(self, client):
        self.client = client
        self.autoNext.start()

    @commands.command(pass_context=True, aliases=['connect', 'c', 'j'])
    async def join(self, ctx):
        guild = ctx.guild
        channel = ctx.message.author.voice
        if channel is None:
            await ctx.send("```css\nNot connected to a voice channel\n```")
            return
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await ctx.send("```css\nAlready connected to a voice channel\n```")
            await voice.move_to(channel.channel)
        else:
            await channel.channel.connect()
            self.musicQueue[guild] = queue.Queue()
            self.ctxAttr[guild] = ctx
            self.voiceAttr[guild] = voice
            # self.autoNext()
            await ctx.message.add_reaction('✅')

    @commands.command(pass_context=True, aliases=['disconnect', 'dc'],force=False)
    async def leave(self, ctx):
        guild = ctx.guild
        channel = ctx.message.author.voice
        if channel is None:
            await ctx.send("```css\nNot connected to a voice channel\n```")
            return
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice is None:
            await ctx.send("```css\nAlready disconnected from a voice channel\n```")
        else:
            self.musicQueue.pop(guild)
            self.ctxAttr.pop(guild)
            self.voiceAttr.pop(guild)
            await voice.disconnect()
            await ctx.message.add_reaction('⭕')

    # @commands.event
    # async def 

    @commands.command(pass_context=True, aliases=['tplay', 'p'])
    async def play(self, ctx, *, url=""):
        if url != "":
            guild = ctx.guild
            author = ctx.message.author.mention
            channel = ctx.message.author.voice
            if channel is None:
                await ctx.send("```css\nYou are not connected to a voice channel\n```")
                return
            voice = get(self.client.voice_clients, guild=ctx.guild)
            if voice and voice.is_connected():
                await voice.move_to(channel.channel)
            else:
                voice = await channel.channel.connect()
                self.musicQueue[guild] = queue.Queue()
            await ctx.send('```yml\nSearching\n```')
            song = self.addMusic(url, author, guild)
            if voice.is_paused():
                voice.resume()
                embed = (discord.Embed(title='🎵 Playing🎵',
                                           description='```yml\n{}\n``` \n[Click to Download]({})\n'.format(
                                               self.current_song[guild]['title'], self.current_song[guild]['url']),
                                           color=discord.Color.purple())
                             .set_thumbnail(url=self.current_song[guild]['thumbnails'])
                             .add_field(name='Duration', value=self.current_song[guild]['time'])
                             .add_field(name='Requested by', value=self.current_song[guild]['user'])
                             .add_field(name='Uploader', value='{}'.format(self.current_song[guild]['uploader']))
                             )
                await ctx.send(embed=embed)
                await ctx.message.add_reaction('▶️')
            # await ctx.delete_message('Searching')
            # delete search message baki??
            if song == "Not found":
                await ctx.send("```css\nNo song found\n```")
                return
            else:
                if voice.is_playing():
                    await ctx.send(embed=(discord.Embed(title='🎵 Added to Queue🎵', description='```yml\n{}\n```'.format(song['title']),
                                                        color=discord.Color.purple()))
                                   .set_thumbnail(url=song['thumbnails'])
                                   .add_field(name='Duration', value=song['time'])
                                   .add_field(name='Requested by', value=song['user'])
                                   .add_field(name='Uploader', value='{}'.format(song['uploader']))
                                   )
                else:
                    name = self.nextMusic(voice, guild)
                    self.current_song[guild] = name
                    embed = (discord.Embed(title='🎵 Playing🎵',
                                           description='```yml\n{}\n``` \n[Click to Download]({})\n'.format(
                                               name['title'], name['url']),
                                           color=discord.Color.purple())
                             .set_thumbnail(url=name['thumbnails'])
                             .add_field(name='Duration', value=name['time'])
                             .add_field(name='Requested by', value=name['user'])
                             .add_field(name='Uploader', value='{}'.format(name['uploader']))
                             )
                    await ctx.send(embed=embed)
                    # await ctx.send("♫ Playing {} [by {}]".format(name['title'],name['user'].split('#')[0]))
                    await ctx.message.add_reaction('▶️')
                    self.ctxAttr[guild] = ctx
        else:
            await ctx.send("```css\nInvalid command\n```")

    @commands.command(pass_context=True, aliases=['ps', 'pp'])
    async def pause(self, ctx):
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("```css\nYou are not connected to a voice channel\n```")
            return
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            await ctx.send("```css\nNot connected to voice channel\n```")
            return

        voice.pause()
        await ctx.message.add_reaction('⏸️')

    @commands.command(pass_context=True, aliases=['rs', 'rr'])
    async def resume(self, ctx):
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("```css\nYou are not connected to a voice channel\n```")
            return
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            await ctx.send("```css\nNot connected to voice channel\n```")
            return

        if voice.is_paused():
            voice.resume()
            await ctx.message.add_reaction('▶️')
        else:
            await ctx.send("```css\nNo songs in the paused to resume\n```")

    @commands.command(pass_context=True, aliases=['st'])
    async def stop(self, ctx):
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("```css\nYou are not connected to a voice channel\n```")
            return
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            await ctx.send("```css\nNot connected to voice channel\n```")
            return
        if voice.is_playing() or voice.is_paused():
            voice.stop()
            await ctx.message.add_reaction('⏹️')
        else:
            await ctx.send("```css\nNo songs in the playing/paused\n```")

    @commands.command(pass_context=True, name="queue", aliases=['q'])
    async def queueMusic(self, ctx):
        guild = ctx.guild
        temp = queue.Queue()
        if self.musicQueue.get(guild, None) != None:
            if not self.musicQueue[guild].empty():
                i = 1
                descript = ""
                while not self.musicQueue[guild].empty():
                    data = self.musicQueue[guild].get()
                    temp.put(data)
                    descript += '```yml\n{}. {}\n```'.format(i, data['title'])
                    i += 1
                    # await ctx.send("- ♫ {} [by {}]".format(data['title'],data['user'].split('#')[0]))
                embed = (discord.Embed(title='🎵 Queue🎵',
                                    description=descript,
                                    color=discord.Color.purple())
                        )
                await ctx.send(embed=embed)
                self.musicQueue[guild] = temp
            else:
                await ctx.send(embed=(discord.Embed(title='🎵 Queue🎵',
                                    description='```yml\nNo songs in the queue\n```',
                                    color=discord.Color.purple())
                        ))     
        else:
            await ctx.send(embed=(discord.Embed(title='🎵 Queue🎵',
                                    description='```yml\nNo songs in the queue\n```',
                                    color=discord.Color.purple())
                        ))     

    @commands.command(pass_context=True, aliases=['np', 'playing', 'current'])
    async def now(self, ctx):
        guild = ctx.guild
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("```css\nYou are not connected to a voice channel\n```")
            return
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            await ctx.send("```css\nNot connected to voice channel\n```")
            return
        if voice.is_playing():
            embed = (discord.Embed(title='🎵 Now playing🎵',
                                   description='```yml\n{}\n``` \n[Click to Download]({})\n'.format(
                                       self.current_song[guild]['title'], self.current_song[guild]['url']),
                                   color=discord.Color.purple())
                     .set_thumbnail(url=self.current_song[guild]['thumbnails'])
                     .add_field(name='Duration', value=self.current_song[guild]['time'])
                     .add_field(name='Requested by', value=self.current_song[guild]['user'])
                     .add_field(name='Uploader', value='{}'.format(self.current_song[guild]['uploader']))
                     )
            await ctx.send(embed=embed)
        else:
            await ctx.send("```css\nNothing is Playing\n```")

    @commands.command(pass_context=True, name="next", aliases=['n'])
    async def next(self, ctx):
        guild = ctx.guild
        channel = ctx.message.author.voice
        if channel is None:
            await ctx.send("```css\nYou are not connected to a voice channel\n```")
            return
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel.channel)
        else:
            voice = await channel.channel.connect()
        voice.stop()
        if not self.musicQueue[guild].empty():
            name = self.nextMusic(voice, guild)
            self.current_song[guild] = name
            embed = (discord.Embed(title='🎵 Playing🎵',
                                   description='```yml\n{}\n``` \n[Click to Download]({})\n'.format(
                                       name['title'], name['url']),
                                   color=discord.Color.purple())
                     .set_thumbnail(url=name['thumbnails'])
                     .add_field(name='Duration', value=name['time'])
                     .add_field(name='Requested by', value=name['user'])
                     .add_field(name='Uploader', value='{}'.format(name['uploader']))
                     )
            await ctx.send(embed=embed)
            await ctx.message.add_reaction('⏭️')
            self.ctxAttr[guild] = ctx
        else:
            await ctx.send(embed=(discord.Embed(title='🎵 Queue🎵',
                                    description='```yml\nNo songs in the queue\n```',
                                    color=discord.Color.purple())
                        ))    

    def addMusic(self, songName, user, server):
        results = json.loads(YoutubeSearch(
            str(songName), max_results=1).to_json())
        if len(results['videos']) > 0:
            video = new(results['videos'][0]['id'])
            audio = video.getbestaudio().url
            dur = results['videos'][0]['duration']
            data = {"title": results['videos'][0]['title'], "url": audio, "time": dur, "user": str(
                user), "thumbnails": results['videos'][0]['thumbnails'][0], "uploader": results['videos'][0]['channel']}
            self.musicQueue[server].put(data)
            return data
        else:
            return "Not found"

    def nextMusic(self, voice, server):
        ffmpeg_opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        data = self.musicQueue[server].get()
        voice.play(FFmpegPCMAudio(data['url'], **ffmpeg_opts))
        voice.source = discord.PCMVolumeTransformer(
            voice.source, volume=self.volumeSet.get(server, 1.0))
        self.voiceAttr[server] = voice
        return data

    @commands.command(name='volume', aliases=['v'])
    async def _volume(self, ctx, *, volume=100):
        guild = ctx.guild
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if not voice.is_playing:
            return await ctx.send('``````css\nNothing being played at the moment.\n```')
        volume = int(volume)
        if 0 <= volume <= 100:
            vc = volume / 100.0
            self.volumeSet[guild] = vc
            voice.source.volume = self.volumeSet[guild]
            if volume == 0:
                await ctx.send(embed=(discord.Embed(description='```elm\n🔇:{}%\n```'.format(volume))))
            elif 1 <= volume <= 15:
                await ctx.send(embed=(discord.Embed(description='```elm\n🔈:{}%\n```'.format(volume))))
            elif 16 <= volume <= 50:
                await ctx.send(embed=(discord.Embed(description='```elm\n🔉:{}%\n```'.format(volume))))
            else:
                await ctx.send(embed=(discord.Embed(description='```elm\n🔊:{}%\n```'.format(volume))))
            await ctx.message.add_reaction('✅')
        else:
            await ctx.send('```yaml\nVolume: Between 0 and 100\n```')


    @tasks.loop(seconds=3)
    async def autoNext(self):
        for key, val in self.ctxAttr.items():
            if self.voiceAttr.get(key, None) is not None and self.ctxAttr.get(key, None) is not None:
                if not self.voiceAttr[key].is_playing() and not self.voiceAttr[key].is_paused() and not self.musicQueue[key].empty():
                    name = self.nextMusic(self.voiceAttr[key], key)
                    self.current_song[key] = name
                    embed = (discord.Embed(title='🎵 Playing🎵',
                                        description='```yml\n{}\n``` \n[Click to Download]({})\n'.format(
                                            name['title'], name['url']),
                                        color=discord.Color.purple())
                            .set_thumbnail(url=name['thumbnails'])
                            .add_field(name='Duration', value=name['time'])
                            .add_field(name='Requested by', value=name['user'])
                            .add_field(name='Uploader', value='{}'.format(name['uploader']))
                            )
                    await val.send(embed=embed)


def setup(client):
    client.add_cog(Music(client))

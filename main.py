import discord
from discord.ext import commands
from discord.utils import get
import argparse
from collections import deque

from concurrent.futures import ThreadPoolExecutor
import asyncio

import os
from dotenv import load_dotenv
import sys

# Import custom functions from the oogabooga library
from oogabooga import init_llm, generate_llm
from speech2text import init_whisper, generate_whisper
from text2speech import init_bark, generate_bark, init_tortoise, generate_tortoise, audio_combine, init_emotion, get_emotion
from udp_server import init_udp_server, udp_server

import tempfile
from tortoise.utils.text import split_and_recombine_text

parser = argparse.ArgumentParser()
parser.add_argument("--reboot", action="store", help="Helper for rebooting the bot (message_id) (don't use this except you are a bot)")
parser.add_argument("--channel", action="store", help="Helper for rebooting the bot (channel_id)(don't use this except you are a bot)")

# Load environment variables from a .env file
load_dotenv()
model_url = os.environ.get("MODEL_URL")
llm_debug = eval(os.environ.get("LLM_DEBUG", "False"))

use_whisper = os.environ.get("USE_WHISPER", "1")
whisper_model = os.environ.get("WHISPER_MODEL", "base")

use_bark = os.environ.get("USE_BARK", "0")
bark_use_small_model = os.environ.get("BARK_USE_SMALL_MODEL", "1")
bark_speaker = os.environ.get("BARK_SPEAKER", "v2/en_speaker_7")

use_tortoise = os.environ.get("USE_TORTOISE", "1")
tortoise_voice = os.environ.get("TORTOISE_VOICE", "angie")
tortoise_diffusion_iterations = int(os.environ.get("TORTOISE_DIFFUSION_ITERATIONS", "50"))
tortoise_num_autoregressive_samples = int(os.environ.get("TORTOISE_NUM_AUTOREGRESSIVE_SAMPLES", "2"))
tortoise_temperature = float(os.environ.get("TORTOISE_TEMPERATURE", "0.2"))
tortoise_use_deepspeed = eval(os.environ.get("TORTOISE_USE_DEEPSPEED", "False"))
tortoise_kv_cache = eval(os.environ.get("TORTOISE_KV_CACHE", "True"))
tortoise_half = eval(os.environ.get("TORTOISE_HALF", "True"))

use_emotion = os.environ.get("USE_EMOTION", "1")

use_unity = os.environ.get("USE_UNITY", "0")

discord_token = os.environ.get("DISCORD_TOKEN")



with open("discord_info.txt", "r") as file:
    discord_info = file.read()

# Set up Discord intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

# Initialize the modeles
llm_chain = init_llm(model_url, llm_debug)

if use_tortoise == "1" and use_bark == "1":
    print("Tortoise and Bark cannot be used at the same time")
    sys.exit()

if use_whisper == "1":  
    whisper_model = init_whisper(whisper_model)

if use_bark == "1":
    init_bark(bark_use_small_model)

if use_tortoise == "1":
    tortoise_tts = init_tortoise(tortoise_use_deepspeed, tortoise_kv_cache, tortoise_half, tortoise_num_autoregressive_samples)

if use_emotion == "1":
    if use_tortoise == "1" or use_bark == "1":
        text2emotion = init_emotion()
    else:
        print("Tortoise or Bark must be enabled because emotion detection is used for them exclusively exept in generate_emotion_test")
        sys.exit()

if use_unity == "1":
    init_udp_server()

bot = discord.Bot(intents=intents)
connectet_voice_channel = None


@bot.event
async def on_ready():
    # This method is called when the bot successfully logs in to Discord
    print("Login successful")
    if parser.parse_args().reboot and parser.parse_args().channel:
        channel_id = int(parser.parse_args().channel)
        message_id = int(parser.parse_args().reboot)

        
        response_msg = await bot.get_channel(channel_id).fetch_message(message_id)
        await response_msg.edit(content="Reboot successful")
        

@bot.command(description="Join a voice channel")
async def join(ctx, channel: discord.VoiceChannel = None):
    global connectet_voice_channel
    if channel is None:
        if ctx.author.voice is None:
            await ctx.respond("Not connected to a voice channel, pls specify a channel or join one")
            return
        channel = ctx.author.voice.channel
    connectet_voice_channel = await channel.connect()
    await ctx.respond("Connected to voice channel")

@bot.command(description="Leave a voice channel")
async def leave(ctx):
    if ctx.voice_client is None:
        await ctx.respond("Not connected to a voice channel")
        return
    global connectet_voice_channel
    connectet_voice_channel = None
    await ctx.voice_client.disconnect()
    await ctx.respond("Disconnected from voice channel")


@bot.event
async def on_message(message):
    # This method is called whenever a message is sent in any channel (also direct messages) the bot can access


    # Ignore messages sent by the bot itself to avoid potential infinite loops
    if message.author == bot.user:
        return
    
    if (message.content == None or message.content == "") and message.attachments == None:
        return
    


    print("Nachricht von " + str(message.author) + " enthält " + message.content)


    # Acknowledge receipt of the command by replying to the original message
    response_msg = await message.reply("Processing your request...")


    # If the message contains an audio file, transcribe it and use the transcription as input
    if message.attachments:
        if 'audio' in message.attachments[0].content_type:
            if use_whisper == "1":
                message.content = generate_whisper(whisper_model, message.attachments[0].url)
            else:
                await response_msg.edit(content="Whisper is disabled")
                return


    # Start the time-consuming task asynchronously
    result = await generate_llm_thread(llm_chain, message.content)

    # Edit the "Processing your request..." message with the final response
    await response_msg.edit(content=result)

    if use_tortoise == "1" or use_bark == "1":
        audio_file = await generate_tts(result)
        await response_msg.edit(file=discord.File(audio_file))



@bot.command(description="Show all commands and other information")
async def info(ctx):
    await ctx.respond(discord_info)

@bot.command(description="Show help")
async def help(ctx):
    await ctx.send("Commands: /join, /leave, /info, /delete_short_mem, /reboot, /help, /generate_bark_test, /generate_tortoise_test, /generate_whisper_test")


#Function that deltets the files located in the shortmem directory 
@bot.command(description="Delete shortmem located files")
@commands.has_permissions(manage_channels=True)
async def delete_short_mem(ctx):
    if os.path.exists("shortmem"):
        for item in os.listdir("shortmem"):
            if os.path.isfile(os.path.join("shortmem", item)):
                os.remove(os.path.join("shortmem", item))
        await ctx.respond("shortterm memory deleted, restarting bot")
        response = await ctx.send("pls wait")
        os.execl(sys.executable, sys.executable, *sys.argv, '--reboot', str(response.id), '--channel', str(ctx.channel.id))
    else:
        await ctx.respond("shortterm memory is not existed")

@bot.command(description="Reboot the bot")
@commands.has_permissions(manage_channels=True)
async def reboot(ctx):
    if ctx.voice_client != None:
        await ctx.voice_client.disconnect()

    await ctx.respond("rebooting bot")
    response = await ctx.send("pls wait")
    os.execl(sys.executable, sys.executable, *sys.argv, '--reboot', str(response.id), '--channel', str(ctx.channel.id))

@bot.command(description="Generate audio from text")
async def generate_bark_test(ctx, text: str=None):
    if use_bark == "1":
        response = await ctx.respond(f"Generating audio from text")
        if text is None:
            text = "Hello this is a bark generation test."
        file = await generate_tts(text)
        await response.edit_original_response(file=discord.File(file))
    else:
        await ctx.respond("Bark generation is disabled")

@bot.command(description="Generate text from audio")
async def generate_whisper_test(ctx, file: discord.Attachment):
    if use_whisper == "1":
        if 'audio' in file.content_type:
            response = await ctx.respond(f"Generating text from audio")
            await response.followup.send(generate_whisper(whisper_model, file.url))
        else:
            await ctx.respond("Please send an audio file")
    else:
        await ctx.respond("Whisper is disabled")

@bot.command(description="Generate audio from text")
async def generate_tortoise_test(ctx, text: str=None):
    if use_tortoise == "1":
        response = await ctx.respond(f"Generating audio from text")
        if text is None:
            text = "Hello this is a tortoise generation test."
        file = await generate_tts(text)
        await response.edit_original_response(file=discord.File(file))
    else:
        await ctx.respond("Tortoise is disabled")

@bot.command(description="Generate emotion from text")
async def generate_emotion_test(ctx, text: str=None):
    if use_emotion == "1":
        response = await ctx.respond(f"Generating emotion from text")
        if text is None:
            text = "Hello this is a emotion generation test."
        emotion = get_emotion(text, text2emotion)
        await response.followup.send(str(emotion))
    else:
        await ctx.respond("Emotion is disabled")



semaphore_llm = asyncio.Semaphore(1)

async def generate_llm_thread(llm_chain, content):
    global semaphore_llm

    # Use a semaphore to ensure that only one thread is running this function at a time and to maintain the order of requests
    async with semaphore_llm:
        # Use ThreadPoolExecutor to run the synchronous function in a separate thread
        # This prevents the event loop from being blocked during the time-consuming task
        with ThreadPoolExecutor() as executor:
            result = await bot.loop.run_in_executor(executor, generate_llm, llm_chain, content)
 
    return result


semaphore_tts = asyncio.Semaphore(1)

async def generate_tts(text):
    global semaphore_tts

    # Use a semaphore to ensure that only one thread is running this function at a time and to maintain the order of requests
    async with semaphore_tts:

        emotion = None

        if use_emotion == "1":
            emotion = get_emotion(text, text2emotion)
            emotion_tts = f"[{emotion}] "
            len_emotion = len(emotion_tts)

        # Use ThreadPoolExecutor to run the synchronous function in a separate thread
        # This prevents the event loop from being blocked during the time-consuming task
        with ThreadPoolExecutor() as executor:
            if use_tortoise == "1":
                max_length = 300
                desired_length = 200
                if use_emotion == "1":
                    desired_length = desired_length - len_emotion
                    max_length = max_length - len_emotion
                texts = split_and_recombine_text(text, desired_length=desired_length, max_length=max_length)
                audio_parts = []
                for text in texts:
                    if use_emotion == "1":
                        text = emotion_tts + text
                    result = await bot.loop.run_in_executor(executor, generate_tortoise, text, tortoise_tts, tortoise_diffusion_iterations, tortoise_num_autoregressive_samples, tortoise_temperature, tortoise_voice)
                    await play_audio(result, emotion)
                    audio_parts.append(result)

                result = audio_combine(audio_parts)

            if use_bark == "1":
                if use_emotion == "1":
                    text = emotion_tts + text
                result = await bot.loop.run_in_executor(executor, generate_bark, text, bark_speaker)
                await play_audio(result, emotion)

    return result

audio_queue = deque()

async def play_audio(audio_file, emotion=None):
    global connectet_voice_channel
    global audio_queue

    if connectet_voice_channel is not None:
    
        if audio_file:  # Check if both audio_file and emotion are provided
            # Add the audio file to the queue
            audio_queue.append((audio_file, emotion))
    
        if not connectet_voice_channel.is_playing() and audio_queue:
            # If the voice channel is not currently playing audio and the queue is not empty, start playback
            audio_file, emotion = audio_queue.popleft()
            if use_unity == "1" and emotion:
                udp_server(emotion)
            connectet_voice_channel.play(discord.FFmpegPCMAudio(audio_file), after=on_audio_complete)

def on_audio_complete(_):
    # This function is called when audio playback is complete
    asyncio.run(play_audio("", ""))  # Continue playing the next audio, pass appropriate audio file and emotion

        

bot.run(discord_token)
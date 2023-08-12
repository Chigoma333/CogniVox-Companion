# CogniVox-Companion Discord Bot

CogniVox-Companion is an advanced AI-powered Discord bot that acts as your intelligent conversational companion. It leverages state-of-the-art natural language processing (NLP) capabilities provided by langchain for text processing and comprehension. The oogabooga webui API is utilized for powerful text generation, allowing the bot to engage in text-based and voice-based conversations through discord. It is planned to add Telegram in the future.

## Features

- Interactive Text-based Communication: Engage in natural and meaningful conversations with the CogniVox-Companion bot through text messages.

- Voice-to-Text Communication: Send audio files with your voice recordings, and the bot will accurately transcribe and respond to your messages.

- Text-to-Speech (TTS) Synthesis: Receive responses as both text and audio files with the bot's speech synthesis feature.

- Long-term Memory: CogniVox-Companion possesses a vector-based long-term memory through langchain, allowing it to remember context and prior interactions for more coherent conversations.

- Summarizing Memory: The bot can summarize lengthy discussions, providing concise responses to complex inquiries.

#  Tested Platform

CogniVox-Companion has been tested on Linux. As the only development platform, it is most stable and well-supported on Linux systems. However, please note that it should work Windows but it was never testet. 

Note: CogniVox-Companion is designed and supported for use on Linux only. Usage on other platforms is not supported and may result in unexpected behavior.


## Getting Started

1. Install https://github.com/oobabooga/text-generation-webui and start it with --api

2. Clone the repository:
   ```sh
   git clone https://github.com/Chigoma333/CogniVox-Companion
   cd your-project
   ```

3. Install system-level dependencies using pacman or apt:
    ```sh
    sudo pacman -S opus
    ```
    or
    ```sh
    sudo apt-get install libopus0 opus-tools
    ```
4. Install Python packages from requirements.txt:

    ```sh
    pip install -r requirements.txt
    ```

5. Rename .sampleenv to .env, add your discord token and add your oogabooga api

6. Depending on what LLM you use change the template inside oogabooga.py

7. Run the bot
   ```sh
   python3 main.py
   ```

## Usage

Invite the Bot into your discord server and chat with it

## Commands

- `/help`: Display the list of available commands.

- `/info`: Show all commands and other information.

- `/join`: Join a voice channel.

- `/leave `: Leave the current voice channel.

- `/delete_short_mem`: Deletes shortterm memory directory. (Requires manage channels permission)


- `/generate_bark_test <text>`: Generate audio from text using the Bark TTS model.


- `/generate_tortoise_test <text>`: Generate audio from text using the Tortoise TTS model.


- `/generate_whisper_test <audio_file>`: Generate text from audio using the Whisper.

## Warning: Shared Memory

CogniVox-Companion utilizes shared memory for long-term context and personalized responses. However, please be aware that this means every user interacting with the bot will be considered as the same person in the shared memory. The bot does store all conversations as memory, but it is designed to provide consistent responses based on past interactions across all users. Do not share any sensitive or personally identifiable information while interacting with the bot.

# Warning: Resource Usage

CogniVox-Companion runs entirely locally on your server to ensure data privacy. However, please be aware that the bot may consume significant resources. On average, it uses up to 10GB of VRAM, especially during memory-intensive tasks such as text generation. Make sure your server can handle these resource requirements to avoid performance issues.

## Feedback and Support

For feedback, suggestions, or bug reports, please use the github issues feature

## Contributing

I welcome contributions from the community.

## Thanks to

- pycord - https://github.com/Pycord-Development/pycord 
- bark - https://github.com/suno-ai/bark
- tortoise-tts - https://github.com/neonbjb/tortoise-tts
- whisper - https://github.com/openai/whisper
- text-generation-webui - https://github.com/oobabooga/text-generation-webui
- langchain - https://github.com/langchain-ai/langchain

## License

This project is licensed under the [GPL-3.0](LICENSE) License - see the [LICENSE](LICENSE) file for details.

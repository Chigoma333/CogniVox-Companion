from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav

import torch
import torchaudio
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_voice
from tortoise.utils.text import split_and_recombine_text



# download and load all models
def init_bark(bark_model):
    preload_models(text_use_small=bark_model)

def generate_bark(text_prompt, speaker):
    print("Speaker: " + str(speaker))
    audio_array = generate_audio(text_prompt, history_prompt=speaker)
    print("Audio generated")
    write_wav("bark.wav", SAMPLE_RATE, audio_array)
    return "bark.wav"


def init_tortoise(use_deepspeed, kv_cache, half):
    tts = TextToSpeech(use_deepspeed=use_deepspeed, kv_cache=kv_cache, half=half)
    return tts

def generate_tortoise(text_input, tts, diffusion_iterations, num_autoregressive_samples, temperature, CUSTOM_VOICE_NAME):
    extra_voice_dirs = ["voices"]
    voice_samples, conditioning_latents = load_voice(CUSTOM_VOICE_NAME, extra_voice_dirs=extra_voice_dirs)
    
    # split text into chunks because of tortoise limitations
    texts = split_and_recombine_text(text_input)

    # generate audio parts and combine them
    audio_parts = []
    for text in texts:
        print(text)
        gen = tts.tts_with_preset(text,
                            voice_samples=voice_samples,
                            conditioning_latents=conditioning_latents, 
                            preset="fast",
                            diffusion_iterations=diffusion_iterations,
                            num_autoregressive_samples=num_autoregressive_samples, 
                            cond_free = True, 
                            temperature=temperature)
        audio_parts.append(gen.squeeze(0).cpu())
    print("Audio generated")
    audio = torch.cat(audio_parts, dim=-1)
    torchaudio.save(f'tortoise.wav', audio, 24000)
    return f'tortoise.wav'
        
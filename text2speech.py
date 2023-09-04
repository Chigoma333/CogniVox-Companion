from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav

import torch
import torchaudio
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_voice
import tempfile

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline


# download and load all models
def init_bark(bark_model):
    preload_models(text_use_small=bark_model)

def generate_bark(text_prompt, speaker):
    print("Speaker: " + str(speaker))
    audio_array = generate_audio(text_prompt, history_prompt=speaker)
    print("Audio generated")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        write_wav(temp_file, SAMPLE_RATE, audio_array)
        temp_file_path = temp_file.name
    return temp_file_path


def init_tortoise(use_deepspeed, kv_cache, half, num_autoregressive_samples):
    tts = TextToSpeech(use_deepspeed=use_deepspeed, kv_cache=kv_cache, half=half, autoregressive_batch_size=num_autoregressive_samples)
    return tts
        
def generate_tortoise(text_input, tts, diffusion_iterations, num_autoregressive_samples, temperature, CUSTOM_VOICE_NAME):
    extra_voice_dirs = ["voices"]
    voice_samples, conditioning_latents = load_voice(CUSTOM_VOICE_NAME, extra_voice_dirs=extra_voice_dirs)

    print(text_input)

    gen = tts.tts_with_preset(text_input,
                    voice_samples=voice_samples,
                    conditioning_latents=conditioning_latents, 
                    preset="fast",
                    diffusion_iterations=diffusion_iterations,
                    num_autoregressive_samples=num_autoregressive_samples, 
                    cond_free = True, 
                    temperature=temperature)
    
    # Create a temporary WAV file to save the generated audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        torchaudio.save(temp_file, gen.squeeze(0).cpu(), 24000, format="wav")
        temp_file_path = temp_file.name  # Store the temporary file path

    return temp_file_path

def audio_combine(audio_parts):
    # Initialize a list to store audio tensors

    audio_tensors = []

    for file in audio_parts:
        waveform, sample_rate = torchaudio.load(file, normalize=True)
        audio_tensors.append(waveform)

    combined_audio_tensor = torch.cat(audio_tensors, dim=1)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        torchaudio.save(temp_file, combined_audio_tensor, sample_rate, format="wav")
        temp_file_path = temp_file.name
    
    return temp_file_path

def init_emotion():
    tokenizer = AutoTokenizer.from_pretrained("bergum/xtremedistil-l6-h384-go-emotion")
    model = AutoModelForSequenceClassification.from_pretrained("bergum/xtremedistil-l6-h384-go-emotion")
    return pipeline("text-classification", model=model, tokenizer=tokenizer)

def get_emotion(text_input, nlp):
    result = nlp(text_input)
    emotion_label = result[0]['label']
    return emotion_label
    
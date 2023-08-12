import whisper

def init_whisper(model):
    model = whisper.load_model(model)
    return model

def generate_whisper(model, TRANSCRIBE_FILENAME):
    output = model.transcribe(TRANSCRIBE_FILENAME)
    return output.get("text")
import openai
from typing import List
from utils.openai_wrapper import wrap_exception


@wrap_exception
def gpt_completion(
        conversation: List[dict[str]],
        temp: float = 0.9,
        model: str = "gpt-3.5-turbo-16k",  # "gpt-3.5-turbo", "gpt-4"
        tokens: int = 2048,
) -> str:

    response = openai.ChatCompletion.create(
        model=model,
        temperature=temp,
        max_tokens=tokens,
        messages=conversation,
    )

    return response['choices'][0]['message']['content']

@wrap_exception
def whisper_transcribe(
        audio_file_path: str,
) -> str:

    # mp3, mp4, mpeg, mpga, m4a, wav, webm
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(
            file=audio_file,
            model="whisper-1",
            response_format="text",
        )
        return transcript

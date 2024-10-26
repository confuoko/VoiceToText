import gdown
import whisperx
import os
import gc 
from openai import OpenAI
import tiktoken
from pathlib import Path
import shutil
 


# переменная для работы с одним файлом
DIR_NAME = 'audio_19102024.wav'

#переменные для работы с папками
FOLDER_NAME = 'analyze_folder'
DIR_FOLDER_NAME = "./analyze_folder"

# в этот текстовый файл постепенно будут сохраняться результаты транскрибации и аналитики
TXT_FILE_NAME = 'output_20.10.2024.txt'
TXT_FOLDER_NAME = 'output_26.10.2024.txt'
#ключ openai не забыть удалить
API_KEY = "kek"
client = OpenAI(api_key = API_KEY)

# просто скачивает один файл, ничего не возвращает
# на вход принимает ссылку на файл и директорию для сохранения
def upload_one_audio(google_href, directory_name):
    gdown.download(google_href, directory_name, quiet=False, fuzzy=True)

# просто скачивает папку, ничего не возвращает
# на вход принимает ссылку на папку и название папки для сохранения
def upload_folder(google_href, folder_name):
    gdown.download_folder(google_href, output=folder_name,  quiet=False)
    print('Папка скачалась')

# возвращает транскрибированный текст
# Создает файл txt
# принимает на вход название аудиофайла
def transcribe_whisperx(dir_name, fl_name):
    device = "cpu" 
    audio_file = dir_name
    compute_type = "int8"

    model = whisperx.load_model("large-v2", device, compute_type=compute_type)

    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio)

    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    
    # Вставить токен из Pyannote
    diarize_model = whisperx.DiarizationPipeline(use_auth_token='kekk', device=device)
    diarize_segments = diarize_model(audio)

    result = whisperx.assign_word_speakers(diarize_segments, result)
    
    # добавлен UNKNOWN чтобы програ не падала, если не удастся распознать говорящего
    data = [[segment.get("speaker", "UNKNOWN"), segment["text"]] for segment in result["segments"]]

    result_final = []
    current_num = None
    current_words = []

    for num, word in data:
        if num == current_num:
            current_words.append(word)
        else:
            if current_num is not None:
                result_final.append([current_num, ' '.join(current_words)])
            current_num = num
            current_words = [word]

    # Добавляем последние собранные слова
    if current_num is not None:
        result_final.append([current_num, ' '.join(current_words)])

    # записываем результат транскрибации построчно в файл
    with open(fl_name, 'a', encoding="utf8") as file:
        file.write("" + '\n')
        for element in result_final:
            file.write(str(element) + '\n')
        file.write("" + '\n')

    return str(result_final)


def sendToGpt(model, messages):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
        max_tokens = 2500
    )
    return chat_completion.choices[0].message.content

def processText(
    prompt=None,
    text_data=None,
    chat_model=
    # "gpt-4",
    "gpt-3.5-turbo",
    model_token_limit=8192,
    max_tokens=2500
):
    if not prompt:
        return "Error: Prompt is missing. Please provide a prompt."
    if not text_data:
        return "Error: Text data is missing. Please provide some text data."

    # Initialize the tokenizer
    tokenizer = tiktoken.encoding_for_model(chat_model)

    # Encode the text_data into token integers
    token_integers = tokenizer.encode(text_data)

    # Split the token integers into chunks based on max_tokens
    chunk_size = max_tokens - len(tokenizer.encode(prompt))
    chunks = [
        token_integers[i : i + chunk_size]
        for i in range(0, len(token_integers), chunk_size)
    ]

    # Decode token chunks back to strings
    chunks = [tokenizer.decode(chunk) for chunk in chunks]
    responses = []
    messages = [
        {"role": "user", "content": prompt},
        {
            "role": "user",
            "content": "Чтобы пояснить контекст к запросу, я буду присылать текст частями. Когда я закончу, я напишу тебе 'ВСЕ ЧАСТИ ВЫСЛАНЫ'. Не отвечай пока не получишь все части.",
        },
    ]

    for chunk in chunks:
        messages.append({"role": "user", "content": chunk})
        # Check if total tokens exceed the model's limit and remove oldest chunks if necessary
        while (sum(len(tokenizer.encode(msg["content"])) for msg in messages) > model_token_limit):
            messages.pop(1)

    messages.append({"role": "user", "content": "ВСЕ ЧАСТИ ВЫСЛАНЫ"})

    response = sendToGpt(model=chat_model, messages=messages)
    final_response = response.strip()
    responses.append(final_response)

    return responses


# функция для аналитики: саммари по аудио в целом и по каждому говорящему
# ничего не возвращает, записывает аналитику в файл TXT_FILE_NAME
# принимает на вход транскрибированный текст
def gpt_magic(raw_text):
    content = raw_text

    text = processText(prompt = "Выведи мне абзацы: 0. Тема диалога очень кратко, 1. суть текста, 2. очень краткую суть текста, 3. выжимку по каждому говорящему", text_data = content)

    text_2 = processText(prompt = "Сформулируй список из 20 самых часто встречающихся слов, касающихся обсуждаемых проблем", text_data = content)

    text_3 = processText(prompt = "Сформулируй 5 основных проблем, которые обсуждали говорящие. Напечатай каждую проблему с новой строки по убыванию серьезности и важности", text_data = content)
    
    # записали красиво в файл
    with open(TXT_FILE_NAME, 'a', encoding="utf8") as file:
        file.write(text[0] + '\n')
        file.write(text_2[0] + '\n')
        file.write(text_3[0] + '\n')

# функция для обработки одного аудио
# возвращает текст: транскрибация + саммари
# на вход принимает ссылку на аудиофайл
def down(href_name): 
    # 1. скачиваем файл в директорию
    upload_one_audio(href_name, DIR_NAME)

    # 2. транскрибируем скачанный файл и возвращаем текст
    output_text = transcribe_whisperx(DIR_NAME, TXT_FILE_NAME)
    
    # 3. генерируем саммари от gpt
    gpt_magic(output_text)

    # 4. забираем текст из TXT_FILE_NAME и записываем его в переменную для перечачи в письмо
    with open(TXT_FILE_NAME, encoding="utf8") as file:
        content_2 = file.read()
    # возвращаем красивый текст для письма    
    return content_2

def down_2(href_name):
    # 1. скачиваем файл в директорию FOLDER_NAME
    upload_folder(href_name, FOLDER_NAME)
    print('функция upload_folder выполнена')

    # 2. транскрибируем каждую аудиозапись и составляем совокупный текст
    files = os.listdir(DIR_FOLDER_NAME)
    dirs = []
    for file in files:
        dir = FOLDER_NAME + '/' + file
        dirs.append(dir)
    

    big_text = []
    # транскрибируем каждую аудио
    for dir in dirs:
        # 1.Запишем название аудио
        with open(TXT_FOLDER_NAME, 'a', encoding="utf8") as file:
            naming = str(dir)
            file.write(naming)
        # 2. Запишем сам текст
        transcribe_whisperx(dir, TXT_FOLDER_NAME)
        print('готово')
    
    # считываем текст всех аудио в переменную
    with open(TXT_FOLDER_NAME, encoding="utf8") as file:
        big_text = file.read()

    return str(big_text)

def delete_files(name_of_text_file, name_of_audio_file):
    t = Path(f'{name_of_text_file}')
    a = Path(f'{name_of_audio_file}')

    t.unlink()
    a.unlink()

def delete_folder_and_txt(name_of_text_file, name_of_folder):
    t = Path(f'{name_of_text_file}')
    t.unlink()

    shutil.rmtree(name_of_folder)


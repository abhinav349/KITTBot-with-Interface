from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
import os
from sqlitedict import SqliteDict
import speech_recognition as sr
import pyttsx3
from playsound import playsound
import webbrowser
import platform
import os
import time as tm
import datetime
import openai
from bs4 import BeautifulSoup
import requests

def save(key, value, cache_file="cache.sqlite3"):
    try:
        with SqliteDict(cache_file) as mydict:
            mydict[key] = value # Using dict[key] to store
            mydict.commit() # Need to commit() to actually flush the data
    except Exception as ex:
        print("Error during storing data (Possibly unsupported):", ex)

def index(request):
    request.apikey = SqliteDict('cache.sqlite3')['apikey']
    request.rate = SqliteDict('cache.sqlite3')['rate']
    request.now = '/'
    if request.method=="POST":
        if request.POST.get('start') == "start":
            os.system("python3 bot.py")
            return redirect("/#start")
        elif request.POST.get('start_background') == "start_background":
            os.system("python3 bot-infinite.py")
            return redirect("/#start")
        # elif request.POST.get('start_interactive') == "start_interactive":
        #     return render(request, "interface.html")
        elif request.POST.get('settings') == "settings":
            request.now = 'settings'
            save('apikey', request.POST.get('apikey'))
            save('rate', request.POST.get('rate'))
            save('gender', request.POST.get('flexRadioDefault'))
            request.apikey = SqliteDict('cache.sqlite3')['apikey']
            request.rate = SqliteDict('cache.sqlite3')['rate']
            return redirect("/#settings", now = 'settings')
    return render(request, "index.html")

def interactive(request):
    if request.method=="POST":
        if request.POST.get('start_interface') == "start_interface":
            def load(key, cache_file="cache.sqlite3"):
                try:
                    with SqliteDict(cache_file) as mydict:
                        value = mydict[key] # No need to use commit(), since we are only loading data!
                    return value
                except Exception as ex:
                    print("Error during loading data:", ex)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

            openai.api_key = load('apikey')
            model_engine = "gpt-3.5-turbo"
            user_OS = platform.system()

            def ask_chatgpt(question):
                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    n=1,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant with exciting, interesting things to say."},
                        {"role": "user", "content": question},
                    ])

                message = response.choices[0]['message']
                return message['content']
            
            def SpeakText(command):
                # Initialize the engine
                engine = pyttsx3.init('nsss')
                voices = engine.getProperty('voices')
                engine.setProperty('voice', voices[15].id)  # changing index, changes voices. 1 for female
                engine.setProperty('rate', int(load('rate')))  # setting up new voice rate
                engine.say(command)
                engine.runAndWait()

            def doTask(MyText):
                if 'open' in MyText:
                    if 'chrome' in MyText:
                        SpeakText("Opening Chrome")
                        user_OS = platform.system()
                        chrome_path_windows = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
                        chrome_path_linux = '/usr/bin/google-chrome %s'
                        chrome_path_mac = 'open -a /Applications/Google\ Chrome.app %s'
                        chrome_path = ''
                        link = 'https://www.google.com'

                        if user_OS == 'Windows':
                            chrome_path = chrome_path_windows
                        elif user_OS == 'Linux':
                            chrome_path = chrome_path_linux
                        elif user_OS == 'Darwin':
                            chrome_path = chrome_path_mac
                        elif user_OS == 'Java':
                            chrome_path = chrome_path_mac
                        else:
                            webbrowser.open_new_tab(link)

                        webbrowser.get(chrome_path).open_new_tab(link)

                    elif 'whatsapp' in MyText:
                        SpeakText("Opening Whatsapp")
                        os.system("open /Applications/Whatsapp.localized/WhatsApp.app")

                    elif 'spotify' in MyText:
                        SpeakText("Opening Spotify")
                        os.system("open /Applications/Spotify.app")

                    elif 'word' in MyText:
                        if 'microsoft' in MyText:
                            SpeakText("Opening Microsoft Word")
                            os.system("open /Applications/'Microsoft Word.app'")
                        else:
                            SpeakText("Did you mean Microsoft Word")
                            while True:
                                str = listen(1)
                                if 'yes' in str[0]:
                                    SpeakText("Opening Microsoft Word")
                                    os.system("open /Applications/'Microsoft Word.app'")
                                    break
                                elif 'no' in str[0]:
                                    SpeakText("Then please tell what do you mean")
                                    break
                                elif str[1]:
                                    SpeakText("I did not got a response of Yes or No")

                    elif 'excel' in MyText:
                        if 'microsoft' in MyText:
                            SpeakText("Opening Microsoft Excel")
                            os.system("open /Applications/'Microsoft Excel.app'")
                        else:
                            SpeakText("Did you mean Microsoft Excel")
                            while(True):
                                str = listen(1)
                                if 'yes' in str[0]:
                                    SpeakText("Opening Microsoft Excel")
                                    os.system("open /Applications/'Microsoft Excel.app'")
                                    break
                                elif 'no' in str[0]:
                                    SpeakText("Then please tell what do you mean")
                                    break
                                elif str[1]:
                                    SpeakText("I did not got a response of Yes or No")
                    SpeakText("Thank You! for using KITT")
                    exit(0)

                elif 'temperature' in MyText or 'weather' in MyText:
                    SpeakText("Please tell the name of the city")
                    while True:
                        city_data = listen(1)
                        if city_data[1] == 0:
                            continue
                        city = city_data[0]
                        city = city+" weather"
                        city = city.replace(" ", "+")
                        res = requests.get(
                            f'https://www.google.com/search?q={city}&oq={city}&aqs=chrome.0.35i39l2j0l4j46j69i60.6128j1j7&sourceid=chrome&ie=UTF-8',
                            headers=headers)
                        print("Searching...\n")
                        soup = BeautifulSoup(res.text, 'html.parser')
                        location = soup.select('#wob_loc')[0].getText().strip()
                        time = soup.select('#wob_dts')[0].getText().strip()
                        info = soup.select('#wob_dc')[0].getText().strip()
                        weather = soup.select('#wob_tm')[0].getText().strip()
                        print(f"Temperature of {city_data[0]} on {time} is {weather} °C with {info}.")
                        SpeakText(f"Temperature of {city_data[0]} on {time} is {weather} °C with {info}.")
                        break
                    SpeakText("Thank You! for using KITT")
                    exit(0)

                elif 'date' in MyText:
                    print(datetime.date.today().strftime('%A %d %B %Y'))
                    SpeakText(datetime.date.today().strftime('%A %d %B %Y'))
                    SpeakText("Thank You! for using KITT")
                    exit(0)

                elif 'time' in MyText:
                    curr_time = tm.strftime("%H:%M:%S", tm.localtime())
                    print(f"Current Time is : {curr_time}")
                    SpeakText(f"Current Time is : {curr_time}")
                    SpeakText("Thank You! for using KITT")
                    exit(0)

                # elif 'exit' in MyText:
                #     SpeakText("Are you sure you want to exit. Please answer in Yes or No!")
                #     while True:
                #         ext = listen(1)
                #         if ext[1] == 0:
                #             continue
                #         if 'yes' in ext[0]:
                #             SpeakText("Thank You! for using KITT")
                #             exit(0)
                #         elif 'no' in ext[0]:
                #             break
                #         elif ext[1]:
                #             SpeakText("Please answer Yes or No")
                else:
                    while True:
                        try:
                            x = ask_chatgpt(MyText)
                            print(x)
                            if '```' in x:
                                str = "```"
                                str_find1 = x.find(str)
                                str_find2 = x.find(str,str_find1+3)
                                SpeakText(f'{x[0:str_find1]}')
                                SpeakText(f'{x[str_find2:]}')
                            else:
                                SpeakText(x)
                            break
                        except Exception as e:
                            print("Error asking ChatGPT", e)
                            break
                    exit(0)
            
            def listen(flag):
                lst = []
                # Initialize the recognizer
                r = sr.Recognizer()
                with sr.Microphone() as source2:
                    try:
                        # use the microphone as source for input.

                        # for playing note.wav file
                        if flag:
                            playsound('sound.mp3')


                        # wait for a second to let the recognizer
                        # adjust the energy threshold based on
                        # the surrounding noise level
                        r.adjust_for_ambient_noise(source2, duration=0.1)

                        # listens for the user's input
                        print("listening ...")
                        audio2 = r.listen(source2)

                        # Using google to recognize audio
                        MyText = r.recognize_google(audio2)
                        MyText = MyText.lower()
                        print("Did you say ", MyText)
                        lst.append(MyText)
                        flag = 1
                        lst.append(flag)
                        # SpeakText(MyText)

                    except sr.RequestError as e:
                        flag = 0
                        lst.append(" ")
                        lst.append(flag)
                        print("Could not request results; {0}".format(e))

                    except sr.UnknownValueError:
                        flag = 0
                        lst.append(" ")
                        lst.append(flag)
                        print("Nothing to say")
                    return lst

            SpeakText("Hello, I am KITT! powered with ChatGPT. How can I help you?")
            lst = listen(1)
            if lst[1]:
                doTask(lst[0])
            lst = listen(lst[1])
            
    return render(request, "interactive.html")

    
        
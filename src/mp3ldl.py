from pytube import YouTube
from moviepy.editor import *
import requests
import os
import time
import tkinter
import threading
from tkinter import filedialog


class mp3Downloader(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.titles = []
        self.bad_titles = []
        self.delay_loop_download = 0.1
        self.delay_loop_main = 0.5
        self.files_directory = "C:\mp3ldl"
        self.on_download_start = threading.Event()

    def run(self):
        while True:
            if self.on_download_start.is_set():
                self.downloadTitles(self.titles)
                self.on_download_start.clear()
            time.sleep(self.delay_loop_main)

    def __downloadAudioMp4FromYoutube(self, url, filepath):
        try:
            youtube = YouTube(url)
            return youtube.streams.filter(only_audio=True, subtype="mp4").first().download(filepath)
        except:
            raise Exception("Error: Either a wrong URL or the right Stream isn't available")

    def __convertAudioMp4ToMp3(self, filename):
        if "mp4" not in filename:
            raise Exception("Error: wrong file format")
        mp4_filename = filename
        mp3_filename = filename.replace("mp4", "mp3")

        mp4_clip = AudioFileClip(mp4_filename)
        mp4_clip.write_audiofile(mp3_filename)

        mp4_clip.close()
        os.remove(mp4_filename)

    def __getVideoUrlByFirstSearchResult(self, search_term):
        std_url = "https://m.youtube.com/results?search_query="
        try:
            page = requests.get(std_url + search_term)
        except:
            raise Exception("Error: invalid request")

        words_in_title = search_term.split(" ")
        id = page.text.split('"videoId":"')[1].split('"')[0]
        title = page.text.split('"text":')[1].split('}')[0]

        for i in words_in_title:
            if i in title \
                    or i.upper() in title \
                    or i.lower() in title \
                    or i.capitalize() in title:
                break
            else:
                raise Exception("Error: right video could not be found")

        return "https://www.youtube.com/watch?v=" + id


    def downloadTitles(self, titles):
        self.bad_titles.clear()
        for i in titles:
            if i == "":
                break
            try:
                url = self.__getVideoUrlByFirstSearchResult(i)
                filename = self.__downloadAudioMp4FromYoutube(url, self.files_directory + "/mp3ldl_files/")
                self.__convertAudioMp4ToMp3(filename)
            except:
                self.bad_titles.append(i)

            time.sleep(self.delay_loop_download)

        print("\n\nDownload complete!\n\n")
        print("Failed to download:\n")
        if len(self.bad_titles) == 0:
            print("None, download was succesful!")
        for i in self.bad_titles:
            print(i)


class mp3ldlGUI(tkinter.Tk):
    def __init__(self, mp3dl):
        tkinter.Tk.__init__(self)
        self.update_delay_ms = 500
        self.title("Mp3 List Downloader")
        self.resizable(False, False)
        self.songlist = ""

        self.frame_songlist = tkinter.Frame(
            self,
            width=100,
            height=200)
        self.frame_download = tkinter.Frame(
            self,
            width=100,
            height=5)
        self.frame_directoryDialog = tkinter.Frame(
            self,
            width=100,
            height=5)

        self.frame_songlist.grid(row=0, column=0)
        self.frame_directoryDialog.grid(row=1, column=0)
        self.frame_download.grid(row=2, column=0)

        self.text_songlist = tkinter.Text(self.frame_songlist)
        self.scrollbar_songlist = tkinter.Scrollbar(self.frame_songlist, command=lambda: [self.text_songlist.yview])
        self.text_songlist["yscrollcommand"] = self.scrollbar_songlist.set
        self.scrollbar_songlist.pack(side="right", fill="y")
        self.text_songlist.pack()

        self.filedialog_label_filename = tkinter.Label(self.frame_directoryDialog)
        self.filedialog_label_filename.pack()

        self.button_download = tkinter.Button(self.frame_download, text="download")
        self.button_download.pack()

    def getSonglist(self, args=0):
        self.songlist = self.text_songlist.get("1.0", "end").split('\n')
        return self.songlist


def handleDownload(gui, mp3dl):
    mp3dl.files_directory = tkinter.filedialog.askdirectory()
    mp3dl.titles = gui.getSonglist()
    mp3dl.on_download_start.set()


if __name__ == "__main__":
    mp3dl = mp3Downloader()
    mp3dl.start()
    gui = mp3ldlGUI(mp3dl)

    gui.filedialog_label_filename.config(text=mp3dl.files_directory)
    gui.button_download.config(command=lambda: [
        handleDownload(gui, mp3dl),
        gui.filedialog_label_filename.config(text=mp3dl.files_directory)
    ])

    gui.mainloop()

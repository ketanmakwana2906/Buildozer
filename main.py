import os
import shutil
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from pytube import YouTube, Playlist
from moviepy.editor import *
import subprocess

class YouTubeDownloader(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        self.url_label = Label(text="Enter YouTube URL:")
        self.layout.add_widget(self.url_label)

        self.url_entry = TextInput()
        self.layout.add_widget(self.url_entry)

        self.option_label = Label(text="Select option:")
        self.layout.add_widget(self.option_label)

        self.option_dropdown = DropDown()
        options = ["Video", "Playlist"]
        for option in options:
            btn = Button(text=option, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.option_dropdown.select(btn.text))
            self.option_dropdown.add_widget(btn)
        self.option_button = Button(text='Choose Option')
        self.option_button.bind(on_release=self.option_dropdown.open)
        self.option_dropdown.bind(on_select=lambda instance, x: setattr(self.option_button, 'text', x))
        self.layout.add_widget(self.option_button)

        self.quality_label = Label(text="Select quality:")
        self.layout.add_widget(self.quality_label)

        self.quality_dropdown = DropDown()
        qualities = ["360p", "720p", "1080p", "1440p", "2160p"]
        for quality in qualities:
            btn = Button(text=quality, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.quality_dropdown.select(btn.text))
            self.quality_dropdown.add_widget(btn)
        self.quality_button = Button(text='Choose Quality')
        self.quality_button.bind(on_release=self.quality_dropdown.open)
        self.quality_dropdown.bind(on_select=lambda instance, x: setattr(self.quality_button, 'text', x))
        self.layout.add_widget(self.quality_button)

        self.location_label = Label(text="Select download location:")
        self.layout.add_widget(self.location_label)

        self.location_button = Button(text="Browse")
        self.location_button.bind(on_release=self.browse_location)
        self.layout.add_widget(self.location_button)

        self.location_label1 = Label()
        self.layout.add_widget(self.location_label1)

        self.download_button = Button(text="Download")
        self.download_button.bind(on_release=self.download)
        self.layout.add_widget(self.download_button)

        return self.layout
    
    def browse_location(self, instance):
        popup_layout = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView()
        file_chooser.bind(on_submit=self.select_location)
        popup_layout.add_widget(file_chooser)
        popup = Popup(title='Select Directory', content=popup_layout, size_hint=(0.9, 0.9))
        popup.open()

    def select_location(self, instance, value):
        self.location_label1.text = value
        instance.parent.parent.parent.dismiss()

    def download(self, instance):
        url = self.url_entry.text
        option = self.option_button.text
        quality = self.quality_button.text
        location = self.location_label1.text

        if not url:
            self.show_message("Error", "Please enter a valid YouTube URL.")
            return

        try:
            if option == "Video":
                if quality in ["1080p", "1440p", "2160p"]:
                    path = os.path.join(location, 'temp')
                    videoname, audioname = self.download_video_audio(url, path, quality)
                    self.merge_video_audio(location, videoname, audioname)
                    self.show_message("Success", "Video downloaded and merged successfully.")
                else:
                    yt = YouTube(url)
                    video = yt.streams.filter(progressive=True, file_extension='mp4', resolution=quality).first()
                    video.download(location)
                    self.show_message("Success", "Video downloaded successfully.")
            elif option == "Playlist":
                playlist = Playlist(url)
                for video_url in playlist.video_urls:
                    if quality in ["1080p", "1440p", "2160p"]:
                        path = os.path.join(location, 'temp')
                        videoname, audioname = self.download_video_audio(video_url, path, quality)
                        self.merge_video_audio(location, videoname, audioname)
                    else:
                        yt = YouTube(video_url)
                        video = yt.streams.filter(progressive=True, file_extension='mp4', resolution=quality).first()
                        video.download(location)
                self.show_message("Success", "Playlist downloaded successfully.")
        except Exception as e:
            self.show_message("Error", f"An error occurred: {str(e)}")

    def download_video_audio(self, youtube_url, output_path, quality):
        yt = YouTube(youtube_url)
        video_stream = yt.streams.get_by_itag({
            "1080p": 137,
            "1440p": 271,
            "2160p": 313
        }[quality])
        videoname = video_stream.default_filename
        videopath = f"video_{videoname}"
        video_stream.download(output_path=output_path, filename=videopath)

        audio_stream = yt.streams.get_by_itag(251)
        audioname = audio_stream.default_filename
        audio_stream.download(output_path=output_path)

        return videoname, audioname

    def merge_video_audio(self, location, videoname, audioname):
        videopath = f"video_{videoname}"
        video_file = os.path.join(location, 'temp', videopath)
        audio_file = os.path.join(location, 'temp', audioname)
        videoname_mp4 = os.path.splitext(videoname)[0] + '.mp4'
        merged_file = os.path.join(location, videoname_mp4)
        subprocess.run(["ffmpeg", "-i", video_file, "-i", audio_file, "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", merged_file])
        directory_path = os.path.join(location, 'temp')
        shutil.rmtree(directory_path)

    def show_message(self, title, message):
        popup_layout = BoxLayout(orientation='vertical')
        popup_layout.add_widget(Label(text=message))
        close_button = Button(text='Close')
        popup_layout.add_widget(close_button)
        popup = Popup(title=title, content=popup_layout, size_hint=(0.5, 0.5))
        close_button.bind(on_release=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    YouTubeDownloader().run()

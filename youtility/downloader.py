import os
import random

import pytube.exceptions
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton, QComboBox, QFileDialog, QHBoxLayout, \
    QSpacerItem, QLabel, QListWidgetItem
from qfluentwidgets import (LineEdit,
                            ScrollArea, StrongBodyLabel, MessageBox, CheckBox, ListWidget)
from pytube import YouTube
from consts import msgs, extension
import threading


class YoutubeVideo(QWidget):
    def __init__(self):
        super().__init__()

        spacer_item_small = QSpacerItem(0, 10)
        spacer_item_medium = QSpacerItem(0, 20)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # YouTube Link Entry
        self.link_layout = QHBoxLayout()
        self.main_layout.addLayout(self.link_layout)
        self.link_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.link_entry = LineEdit(self)
        self.link_entry.textChanged.connect(self.get_quality)
        self.link_entry.setPlaceholderText("Enter YouTube Video Link: ")
        self.link_layout.addWidget(self.link_entry)

        self.main_layout.addSpacerItem(spacer_item_small)

        # Option menu for Quality
        self.quality_layout = QHBoxLayout()
        self.options_layout = QHBoxLayout()
        self.main_layout.addLayout(self.quality_layout)
        self.main_layout.addLayout(self.options_layout)
        self.quality_menu = QComboBox()
        self.quality_menu.addItems(["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"])
        self.quality_layout.addWidget(self.quality_menu)
        self.options_layout.addSpacerItem(spacer_item_medium)
        self.thumbnail_url_checkbox = CheckBox('Copy Thumbnail Link', self)
        self.captions_checkbox = CheckBox('Download Captions', self)
        self.captions_checkbox.stateChanged.connect(self.trigger_captions_list)

        self.options_group = QGroupBox("Additional Options")
        self.options_group_layout = QVBoxLayout(self.options_group)
        self.options_group_layout.addWidget(self.captions_checkbox)
        self.options_group_layout.addWidget(self.thumbnail_url_checkbox)
        self.options_layout.addWidget(self.options_group)

        self.main_layout.addSpacerItem(spacer_item_small)

        self.captions_layout = QHBoxLayout()
        self.captions_layout.addSpacerItem(spacer_item_medium)
        self.main_layout.addLayout(self.captions_layout)

        # Download Button
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download)
        self.button_layout.addWidget(self.download_button)

        # GIF Loading Screen
        self.gif_layout = QHBoxLayout()
        self.main_layout.addLayout(self.gif_layout)
        self.loading_label = QLabel()
        self.main_layout.addWidget(self.loading_label)

        # Progress Area
        self.count_layout = QHBoxLayout()
        # Create a QListWidget to display downloading status
        self.download_list_widget = ListWidget()
        self.count_layout.addWidget(self.download_list_widget)
        self.main_layout.addLayout(self.count_layout)

        self.setLayout(self.main_layout)

    def get_quality(self):
        url = self.link_entry.text()
        try:
            youtube = pytube.YouTube(url)
            streams = youtube.streams.filter(progressive=False)
            self.quality_menu.clear()
            for stream in streams:
                self.quality_menu.addItem(stream.resolution)
        except pytube.exceptions.RegexMatchError:
            pass

    def trigger_captions_list(self):
        if self.captions_checkbox.isChecked():
            link = self.link_entry.text()
            if link == "":
                msg = random.choice(msgs)
                w = MessageBox(
                    'No URL Found',
                    msg,
                    self
                )
                self.captions_checkbox.setChecked(False)
                w.yesButton.setText('Alright Genius 🤓')
                w.cancelButton.setText('Yeah let me try again 🤝')

                if w.exec():
                    pass

            else:
                try:
                    youtube_client = YouTube(link)
                    captions = youtube_client.captions
                    language_names = []
                    language_dict = {}

                    for caption in captions:
                        language_name = caption.name.split(" - ")[0]  # Extracting the main language name
                        language_code = caption.code.split(".")[0]  # Extracting the main language code

                        if language_name not in language_dict:
                            language_dict[language_name] = language_code

                        if language_name not in language_names:
                            language_names.append(language_name)

                    self.caption_label = StrongBodyLabel('Caption Language', self)
                    self.captions_layout.addWidget(self.caption_label)
                    self.caption_list = QComboBox()
                    self.caption_list.addItems(language_names)
                    self.captions_layout.addWidget(self.caption_list)

                except pytube.exceptions.RegexMatchError:
                    pass

        else:
            self.caption_list.hide()
            self.caption_label.hide()


    def download(self):
        def get_gif():
            gifs = ["loading.gif", "loading_1.gif", "loading_2.gif"]
            gif = random.choice(gifs)
            gif_path = "resource/misc/" + gif
            return gif_path

        link = self.link_entry.text()
        download_captions = False
        copy_thumbnail_link = False
        quality = self.quality_menu.currentText()

        if link != "":
            if self.captions_checkbox.isChecked():
                download_captions = True
            else:
                download_captions = False

            if self.thumbnail_url_checkbox.isChecked():
                copy_thumbnail_link = True
            else:
                copy_thumbnail_link = False

            youtube_client = YouTube(link)
            title = youtube_client.title
            youtube_client.streams.filter(file_extension=extension)

            self.list_item = QListWidgetItem(
                "Downloading: " + title)  # Assuming title is fetched from youtube_client.title
            self.download_list_widget.addItem(self.list_item)
            # Get available streams for the video
            streams = youtube_client.streams.filter(progressive=False)

            # Get the selected quality option
            choice = self.quality_menu.currentIndex()
            stream = streams[choice]
            if not download_captions:
                save_path, _ = QFileDialog.getSaveFileName(self, "Save file", title, "Video Files (*.mp4)")
                save_path = str(save_path)
                stream.download(save_path)

            if download_captions:
                captions = youtube_client.captions
                language_dict = {}
                for caption in captions:
                    language_name = caption.name.split(" - ")[0]  # Extracting the main language name
                    language_code = caption.code.split(".")[0]  # Extracting the main language code

                    if language_name not in language_dict:
                        language_dict[language_name] = language_code

                lang_get = self.caption_list.currentText()
                lang = language_dict.get(lang_get)
                print(lang)
                default_folder = os.path.expanduser("~")
                folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", default_folder)
                caption_file_name = "captions.srt"

                if folder_path:
                    default_filename = title
                    save_path = os.path.join(folder_path, default_filename)

                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                    stream.download(save_path)
                    caption_dwnld = youtube_client.captions.get_by_language_code(lang)
                    caption_dwnld = caption_dwnld.generate_srt_captions()
                    with open(folder_path, 'w') as file:
                        pass
                        file.write(caption_dwnld)

            self.movie = QMovie(get_gif())
            self.loading_label.setMovie(self.movie)
            self.movie.start()

    def complete_download(self, title):
        self.list_item.setText("Downloaded: " + title)
        self.loading_label.hide()
        print("DONE")

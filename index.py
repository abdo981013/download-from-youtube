####################################
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.uic  import  loadUiType

import os
from os import path
import sys

import pafy
import humanize
####################################
ui_file,_ = loadUiType(path.join(path.dirname(__file__),"main.ui"))

class MainApp(QMainWindow,ui_file):
    def __init__(self,parent=None):
        super(MainApp,self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.Handel_Buttons()
        self.Handel_window()
        self.downloader = DownLoader()
        thread = QtCore.QThread(self)
        thread.start()
        self.downloader.moveToThread(thread)
        self.downloader.qualitiesChanged.connect(self.update_qualityes)
        self.downloader.video_download_speed.connect(self.lcdNumber_3.display)
        self.downloader.video_download_speed.connect(self.video_download_speed)
        self.downloader.video_name.connect(self.video_name_wd)
        self.downloader.playlist_Changed.connect(self.playlist_information)
        self.downloader.progress_video.connect(self.progress_bar.setValue)
        self.downloader.playlist_download_speed.connect(self.lcdNumber_2.display)
        self.downloader.playlist_download_speed.connect(self.playlist_download_rate)
        self.downloader.playlist_video_name.connect(self.playlist_vide_name)
        self.downloader.progress_playlist.connect(self.progress_bar2.setValue)
        self.downloader.finished_video.connect(self.on_finished_video)
        self.downloader.finished_playlist.connect(self.on_finshid_playlist)

    def Handel_window(self):
        self.setWindowTitle('Youtube Downloader')
        self.tabWidget.tabBar().setVisible(False)

    def Handel_Buttons(self):
        self.video_search.clicked.connect(self.on_clicked_quality)
        self.video_start.clicked.connect(self.download)
        self.playlist_search.clicked.connect(self.video_playlist_search)
        self.playlist_start.clicked.connect(self.playlist_start_download)
        self.video_save.clicked.connect(self.Handel_Save_video)
        self.playlist_save.clicked.connect(self.Handel_Save_playlist)
        self.video_tab.clicked.connect(self.Tab_video)
        self.playlist_tab.clicked.connect(self.Tab_playlist)

    def Handel_Save_video(self):
        save = QFileDialog.getExistingDirectory(self, "Select Place")
        self.save_video.setText(save)
    def Handel_Save_playlist(self):
        save = QFileDialog.getExistingDirectory(self, "Select Place Folder Playlist")
        self.save_playlist.setText(save)

    def Tab_video(self):
        self.tabWidget.setCurrentIndex(0)
    def Tab_playlist(self):
        self.tabWidget.setCurrentIndex(1)

    @QtCore.pyqtSlot()
    def on_finished_video(self):
        ##########video############
        QMessageBox.information(self,'Download Complet','Dowload Is Finished')
        self.video_url.setText('')
        self.save_video.setText('')
        self.combo_box.clear()
        self.label_6.setText('')
        self.lcdNumber_3.display(0)
        self.progress_bar.setValue(0)

    @QtCore.pyqtSlot()
    def on_finshid_playlist(self):
        #########playlist##########
        QMessageBox.information(self,'Download Complet','Dowload Is Finished')
        self.playlist_url.setText('')
        self.save_playlist.setText('')
        self.save_playlist.setText('')
        self.label_3.setText('')
        self.lcdNumber.display(0)
        self.lcdNumber_2.display(0)
        self.progress_bar2.setValue(0)


#######################video########################
    @QtCore.pyqtSlot()
    def on_clicked_quality(self):
        video_url = self.video_url.text()
        QtCore.QMetaObject.invokeMethod(self.downloader, "video_quality",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(str, video_url))

    @QtCore.pyqtSlot(list)
    def update_qualityes(self, types_of_video):
        for t in types_of_video:
            self.combo_box.addItem(str(t), t)
    @QtCore.pyqtSlot(float)
    def video_download_speed(self ,rate_lcd):
        if rate_lcd > 1000:
            self.label_6.setText('MB/s')
        else:
            self.label_6.setText('KB/s')

    @QtCore.pyqtSlot(str)
    def video_name_wd(self ,video_name):
        self.list_video_download_2.addItem(video_name)

    @QtCore.pyqtSlot()
    def download(self):
        video_url = self.video_url.text()
        video_save = self.save_video.text()
        d = self.combo_box.currentData()
        QtCore.QMetaObject.invokeMethod(self.downloader, "video_download",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(object, d),
                                        QtCore.Q_ARG(str, video_save),
                                        QtCore.Q_ARG(str, video_url))

    #####################playlist##############################
    @QtCore.pyqtSlot()
    def video_playlist_search(self):
        playlist_url = self.playlist_url.text()
        QtCore.QMetaObject.invokeMethod(self.downloader, "playlist_search",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(str, playlist_url))

    @QtCore.pyqtSlot(list)
    def playlist_information(self, videos):
        for video in videos:
            qualitey = video['pafy']
            best = qualitey.getbest(preftype='mp4')
            self.label_16.setText('{}'.format(best))
            self.lcdNumber.display(len(videos))

    @QtCore.pyqtSlot(float)
    def playlist_download_rate(self, rate_lcd):
        if rate_lcd > 1000:
            self.label_3.setText('MB/s')
        else:
            self.label_3.setText('KB/s')

    @QtCore.pyqtSlot(str)
    def playlist_vide_name(self, playlist_video_name):
        self.list_video_download.addItem(playlist_video_name)

    @QtCore.pyqtSlot()
    def playlist_start_download(self):
        playlist_url = self.playlist_url.text()
        playlist_save = self.save_playlist.text()
        QtCore.QMetaObject.invokeMethod(self.downloader, "video_playlist_download",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(str, playlist_url),
                                        QtCore.Q_ARG(str, playlist_save))

class DownLoader(QtCore.QObject):
    progress_video = QtCore.pyqtSignal(int)
    video_download_speed = QtCore.pyqtSignal(float)
    video_name = QtCore.pyqtSignal(str)
    progress_playlist = QtCore.pyqtSignal(int)
    playlist_download_speed = QtCore.pyqtSignal(float)
    qualitiesChanged = QtCore.pyqtSignal(list)
    playlist_Changed = QtCore.pyqtSignal(list)
    playlist_video_name = QtCore.pyqtSignal(str)
    finished_video = QtCore.pyqtSignal()
    finished_playlist = QtCore.pyqtSignal()

    @QtCore.pyqtSlot(str)
    def video_quality(self,video_url):
        pafy_video = pafy.new(video_url)
        types_of_video = pafy_video.videostreams
        self.qualitiesChanged.emit(types_of_video)

    @QtCore.pyqtSlot(object, str ,str)
    def video_download(self, d, save,url):
        d.download(filepath=save,callback=self.callback)
        pafy_video = pafy.new(url)
        video_name_ = pafy_video.title
        self.video_name.emit(video_name_)

    def callback(self,total, recvd, ratio, rate, eta):
        val = int(ratio * 100)
        rate_lcd = rate
        self.progress_video.emit(val)
        self.video_download_speed.emit(rate_lcd)
        if val == 100:
            self.finished_video.emit()

    ######################playlist######################
    @QtCore.pyqtSlot(str)
    def playlist_search(self,playlist_url):
        playlist_pafy = pafy.get_playlist(playlist_url)
        videos = playlist_pafy['items']
        self.playlist_Changed.emit(videos)

    @QtCore.pyqtSlot(str,str)
    def video_playlist_download(self,playlist_url,playlist_save):
        playlist_pafy = pafy.get_playlist(playlist_url)
        videos = playlist_pafy['items']
        a = 0
        for video in videos:
            video_ = video['pafy']
            best = video_.getbest(preftype='mp4')
            best.download(filepath=playlist_save,callback=self.play_pro)
            video_name = playlist_pafy['items'][a]['playlist_meta']['title']
            self.playlist_video_name.emit(video_name)
            a +=1
        self.finished_playlist.emit()

    def play_pro(self,total, recvd, ratio, rate, eta):
        val = int(ratio * 100)
        rate_lcd = rate
        self.playlist_download_speed.emit(rate_lcd)
        self.progress_playlist.emit(val)

def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()

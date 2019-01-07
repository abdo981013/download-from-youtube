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
        self.downloader.playChanged.connect(self.playlist_videos)
        self.downloader.progressChanged.connect(self.progress_bar.setValue)
        self.downloader.progressChanged.connect(self.progress_bar2.setValue)
        self.downloader.finished.connect(self.on_finished)
    def Handel_window(self):
        self.setWindowTitle('Youtube Downloader')
        self.tabWidget.tabBar().setVisible(False)

    def Handel_Buttons(self):
        self.video_search.clicked.connect(self.on_clicked_quality)
        self.video_start.clicked.connect(self.download)
        self.playlist_start.clicked.connect(self.playlist_click)
        self.playlist_search.clicked.connect(self.video_playlist_search)
        self.video_save.clicked.connect(self.Handel_Save_video)
        self.playlist_save.clicked.connect(self.Handel_Save_playlist)
        self.video_tab.clicked.connect(self.Tab_video)
        self.playlist_tab.clicked.connect(self.Tab_playlist)

    def Handel_Save_video(self):
        save = QFileDialog.getExistingDirectory(self, "Select Place")
        self.save_video.setText(save)
    def Handel_Save_playlist(self):
        save = QFileDialog.getExistingDirectory(self, "Select Place")
        self.save_playlist.setText(save)

    def Tab_video(self):
        self.tabWidget.setCurrentIndex(0)
    def Tab_playlist(self):
        self.tabWidget.setCurrentIndex(1)

    @QtCore.pyqtSlot()
    def on_finished(self):
        QMessageBox.information(self,'Download Complet','Dowload Is Finished')
        ##########video############
        self.video_url.setText('')
        self.save_video.setText('')
        self.progress_bar.setValue(0)
        #########playlist##########
        self.playlist_url.setText('')
        self.save_playlist.setText('')
        self.lcdNumber.display(0)
        self.progress_bar2.setValue(0)
    @QtCore.pyqtSlot()
    def on_clicked_quality(self):
        video_url = self.video_url.text()
        QtCore.QMetaObject.invokeMethod(self.downloader, "video_quality",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(str, video_url))
#######################video########################
    @QtCore.pyqtSlot(list)
    def update_qualityes(self, types_of_video):
        for t in types_of_video:
            self.combo_box.addItem(str(t), t)

    @QtCore.pyqtSlot()
    def download(self):
        video_save = self.save_video.text()
        d = self.combo_box.currentData()
        QtCore.QMetaObject.invokeMethod(self.downloader, "video_download",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(object, d),
                                        QtCore.Q_ARG(str, video_save))
    #####################playlist##############################
    @QtCore.pyqtSlot()
    def playlist_click(self):
        playlist_url = self.playlist_url.text()
        playlist_save = self.save_playlist.text()
        QtCore.QMetaObject.invokeMethod(self.downloader, "video_playlist_download",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(str, playlist_url),
                                        QtCore.Q_ARG(str, playlist_save))

    @QtCore.pyqtSlot()
    def video_playlist_search(self):
        playlist_url = self.playlist_url.text()
        QtCore.QMetaObject.invokeMethod(self.downloader, "playlist_search",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(str, playlist_url))

    @QtCore.pyqtSlot(list)
    def playlist_videos(self,videos):
        for video in videos:
            qualitey = video['pafy']
            best = qualitey.getbest(preftype='mp4')
            self.label_16.setText('{}'.format(best))
            self.lcdNumber.display(len(videos))

class DownLoader(QtCore.QObject):
    progressChanged = QtCore.pyqtSignal(int)
    qualitiesChanged = QtCore.pyqtSignal(list)
    playChanged = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()

    @QtCore.pyqtSlot(str)
    def video_quality(self,video_url):
        pafy_video = pafy.new(video_url)
        types_of_video = pafy_video.videostreams
        self.qualitiesChanged.emit(types_of_video)

    @QtCore.pyqtSlot(object, str)
    def video_download(self, d, video_save):
        d.download(filepath=video_save,callback=self.callback)
    def callback(self,total, recvd, ratio, rate, eta):
        val = int(ratio * 100)
        self.progressChanged.emit(val)
        if val == 100:
            self.finished.emit()

    @QtCore.pyqtSlot(str)
    def playlist_search(self,playlist_url):
        playlist_pafy = pafy.get_playlist(playlist_url)
        videos = playlist_pafy['items']
        self.playChanged.emit(videos)

    @QtCore.pyqtSlot(str,str)
    def video_playlist_download(self,playlist_url,playlist_save):
        playlist_pafy = pafy.get_playlist(playlist_url)
        videos = playlist_pafy['items']
        for video in videos:
            video_ = video['pafy']
            best = video_.getbest(preftype='mp4')
            best.download(filepath=playlist_save,callback=self.play_pro)
    def play_pro(self,total, recvd, ratio, rate, eta):
        val = int(ratio * 100)
        self.progressChanged.emit(val)
        if val == 100:
            self.finished.emit()
def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()

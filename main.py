import sys
import os
from scipy.io import wavfile
from scipy import signal
import numpy as np
import wave
import matplotlib.pyplot as plt
from scipy.fftpack import fft, rfft, rfftfreq, fftfreq
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QPushButton, QAction, QMenuBar, QLabel, QMessageBox, QDesktopWidget)
from PyQt5.QtGui import (QIcon, QFont, QPixmap)
from PyQt5.QtCore import pyqtSlot, QCoreApplication as qca
from PyQt5.QtMultimedia import QSound

#Nazwa projektu: Analiza częstotliwościowa sygnału akustycznego z wykorzystaniem FFT.
#Wykonanie: Patryk Jelonek - 18723

class App(QMainWindow):
    file = None
    wave = None

    def __init__(self):
        super().__init__()
        self.title = 'Projekt MN - 18723'
        self.left = 200
        self.top = 200
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon('./fav.png'))
        self.statusBar().showMessage(self.wave)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        boldFont = QFont()
        boldFont.setBold(True)

        labelFileName = QLabel(self)
        labelFileName.setFont(boldFont)
        labelFileName.setGeometry(10, 40, 100, 50)
        labelFileName.setText("Nazwa:")

        self.labelFileNameValue = QLabel(self)
        self.labelFileNameValue.setGeometry(100, 40, 400, 50)
        self.labelFileNameValue.setText("None")

        labelChannel = QLabel(self)
        labelChannel.setFont(boldFont)
        labelChannel.setGeometry(10, 80, 150, 50)
        labelChannel.setText("Kanał(y):")

        self.labelChannelValue = QLabel(self)
        self.labelChannelValue.setGeometry(120, 80, 120, 50)
        self.labelChannelValue.setText("None")

        labelSampleWidth = QLabel(self)
        labelSampleWidth.setGeometry(10, 120, 220, 50)
        labelSampleWidth.setFont(boldFont)
        labelSampleWidth.setText("Długość Próbki [bit]: ")

        self.labelSampleWidthValue = QLabel(self)
        self.labelSampleWidthValue.setGeometry(240, 120, 150, 50)
        self.labelSampleWidthValue.setText("None")

        labelSampleFreq = QLabel(self)
        labelSampleFreq.setGeometry(10, 160, 300, 50)
        labelSampleFreq.setFont(boldFont)
        labelSampleFreq.setText("Częstotliwość Próbkowania: ")

        self.labelSampleFreqValue = QLabel(self)
        self.labelSampleFreqValue.setGeometry(320, 160, 100, 50)
        self.labelSampleFreqValue.setText("None")

        labelDuration = QLabel(self)
        labelDuration.setFont(boldFont)
        labelDuration.setGeometry(10, 200, 150, 50)
        labelDuration.setText("Czas trwania:")

        self.labelDurationValue = QLabel(self)
        self.labelDurationValue.setGeometry(170, 200, 120, 50)
        self.labelDurationValue.setText("None")

        #Menu
        menuBar =  self.menuBar()

        fileOpenAction = QAction("&Otworz", self)
        fileOpenAction.setShortcut("Ctrl+O")
        fileOpenAction.setStatusTip('Otworz plik audio')
        fileOpenAction.triggered.connect(self.file_open)

        inputSignalAction = QAction("&Sygnał wejściowy", self)
        inputSignalAction.setStatusTip('Wykres sygnału wejściowego')
        inputSignalAction.triggered.connect(self.input_signal)

        spectrogramAction = QAction("&Spectrogram", self)
        spectrogramAction.setStatusTip('Wykres Spektograficzny')
        spectrogramAction.triggered.connect(self.spectrogram)

        specrumAmplitudeAction = QAction("&Widmo amplitudowe", self)
        specrumAmplitudeAction.setStatusTip('Wykres widma aplitudowego')
        specrumAmplitudeAction.triggered.connect(self.spectrum_amplitude)

        specrumAmplitudeDBAction = QAction("&Widmo amplituowe [dB]", self)
        specrumAmplitudeDBAction.setStatusTip('Wykres widma aplitudowego w skali decybelowej')
        specrumAmplitudeDBAction.triggered.connect(self.spectrum_amplitude_db)

        periodogramAction = QAction("&Periodogram", self)
        periodogramAction.setStatusTip('Wykres widmowej gęstości mocy')
        periodogramAction.triggered.connect(self.periodogram)

        quitAction = QAction("&Zamknij", self)
        quitAction.setShortcut("Ctrl+Q")
        quitAction.setStatusTip('Wylacz applikacje')
        quitAction.triggered.connect(self.close_app)

        fileMenu = menuBar.addMenu('&Plik')
        fileMenu.addAction(fileOpenAction)
        fileMenu.addAction(quitAction)

        self.plotMenu = menuBar.addMenu('&Wykresy')
        self.plotMenu.addAction(inputSignalAction)
        self.plotMenu.addAction(spectrogramAction)
        self.plotMenu.addAction(periodogramAction)
        self.plotMenu.addAction(specrumAmplitudeAction)
        self.plotMenu.addAction(specrumAmplitudeDBAction)
        self.plotMenu.setEnabled(False)

        self.btn_play = QPushButton("Play", self)
        self.btn_play.setGeometry(0, 0, 80, 80)
        self.btn_play.move(240, 300)
        self.btn_play.setVisible(False)
        self.btn_play.clicked.connect(self.play_sound)

        self.btn_stop = QPushButton("Pause", self)
        self.btn_stop.setGeometry(0, 0, 80, 80)
        self.btn_stop.move(315, 300)
        self.btn_stop.setVisible(False)
        self.btn_stop.clicked.connect(self.stop_sound)

        self.show()

    def close_app(self):
        print('Close')
        sys.exit()

    def prints(self):
        print(self.wave)

    def file_open(self):
        try:
            self.file = QFileDialog.getOpenFileName(self,"Open File", os.getcwd(), 'WAV(*.wav)')
            self.wave = wave.openfp(self.file[0], 'rb')
            self.show_info()

            with self.wave:
                self.plotMenu.setEnabled(True)
                self.statusBar().showMessage("Wczytano plik!")
                self.show_info
                self.sound = QSound(self.file[0])
                self.show_player()

        except FileNotFoundError:
            print('Nie udało się otworzyć pliku!')

    def show_info(self):
        self.labelFileNameValue.setText(os.path.basename(self.file[0]))
        self.labelChannelValue.setText(str(self.wave.getnchannels()))
        self.labelSampleFreqValue.setText(str(self.wave.getframerate()) + ' Hz')
        self.labelSampleWidthValue.setText(str(self.wave.getsampwidth()))

        self.wav_duration = self.wave.getnframes() / float(self.wave.getframerate())
        self.labelDurationValue.setText(str(round(self.wav_duration, 2)) + 's')

    def show_player(self):
        self.btn_play.setVisible(True)
        self.btn_stop.setVisible(True)

    def play_sound(self):
        self.sound.play()

    def stop_sound(self):
        self.sound.stop()

    def spectrogram(self):
        try:
            i = 0
            numberOfChannels = self.wave.getnchannels()
            sample_rate, samples = wavfile.read(self.file[0])

            if numberOfChannels > 1:
                fig, axarr = plt.subplots(2,1,True, num="Spectrogram")

                while i < numberOfChannels:
                    axarr[i].plot(i)
                    axarr[i].set_title('Kanał ' + str(i+1))
                    frequencies, times, spectrogram = signal.spectrogram(samples[:,i], sample_rate)
                    axarr[i].pcolormesh(times, frequencies, np.log(np.abs(spectrogram)))
                    axarr[i].set_xlabel('Czas [s]')
                    axarr[i].set_ylabel('Częstotliwość [Hz]')
                    i += 1
            else:
                plt.figure("Spectrogram")
                frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)

                plt.pcolormesh(times, frequencies, np.log(spectrogram))
                plt.title('Kanał 1')
                plt.xlabel('Czas [s]')
                plt.ylabel('Częstotliwość [Hz]')

            plt.subplots_adjust(hspace = .3)
            plt.show()
        except:
            QMessageBox.about(self, 'Bład!', 'Nie udało się utworzyć wykresu!')
            print(sys.exc_info()[0])

    def spectrum_amplitude(self):
        try:
            rate, spectrum = wavfile.read(self.file[0])

            fig, axarr = plt.subplots(2,1, num="Amplituda Widma")
            fig.suptitle("Widma Sygnału")

            axarr[0].plot(0)
            axarr[0].set_title("Pełne widmo sygnału [FFT]")
            spectrum_with_coupling = fft(spectrum)
            axarr[0].plot(spectrum_with_coupling)
            axarr[0].set_xlabel('Indeks widma')
            axarr[0].set_ylabel('Amplituda widma')

            axarr[1].plot(1)
            axarr[1].set_title("Widmo \"rzeczywiste\" sygnału [RFFT]")
            spectrum_without_coupling = rfft(spectrum)
            axarr[1].plot(spectrum_without_coupling)
            axarr[1].set_xlabel('Indeks widma')
            axarr[1].set_ylabel('Amplituda widma')

            plt.subplots_adjust(hspace = .5)
            plt.show()
        except:
            QMessageBox.about(self, 'Bład!', 'Nie udało się utworzyć wykresu!')

    def input_signal(self):
        try:
            rate, spectrum = wavfile.read(self.file[0])

            plt.figure('Sygnal Wejsciowy')
            plt.plot(spectrum)
            plt.title('Sygnał Wejsciowy')
            plt.xlabel('Indeks')
            plt.show()
        except:
            QMessageBox.about(self, 'Bład!', 'Nie udało się utworzyć wykresu!')

    def spectrum_amplitude_db(self):
        try:
            rate, spectrum = wavfile.read(self.file[0])
            numberOfChannels = self.wave.getnchannels()

            if numberOfChannels > 1:
                frequencies, times, spectrogram = signal.spectrogram(spectrum[:,0], rate)
            else:
                frequencies, times, spectrogram = signal.spectrogram(spectrum, rate)

            fig, axarr = plt.subplots(2,1, num="Amplituda Widma - Skala Decybelowa")

            axarr[0].plot(0)
            axarr[0].set_title("Skala liniowa")
            axarr[0].plot(frequencies, np.abs(rfft(spectrogram)), 'r-')
            axarr[0].set_xlabel('Czestotliwosc [Hz]')

            axarr[1].plot(1)
            axarr[1].set_title("Skala logarytmiczna")
            axarr[1].plot(frequencies, 20*np.log10(np.abs(spectrogram)), 'r-')
            axarr[1].set_xlabel('Czestotliwosc [Hz]')
            axarr[1].set_ylabel('Aplituda widma [dB]')

            plt.subplots_adjust(hspace = .5)
            plt.show()
        except:
            QMessageBox.about(self, 'Bład!', 'Nie udało się utworzyć wykresu!')

    def periodogram(self):
        try:
            rate, spectrum = wavfile.read(self.file[0])
            numberOfChannels = self.wave.getnchannels()

            if numberOfChannels > 1:
                freq, Pxx = signal.periodogram(spectrum[:,0], rate, 'hamming', self.wave.getnframes(), scaling='density')
            else:
                freq, Pxx = signal.periodogram(spectrum, rate, 'hamming', self.wave.getnframes(), scaling='density')

            plt.figure("Periodogram")
            plt.semilogy(freq, Pxx)
            plt.xlim(0, 10000)
            plt.xlabel('Częstotliwość [Hz]')
            plt.ylabel('Widmowa gęstość mocy')
            plt.show()
        except:
            QMessageBox.about(self, 'Bład!', 'Nie udało się utworzyć wykresu!')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

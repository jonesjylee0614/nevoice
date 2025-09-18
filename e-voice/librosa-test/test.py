import librosa.display
import matplotlib.pyplot as plt
import numpy as np

# 加载音频文件
audio_path = 'asr_example.wav'
audio, sr = librosa.load(audio_path)

# 绘制音频波形图
plt.figure(figsize=(100, 20))
librosa.display.waveshow(audio, sr=sr)
plt.title('Waveform')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.show()

# 绘制音频频谱图
plt.figure(figsize=(100, 20))
librosa.display.specshow(librosa.amplitude_to_db(librosa.stft(audio), ref=np.max), y_axis='log', x_axis='time')
plt.colorbar(format='%+2.0f dB')
plt.title('Spectrogram')
plt.show()
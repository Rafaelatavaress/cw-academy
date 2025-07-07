import pyaudio
import wave
import time
from datetime import datetime
from typing import Optional
import sys
"""import select (vamos importá-lo condicionalmente)"""
if sys.platform == "win32":
    import msvcrt
else:
    import select # Agora o select é importado aqui, se não for Windows


def record_audio() -> Optional[str]:
    """Records audio from microphone when user presses Enter and stops when Enter is pressed again.
    
    Returns:
        str: Path to the saved WAV file, or None if recording failed
    """
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    
    audio = pyaudio.PyAudio()
    frames = []
    recording = False
    
    def callback(in_data, frame_count, time_info, status):
        if recording:
            frames.append(in_data)
        return (in_data, pyaudio.paContinue)
    
    try:
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS, 
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=callback
        )
        
        stream.start_stream()
        print("Press Enter to start recording, press Enter again to stop...")
        
        while True:
            # Verificação de Enter (compatível com Windows/Linux/macOS)
            if sys.platform == "win32":
                if msvcrt.kbhit():  # Verifica se alguma tecla foi pressionada
                    # lê o caractere e verifica se é Enter (byte '\r')
                    if msvcrt.getch() == b'\r': 
                        if not recording:
                            recording = True
                            print("Recording...")
                        else:
                            print("Stopping recording.")
                            break # Sai do loop quando Enter é pressionado para parar
            else: # Para Linux/macOS
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    sys.stdin.readline() # Consume o Enter
                    if not recording:
                        recording = True
                        print("Recording...")
                    else:
                        print("Stopping recording.")
                        break # Sai do loop quando Enter é pressionado para parar
                        
            time.sleep(0.1)  # Reduz o uso da CPU
                
        stream.stop_stream()
        stream.close()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            
        return filename
        
    finally:
        audio.terminate()
        
    return None
import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog
from urllib.parse import urlparse, parse_qs, unquote

DEFAULT_PT_CANDIDATES = [
    r"C:\Program Files\Cisco Packet Tracer 8.2.1\bin\PacketTracer.exe",
    r"C:\Program Files\Cisco Packet Tracer 8.2.2\bin\PacketTracer.exe",
    r"C:\Program Files\Cisco Packet Tracer 8.2.0\bin\PacketTracer.exe",
    r"C:\Program Files\Cisco Packet Tracer 8.3.0\bin\PacketTracer.exe",
    r"C:\Program Files\Cisco Packet Tracer*\bin\PacketTracer.exe",
]

def find_packet_tracer():
    for cand in DEFAULT_PT_CANDIDATES:
        if '*' in cand:
            import glob
            matches = glob.glob(cand)
            if matches and os.path.exists(matches[0]):
                return matches[0]
        elif os.path.exists(cand):
            return cand
    try:
        import winreg
        for key in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                k = winreg.OpenKey(key, r"SOFTWARE\Cisco Systems\Cisco Packet Tracer")
                exe, _ = winreg.QueryValueEx(k, "InstallDir")
                cand = os.path.join(exe, "bin", "PacketTracer.exe")
                if os.path.exists(cand):
                    return cand
            except OSError:
                pass
    except Exception:
        pass
    return None

PACKET_TRACER_EXE = find_packet_tracer() or r"C:\Program Files\Cisco Packet Tracer 8.2.1\bin\PacketTracer.exe"
DEFAULT_FOLDER = r"C:\Redes"


def parse_requested_file(raw_url: str):
    if not raw_url:
        return None

    if raw_url.startswith('ciscopt://'):
        parsed = urlparse(raw_url)
        if parsed.query:
            params = parse_qs(parsed.query)
            if 'file' in params and params['file']:
                return unquote(params['file'][0])
        return None

    if raw_url.lower().endswith('.pkt') and os.path.exists(raw_url):
        return raw_url

    return None


def pick_file_from_dialog():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    try:
        file_path = filedialog.askopenfilename(
            title='Selecciona un proyecto de Cisco Packet Tracer',
            initialdir=DEFAULT_FOLDER,
            filetypes=[('Archivos Packet Tracer', '*.pkt')]
        )
        return file_path
    finally:
        root.destroy()


def launch_packet_tracer(file_path: str):
    if not file_path:
        raise ValueError('No se seleccionó ningún archivo .pkt')

    if not os.path.exists(file_path):
        raise FileNotFoundError(f'No existe el archivo: {file_path}')

    if not file_path.lower().endswith('.pkt'):
        raise ValueError('El archivo seleccionado no es un proyecto .pkt')

    if not os.path.exists(PACKET_TRACER_EXE):
        raise FileNotFoundError(f'No se encontró Cisco Packet Tracer en: {PACKET_TRACER_EXE}')

    subprocess.Popen([PACKET_TRACER_EXE, file_path], shell=False)
    print(f'Abriendo proyecto: {file_path}')


def main():
    raw_argument = sys.argv[1] if len(sys.argv) > 1 else ""
    requested_file = parse_requested_file(raw_argument)

    if requested_file:
        launch_packet_tracer(requested_file)
        return

    selected_file = pick_file_from_dialog()
    if not selected_file:
        print('No se seleccionó ningún archivo .pkt.')
        return

    launch_packet_tracer(selected_file)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Error: {exc}')
        input('Presiona Enter para cerrar...')
        raise

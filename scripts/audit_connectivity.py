import sys
from librouteros import connect

devices = [
    {"name": "Filial 01", "host": "192.168.3.11", "user": "admin", "pass": "SUA_SENHA_SEGURA"},
    {"name": "Filial 02", "host": "192.168.3.12", "user": "admin", "pass": "SUA_SENHA_SEGURA"},
    {"name": "Filial 03", "host": "192.168.3.13", "user": "admin", "pass": "SUA_SENHA_SEGURA"},
    {"name": "Filial 04", "host": "192.168.3.14", "user": "admin", "pass": "SUA_SENHA_SEGURA"},
]

def audit_devices():
    print("Iniciando auditoria de conectividade e status dos MikroTiks...\n")
    for dev in devices:
        try:
            api = connect(username=dev["user"], password=dev["pass"], host=dev["host"])
            print(f"[SUCESSO] Conectado a {dev['name']} ({dev['host']})")
            
            # Coleta informações de recursos do sistema
            resource = list(api(path='/system/resource'))
            if resource:
                r = resource[0]
                print(f"   -> Uptime: {r.get('uptime')} | Versão: {r.get('version')} | CPU Load: {r.get('cpu-load')}%")
            api.close()
        except Exception as e:
            print(f"[ERRO] Falha ao conectar em {dev['name']} ({dev['host']}): {e}")

if __name__ == "__main__":
    audit_devices()
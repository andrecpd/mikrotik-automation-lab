#!/usr/bin/env python3
"""Validação local de endereçamento e parâmetros; não conecta ao roteador."""
from __future__ import annotations
import ipaddress
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "vars" / "lan.yml"

def main() -> int:
    errors: list[str] = []
    try:
        lan = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["lan"]
        interface = ipaddress.ip_interface(lan["gateway_cidr"])
        network = interface.network
        start = ipaddress.ip_address(lan["dhcp"]["range_start"])
        end = ipaddress.ip_address(lan["dhcp"]["range_end"])
        ports = lan["ports"]
        if interface.ip in (network.network_address, network.broadcast_address):
            errors.append("Gateway não pode ser endereço de rede ou broadcast.")
        if start not in network or end not in network:
            errors.append("As extremidades do pool devem pertencer à sub-rede LAN.")
        if int(start) > int(end):
            errors.append("range_start deve ser menor ou igual a range_end.")
        if start <= interface.ip <= end:
            errors.append("Pool DHCP inclui o endereço do gateway.")
        if len(ports) != len(set(ports)) or not ports:
            errors.append("Lista de portas vazia ou com duplicatas.")
        if lan["dhcp"]["enabled"] is not True:
            errors.append("Este perfil exige DHCP habilitado.")
        if lan["management_ip"] != lan["api"]["host"]:
            errors.append("management_ip e api.host devem apontar para o mesmo CHR.")
        if not lan["bridge_name"] or lan["bridge_name"] == "all":
            errors.append("bridge_name vazio ou reservado.")
        print(f"Gerenciamento: {lan['management_ip']}")
        print(f"LAN: {interface.ip} | rede {network} | portas {', '.join(ports)}")
        print(f"DHCP: {start}-{end}")
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
        errors.append(f"Falha ao interpretar configuração: {exc}")
    if errors:
        print("\nFAIL — pré-validação reprovada:")
        for error in errors:
            print(f" - {error}")
        return 1
    print("\nPASS — validação local concluída; nenhum equipamento foi alterado.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

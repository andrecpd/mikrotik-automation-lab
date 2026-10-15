#!/usr/bin/env python3
"""Audita a configuração LAN do MikroTik contra config/lan.yml; não altera o roteador."""
import json
import os
import sys
from pathlib import Path

import yaml
from librouteros import connect

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "lan.yml"


def first(items):
    return items[0] if items else None


def main():
    host = os.getenv("MIKROTIK_HOST")
    username = os.getenv("MIKROTIK_USER")
    password = os.getenv("MIKROTIK_PASSWORD")
    if not all((host, username, password)):
        print("ERRO: defina MIKROTIK_HOST, MIKROTIK_USER e MIKROTIK_PASSWORD.")
        return 2

    with CONFIG_PATH.open(encoding="utf-8") as handle:
        lan = yaml.safe_load(handle)["lan"]

    checks = []
    api = None
    try:
        api = connect(host=host, username=username, password=password, timeout=5)
        bridges = list(api.path("/interface/bridge"))
        bridge = next((x for x in bridges if x.get("name") == lan["bridge"]), None)
        checks.append(("Bridge existe", bridge is not None, lan["bridge"]))

        ports = list(api.path("/interface/bridge/port"))
        for interface in lan["interface_ports"]:
            entry = next((x for x in ports if x.get("interface") == interface
                          and x.get("bridge") == lan["bridge"]), None)
            checks.append((f"Porta {interface} na bridge", entry is not None, lan["bridge"]))

        addresses = list(api.path("/ip/address"))
        gateway = next((x for x in addresses if x.get("address") == lan["gateway_cidr"]
                        and x.get("interface") == lan["bridge"]), None)
        checks.append(("Gateway configurado", gateway is not None, lan["gateway_cidr"]))

        if lan.get("dhcp", {}).get("enabled", False):
            pools = list(api.path("/ip/pool"))
            pool = next((x for x in pools if x.get("name") == lan["dhcp"]["pool_name"]
                         and x.get("ranges") == lan["dhcp"]["pool_range"]), None)
            checks.append(("Pool DHCP", pool is not None, lan["dhcp"]["pool_name"]))

            servers = list(api.path("/ip/dhcp-server"))
            server = next((x for x in servers if x.get("name") == lan["dhcp"]["server_name"]
                           and x.get("interface") == lan["bridge"]
                           and x.get("disabled") != "true"), None)
            checks.append(("Servidor DHCP habilitado", server is not None, lan["dhcp"]["server_name"]))

            networks = list(api.path("/ip/dhcp-server/network"))
            network = next((x for x in networks if x.get("address") == lan["network"]), None)
            checks.append(("Rede DHCP", network is not None, lan["network"]))

    except Exception as exc:
        print(f"ERRO: falha na conexão ou consulta RouterOS: {exc}")
        return 2
    finally:
        if api is not None:
            close = getattr(api, "close", None)
            if callable(close):
                close()

    print("\nAUDITORIA LAN - RESULTADO")
    print("=" * 64)
    for name, passed, expected in checks:
        print(f"[{'OK' if passed else 'FALHA'}] {name} | esperado: {expected}")
    failed = sum(not passed for _, passed, _ in checks)
    summary = {"host": host, "total": len(checks), "passed": len(checks)-failed,
               "failed": failed, "status": "PASS" if failed == 0 else "FAIL"}
    report_path = ROOT / "reports" / "audit_lan_latest.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(f"\nResumo: {summary['passed']}/{summary['total']} verificações aprovadas.")
    print(f"Relatório: {report_path.relative_to(ROOT)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

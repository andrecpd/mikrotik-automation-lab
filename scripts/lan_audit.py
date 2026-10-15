#!/usr/bin/env python3
"""Auditoria pós-configuração somente leitura via API RouterOS."""
from __future__ import annotations
import json
import os
import sys
import ipaddress
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import yaml
from librouteros import connect

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "vars" / "lan.yml"
REPORT_DIR = ROOT / "reports"

def find(items: list[dict[str, Any]], key: str, value: str):
    return next((item for item in items if str(item.get(key, "")) == value), None)

def run_audit():
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["lan"]
    host, port = cfg["api"]["host"], int(cfg["api"]["port"])
    password = os.getenv("MIKROTIK_PASSWORD")
    if not password:
        raise RuntimeError("MIKROTIK_PASSWORD não está definido no ambiente.")
    user = os.getenv("MIKROTIK_USER", "admin")
    gateway_ip = cfg["gateway_cidr"].split("/")[0]
    network_cidr = str(ipaddress.ip_interface(cfg["gateway_cidr"]).network)
    checks = []
    def check(name, ok, expected, actual):
        checks.append({"check": name, "status": "PASS" if ok else "FAIL",
                       "expected": expected, "actual": actual})
    api = None
    try:
        api = connect(username=user, password=password, host=host, port=port, timeout=10)
        bridges = list(api(path="/interface/bridge"))
        ports = list(api(path="/interface/bridge/port"))
        addresses = list(api(path="/ip/address"))
        pools = list(api(path="/ip/pool"))
        servers = list(api(path="/ip/dhcp-server"))
        networks = list(api(path="/ip/dhcp-server/network"))
        bridge = find(bridges, "name", cfg["bridge_name"])
        check("bridge_exists", bridge is not None, cfg["bridge_name"],
              bridge.get("name") if bridge else None)
        if bridge:
            check("bridge_protocol",
                  str(bridge.get("protocol-mode", "")).lower() == cfg["bridge_protocol"],
                  cfg["bridge_protocol"], bridge.get("protocol-mode"))
        actual_ports = sorted(str(x.get("interface")) for x in ports
                              if str(x.get("bridge")) == cfg["bridge_name"])
        expected_ports = sorted(cfg["ports"])
        check("bridge_ports_exact", actual_ports == expected_ports, expected_ports, actual_ports)
        addr = next((x for x in addresses if str(x.get("interface")) == cfg["bridge_name"]
                     and str(x.get("address")) == cfg["gateway_cidr"]), None)
        check("gateway_address", addr is not None, cfg["gateway_cidr"],
              addr.get("address") if addr else None)
        pool = find(pools, "name", cfg["dhcp"]["pool_name"])
        expected_range = cfg["dhcp"]["range_start"] + "-" + cfg["dhcp"]["range_end"]
        check("dhcp_pool", pool is not None and str(pool.get("ranges")) == expected_range,
              expected_range, pool.get("ranges") if pool else None)
        server = find(servers, "name", cfg["dhcp"]["server_name"])
        server_ok = bool(server) and str(server.get("interface")) == cfg["bridge_name"] and str(server.get("address-pool")) == cfg["dhcp"]["pool_name"] and str(server.get("disabled", "false")).lower() not in ("true", "yes")
        check("dhcp_server_enabled", server_ok,
              {"interface": cfg["bridge_name"], "pool": cfg["dhcp"]["pool_name"], "enabled": True},
              {"interface": server.get("interface"), "pool": server.get("address-pool"),
               "disabled": server.get("disabled")} if server else None)
        dhcp_net = find(networks, "address", network_cidr)
        net_ok = bool(dhcp_net) and str(dhcp_net.get("gateway")) == gateway_ip
        check("dhcp_network_gateway", net_ok,
              {"address": network_cidr, "gateway": gateway_ip},
              {"address": dhcp_net.get("address"), "gateway": dhcp_net.get("gateway")} if dhcp_net else None)
    finally:
        if api is not None:
            api.close()
    passed = bool(checks) and all(x["status"] == "PASS" for x in checks)
    return {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "target": host,
            "mode": "read-only RouterOS API audit", "overall": "PASS" if passed else "FAIL",
            "checks_passed": sum(x["status"] == "PASS" for x in checks),
            "checks_failed": sum(x["status"] == "FAIL" for x in checks), "checks": checks}, passed

def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        report, passed = run_audit()
    except Exception as exc:
        report = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                  "target": "192.168.3.11", "overall": "FAIL", "checks_passed": 0,
                  "checks_failed": 1, "error": f"{type(exc).__name__}: {exc}", "checks": []}
        passed = False
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = REPORT_DIR / f"lan-audit-{stamp}.json"
    md_path = REPORT_DIR / f"lan-audit-{stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Relatório de auditoria LAN", "", f"- Resultado: **{report['overall']}**",
             f"- Alvo: {report['target']}", f"- Data UTC: {report['timestamp_utc']}",
             f"- Checks PASS: {report['checks_passed']}", f"- Checks FAIL: {report['checks_failed']}", ""]
    if report.get("error"):
        lines += [f"Erro: {report['error']}", ""]
    lines += ["| Check | Status | Esperado | Encontrado |", "|---|---|---|---|"]
    for item in report.get("checks", []):
        lines.append("| " + item["check"] + " | " + item["status"] + " | " +
                     json.dumps(item.get("expected"), ensure_ascii=False) + " | " +
                     json.dumps(item.get("actual"), ensure_ascii=False) + " |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{report['overall']} — {report['checks_passed']} PASS / {report['checks_failed']} FAIL")
    print(f"Relatórios: {json_path.relative_to(ROOT)} e {md_path.relative_to(ROOT)}")
    if report.get("error"):
        print(report["error"], file=sys.stderr)
    return 0 if passed else 1

if __name__ == "__main__":
    sys.exit(main())

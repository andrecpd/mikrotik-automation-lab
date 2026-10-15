# MikroTik NetOps Lab — automação LAN segura

Laboratório didático para configurar uma LAN em MikroTik CHR com Ansible community.routeros e auditar o estado real com Python.

> **Segurança:** nenhuma alteração ocorre por padrão. A configuração exige explicitamente -e apply_lan_config=true. Use apenas em CHR isolado de laboratório, faça snapshot da VM e revise a configuração antes de executar.

## Parâmetros confirmados

| Item | Valor |
|---|---|
| IP de gerenciamento CHR | 192.168.3.11 |
| Gateway LAN | 192.168.10.1/24 |
| Rede LAN | 192.168.10.0/24 |
| Portas LAN | ether2, ether3, ether4 |
| DHCP | Ativado |
| Pool DHCP | 192.168.10.100-192.168.10.200 |

## Valores adicionais escolhidos e documentados

- Bridge: br-lan
- Pool: pool-lan
- Servidor DHCP: dhcp-lan
- Lease time: 1d
- Protocolo bridge: RSTP
- API RouterOS para auditoria: TCP/8728, restrita à rede de gerenciamento
- DNS entregue por DHCP: não definido; a automação não presume servidores DNS.
- A automação não apaga objetos preexistentes. Revise conflitos antes de aplicar.

## Instalação no Ubuntu VMware

    sudo apt update
    sudo apt install -y python3 python3-venv python3-pip git openssh-client
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r scripts/requirements-lan.txt
    ansible-galaxy collection install -r requirements-lan.yml

Defina credenciais apenas no ambiente do terminal:

    read -rsp 'Senha RouterOS: ' MIKROTIK_PASSWORD; echo
    export MIKROTIK_PASSWORD
    export MIKROTIK_USER=admin

admin é apenas o padrão documentado; ajuste MIKROTIK_USER ao usuário real do CHR. Prefira usuário dedicado com privilégios mínimos.

## Execução em etapas

1. Pré-validação local, sem conexão:

       python scripts/lan_precheck.py

2. Pré-check remoto, somente leitura:

       ansible-playbook -i inventory/lan-lab.yaml playbooks/01_precheck_lan.yml

3. Depois de revisar tudo e confirmar que é o CHR de laboratório, aplicar explicitamente:

       ansible-playbook -i inventory/lan-lab.yaml playbooks/02_configure_lan.yml -e apply_lan_config=true

4. Habilite RouterOS API TCP/8728 com acesso limitado à VM NetOps e execute auditoria somente leitura:

       python scripts/lan_audit.py

Relatórios JSON e Markdown são gravados em reports/. Código de saída 0 = PASS, 1 = FAIL.

## Limites

A auditoria verifica bridge, protocolo, conjunto de portas, gateway, pool, servidor DHCP e gateway da rede DHCP. PASS não certifica firewall, NAT, DNS, acesso à Internet ou entrega real de leases. A automação não configura esses itens.

Consulte docs/lan-automation.md para detalhes, troubleshooting e cuidados de segurança.

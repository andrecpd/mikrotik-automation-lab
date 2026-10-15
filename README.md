# MikroTik Automation Lab

Laboratório de NetOps para automação de equipamentos MikroTik RouterOS usando Ansible e Python.

## Objetivos

- Gerenciar equipamentos por inventário Ansible.
- Provisionar uma LAN de laboratório com bridge, portas, gateway IP e DHCP.
- Auditar a configuração real com Python comparando-a ao estado desejado.
- Produzir um relatório JSON e código de saída útil para CI.

## Estrutura

```text
config/lan.yml                         # Estado desejado da LAN
docs/lan-automation.md                 # Tutorial do fluxo de LAN
inventory/hosts.yaml                   # Inventário (sem senhas fixas)
playbooks/lan.yml                      # Provisionamento da LAN
playbooks/site.yaml                    # Playbook base existente
playbooks/roles/base_config/            # Role de configuração base
scripts/audit_lan.py                   # Auditoria read-only da LAN
scripts/audit_connectivity.py          # Auditoria básica existente
scripts/requirements.txt               # Dependências Python
reports/                               # Relatórios locais, ignorados pelo Git
```

## Início rápido

1. Prepare Ubuntu/WSL ou Ubuntu VM e ative o ambiente virtual Python.
2. Instale dependências: `pip install -r scripts/requirements.txt`.
3. Instale coleções: `ansible-galaxy collection install ansible.netcommon community.routeros`.
4. Configure `MIKROTIK_USER` e `MIKROTIK_PASSWORD` no ambiente. Não grave segredos no inventário.
5. Leia [o guia de automação da LAN](docs/lan-automation.md).
6. Revise inventário, portas e endereçamento para corresponder ao seu CHR antes de executar.

## Segurança

**Não use senhas reais em arquivos versionados.** Se uma senha já foi enviada para um repositório público, troque-a imediatamente e considere limpar o histórico Git. Remover uma senha do arquivo atual não a remove dos commits antigos.

## Aviso

Este é um laboratório inicial. Teste em um MikroTik CHR descartável, faça backup e confirme a porta de gerenciamento antes de aplicar mudanças. A auditoria de configuração não substitui testes reais de DHCP, DNS e conectividade de clientes.

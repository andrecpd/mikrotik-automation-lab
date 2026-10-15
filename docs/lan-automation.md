# Automação e auditoria da LAN

## Objetivo

Provisionar uma bridge LAN no MikroTik RouterOS usando Ansible e comparar o estado do equipamento com o estado desejado usando Python. A auditoria é somente leitura.

## Estado desejado inicial

O arquivo `config/lan.yml` define a bridge `bridge-LAN`, portas `ether2` a `ether5`, gateway `192.168.10.1/24` e DHCP de `192.168.10.100` a `192.168.10.200`.

**Importante:** confirme a topologia e os nomes das interfaces do seu CHR antes de executar. Não use este exemplo em roteador de produção sem revisão, backup e plano de rollback. Garanta que a porta de gerenciamento não será adicionada à bridge LAN.

## Preparação

1. Instale as coleções necessárias no ambiente virtual:

   ```bash
   ansible-galaxy collection install ansible.netcommon community.routeros
   pip install -r scripts/requirements.txt PyYAML
   ```

2. Configure usuário e senha fora do Git. Use um usuário dedicado do RouterOS com privilégios mínimos necessários e mantenha a senha fora de arquivos versionados.

   ```bash
   export MIKROTIK_HOST="192.168.3.11"
   export MIKROTIK_USER="netops"
   read -s MIKROTIK_PASSWORD
   export MIKROTIK_PASSWORD
   ```

3. Antes de provisionar, faça backup/export do CHR e confirme conectividade de gerenciamento.

## Validar sintaxe e revisar mudanças

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/lan.yml --syntax-check
ansible-playbook -i inventory/hosts.yaml playbooks/lan.yml --check --diff
```

O modo check não garante que cada comando RouterOS seja simulável. Revise a saída e o plano antes da execução real.

## Aplicar a LAN no laboratório

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/lan.yml --limit filial_01
```

O exemplo limita a execução a `filial_01`. O inventário precisa usar o método de conexão RouterOS correto e credenciais externas; revise-o antes de executar.

## Auditar depois da aplicação

```bash
python scripts/audit_lan.py
```

O script lê `config/lan.yml`, consulta bridge, portas, endereço IP, pool e servidor/rede DHCP e gera `reports/audit_lan_latest.json`. Código de saída 0 significa auditoria aprovada; 1 indica divergências; 2 indica erro de conexão/execução.

## Limitações conhecidas

- A auditoria verifica a presença e os principais parâmetros dos objetos, não comprova por si só o funcionamento fim a fim de um cliente DHCP.
- Faça testes adicionais de DHCP, gateway, DNS e conectividade a partir de uma máquina cliente conectada à LAN.
- A automação é um ponto de partida de laboratório. Faça revisão de sintaxe e teste em CHR descartável antes de uso real.

# Automação LAN: procedimento operacional

## Escopo

Configura bridge br-lan, portas ether2/ether3/ether4, gateway 192.168.10.1/24 e DHCP 192.168.10.100-192.168.10.200 no CHR gerenciado em 192.168.3.11. Nomes br-lan, pool-lan e dhcp-lan, lease-time 1d e RSTP são escolhas documentadas do laboratório, não parâmetros informados originalmente. DNS não é definido.

A automação não configura NAT, firewall, rotas, VLANs, DNS global nem acesso à Internet. Não remove objetos preexistentes. Uma falha durante o playbook pode deixar alterações parciais; inspecione o estado antes de tentar novamente.

## Pré-requisitos

- Ubuntu VMware alcança 192.168.3.11.
- SSH/TCP 22 habilitado e limitado à rede de gerência.
- Para auditoria Python, RouterOS API TCP/8728 habilitada e limitada por firewall ao host NetOps. A API sem TLS não deve ser exposta à Internet.
- Confirme que ether2, ether3 e ether4 existem e não são uplinks/WAN nem pertencem a outra bridge.
- Faça snapshot/checkpoint da VM CHR.

## Credenciais

    read -rsp 'Senha RouterOS: ' MIKROTIK_PASSWORD; echo
    export MIKROTIK_PASSWORD
    export MIKROTIK_USER=admin

admin é o valor padrão do exemplo. Use o usuário real e, preferencialmente, uma conta exclusiva de laboratório com privilégios mínimos. Não grave segredos em YAML, histórico de shell ou Git.

## Etapas

1. Validação estática: python scripts/lan_precheck.py
2. Pré-check remoto somente leitura: ansible-playbook -i inventory/lan-lab.yaml playbooks/01_precheck_lan.yml
3. Só no CHR de laboratório, após revisão: ansible-playbook -i inventory/lan-lab.yaml playbooks/02_configure_lan.yml -e apply_lan_config=true
4. Auditoria via API: python scripts/lan_audit.py

A etapa 3 é bloqueada sem confirmação explícita. A etapa 4 gera JSON e Markdown em reports/. Código de saída 0 = PASS; 1 = FAIL.

## Critérios auditados

Bridge existe, protocolo corresponde, conjunto exato de portas corresponde, endereço gateway existe, pool DHCP tem faixa correta, servidor DHCP está habilitado na bridge e usa o pool esperado, rede DHCP tem gateway correto. PASS não comprova entrega real de leases nem valida firewall/NAT/DNS/Internet.

## Troubleshooting

- SSH falha: confira endereço, rota, serviço SSH e firewall.
- API falha: confira serviço API, TCP/8728, usuário, permissões e origem permitida.
- Porta já associada a outra bridge: não remova automaticamente; revise a topologia.
- DHCP existente com outro nome: investigue possível conflito antes de ativar outro servidor.
- Falha parcial: guarde a saída do Ansible, inspecione o estado e corrija manualmente antes de repetir.

## Credencial legada

O inventário anterior continha uma senha em texto puro. Esta versão remove a senha do arquivo atual, mas não elimina o valor do histórico Git. Rotacione essa credencial imediatamente e não a reutilize.

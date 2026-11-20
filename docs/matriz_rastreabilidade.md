# Matriz de Rastreabilidade — UniReserve (Requisitos × Código)

> **Responsável:** Gabriel — Analista de Requisitos  
> **Base auditada:** branch `main` (commit `702230e`) + referência ao PR `#1` (`qa/melhorias-backend-e-testes`)  
> **Objetivo:** Rastrear cada Requisito Funcional (`RF01–RF55`) e Regra de Negócio (`RN01–RN31`) contra a implementação real, documentando lacunas e encaminhando pendências técnicas para Desenvolvedores, QA e UX no Kanban.

---

## 1. Resumo Executivo da Cobertura (`main`)

| Categoria | Total | Atendido | Parcial | Pendente (MVP) | Pós-MVP (Fora do escopo) |
|---|---:|---:|---:|---:|---:|
| **Requisitos Funcionais (`RF01–RF55`)** | 55 | 46 | 4 | 0 | 5 |
| **Regras de Negócio (`RN01–RN31`)** | 31 | 19 | 7 | 5 | 0 |

- **RFs Parciais no MVP:** `RF40` (`curso` exibido sem campo de cadastro/edição), `RF46` (`regras_especificas` não exibidas antes da reserva), `RF50` (filtro verifica janela fixa de 30 min a partir de um instante, sem intervalo início/fim), `RF51` (notificações de reserva funcionam; avisos institucionais ainda são slides estáticos).
- **RFs Pós-MVP (documentados como futuros):** `RF10`, `RF11`, `RF28`, `RF29`, `RF45`.
- **RNs Pendentes (não aplicadas no código):** `RN06` (espaços exclusivos por perfil além de externos), `RN08` (duração máxima), `RN09` (limite de antecedência), `RN12` (validação de capacidade na reserva), `RN14` (validação do campo `exige_autorizacao` dos equipamentos na reserva).
- **RNs Parciais (exigem reforço no backend/UI):** `RN01` (auto-cadastro permite escolher `professor`), `RN05` e `RN29` (RBAC de espaços/equipamentos/usuários apenas na UI), `RN07` (horário de funcionamento só na exibição da agenda; passado validado só na UI), `RN13` (`regras_especificas` salvas, mas não exibidas ao reservar), `RN17` (`aprovar_se_disponivel` não revalida bloqueios), `RN18` (criação de bloqueio não alerta sobre reservas existentes).

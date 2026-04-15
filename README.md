# nitailab-propostas

Sistema de propostas comerciais em HTML estático para o Nitai Lab — Resgate seu Google.
Hospedado em `propostas.nitailab.com.br` (subdomínio privado, noindex).

Cada proposta expira em **7 dias**. Uma GitHub Action roda diariamente e remove os arquivos expirados.

Visual baseado no **Brandbook Nitai Lab — Resgate seu Google v1.0 (14/04/2026)**.
Tipografia: IBM Plex Sans · Urbanist · Outfit. Paleta: Carvão #1C1C1A, Vermelho Maps #EA4335, Amarelo pin #FFCC00.

---

## Fluxo completo

### 1. Criar o JSON do cliente

Copie `clientes/_exemplo.json` para `clientes/nome-do-negocio.json` e preencha com os dados reais do diagnóstico:

```bash
cp clientes/_exemplo.json clientes/otica-do-seu-pedro.json
# edite com os dados reais
```

Campos obrigatórios:

| Campo | Exemplo |
|---|---|
| NOME_DO_NEGOCIO | "Ótica do Seu Pedro" |
| CIDADE | "Pará de Minas" |
| TELEFONE | "(31) 99999-9999" |
| POSICAO | "11" |
| NOTA_ATUAL | "3.5" |
| PALAVRA_CHAVE_PRINCIPAL | "ótica em Pará de Minas" |
| BAIRRO_OU_REGIAO | "Centro" |
| CONCORRENTE_1 | "Óticas Visão Clara" |
| NUMERO_AVALIACOES | "18" |
| NUMERO_SEM_RESPOSTA | "12" |
| NUMERO_NEGATIVAS | "2" |
| NUMERO_CONCORRENTES_NA_FRENTE | "10" |
| NUMERO_FOTOS | "4" |
| DATA_ULTIMA_FOTO | "setembro de 2024" |
| NUMERO_FOTOS_CONCORRENTE | "22" |
| PROBLEMAS_NAP | "Horário no Google diferente do Instagram" |
| DATA_ULTIMO_POST | "novembro de 2024" |
| TICKET_MEDIO | "320" |
| LTV_ESTIMADO | "1.800" |
| PERDA_MEDIA | "7.800" |
| SERVICO_PRINCIPAL | "ótica" |
| DATA_PRIMEIRO_RELATORIO | "15/05/2026" |

Campos calculados automaticamente pelo script (não precisam estar no JSON):
- `DATA`, `DATA_EXPIRACAO`, `DATA_EXPIRACAO_ISO`, `DIAS_ATE_EXPIRAR`, `SLUG`, `TELEFONE_LIMPO`

### 2. Rodar o gerador

```bash
python3 scripts/gerar_proposta.py clientes/otica-do-seu-pedro.json
```

Saída:
```
Proposta gerada com sucesso!
  Completa:  https://propostas.nitailab.com.br/p/otica-do-seu-pedro-k3m9
  Local:     file:///...p/otica-do-seu-pedro-k3m9.html
  Pocket:    file:///...p/otica-do-seu-pedro-k3m9-pocket.html (abrir e Ctrl+P)
  QR code:   .../p/qr-otica-do-seu-pedro-k3m9.png
  Expira em: 21/04/2026
```

O script gera:
- `p/{slug}.html` — proposta completa com 12 seções (enviar pelo WhatsApp)
- `p/{slug}-pocket.html` — versão A4, 1 folha, pra levar na visita presencial
- `p/qr-{slug}.png` — QR code que aponta pra proposta completa

### 3. Testar localmente

Abra `p/{slug}.html` no navegador. Para o pocket, abra `p/{slug}-pocket.html` e use Ctrl+P pra verificar que cabe em A4.

### 4. Commit e push

```bash
git add p/
git commit -m "proposta: otica-do-seu-pedro"
git push
```

A proposta fica em `https://propostas.nitailab.com.br/p/{slug}` em alguns minutos.

### 5. Enviar pelo WhatsApp

> Seu Pedro, preparei o diagnóstico completo do seu Google. Acessa aqui: https://propostas.nitailab.com.br/p/otica-do-seu-pedro-k3m9 — expira em 7 dias.

### 6. Imprimir o pocket

Abra `p/{slug}-pocket.html`, Ctrl+P, A4, imprima. Uma página com diagnóstico, planos, garantia e QR.

---

## Expiração automática

Duas camadas:

1. **Meta `expires-at`:** o script `expire.py` lê essa tag e remove arquivos expirados.
2. **GitHub Action:** roda todo dia às 3h UTC. Remove propostas com mais de 2 dias além da expiração. Ver `.github/workflows/expire-propostas.yml`.

---

## Estrutura

```
nitailab-propostas/
├── index.html
├── 404.html
├── robots.txt
├── template/
│   ├── base.html        proposta completa (12 seções)
│   ├── pocket.html      versão A4 impressa (1 folha)
│   └── style.css        referência de tokens do brandbook
├── p/
│   ├── assets/
│   │   └── depoimento-poli-01.jpeg
│   ├── {slug}.html
│   ├── {slug}-pocket.html
│   └── qr-{slug}.png
├── clientes/            JSONs com dados dos clientes — NUNCA commitar
│   └── _exemplo.json
├── scripts/
│   ├── gerar_proposta.py
│   └── expire.py
└── .github/
    └── workflows/
        └── expire-propostas.yml
```

---

## Aviso

A pasta `clientes/` contém dados pessoais e nunca deve ser commitada. Mantenha backups locais ou em drive privado.

#!/usr/bin/env python3
"""
Nitai Lab — Gerador de Propostas V4 (Laudo Técnico Resgate seu Google v2.0)
Uso: python3 scripts/gerar_proposta.py clientes/cliente-x.json
"""

import json
import sys
import os
import re
import random
from datetime import date, timedelta
from pathlib import Path

# -- Tenta instalar qrcode se não existir --
try:
    import qrcode
    from PIL import Image
except ImportError:
    print("Instalando dependência qrcode[pil]...")
    os.system(f"{sys.executable} -m pip install 'qrcode[pil]' --break-system-packages --quiet")
    import qrcode
    from PIL import Image


BASE_DIR = Path(__file__).resolve().parent.parent


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[áàãâä]', 'a', text)
    text = re.sub(r'[éèêë]', 'e', text)
    text = re.sub(r'[íìîï]', 'i', text)
    text = re.sub(r'[óòõôö]', 'o', text)
    text = re.sub(r'[úùûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[ñ]', 'n', text)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text.strip())
    text = re.sub(r'-+', '-', text)
    return text


def random_hash(n=4) -> str:
    """Retorna N dígitos numéricos com zero-padding (ex: 0042)."""
    return str(random.randint(0, 10**n - 1)).zfill(n)


def limpar_telefone(telefone: str) -> str:
    return re.sub(r'\D', '', telefone)


def gerar_qr(url: str, dest_path: Path) -> None:
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1C1C1A", back_color="white")
    img.save(str(dest_path))


def substituir_placeholders(template: str, dados: dict) -> str:
    for chave, valor in dados.items():
        template = template.replace('{{' + chave + '}}', str(valor))
    return template


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/gerar_proposta.py clientes/cliente-x.json")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.is_absolute():
        json_path = BASE_DIR / sys.argv[1]

    if not json_path.exists():
        print(f"Arquivo não encontrado: {json_path}")
        sys.exit(1)

    with open(json_path, encoding='utf-8') as f:
        dados = json.load(f)

    # ── Datas ──────────────────────────────────────────────
    hoje = date.today()
    expiracao = hoje + timedelta(days=7)

    dados['DATA']               = hoje.strftime('%d/%m/%Y')
    dados['DATA_EXPIRACAO']     = expiracao.strftime('%d/%m/%Y')
    dados['DATA_EXPIRACAO_ISO'] = expiracao.isoformat()
    dados['DIAS_ATE_EXPIRAR']   = '7'
    dados['ANO']                = str(hoje.year)

    # ── Hash numérico de referência ────────────────────────
    if 'HASH_NUMERICO' not in dados:
        dados['HASH_NUMERICO'] = random_hash(4)

    # ── DATA_PRIMEIRO_RELATORIO ────────────────────────────
    if 'DATA_PRIMEIRO_RELATORIO' not in dados:
        primeiro_mes_seguinte = (hoje.replace(day=1) + timedelta(days=32)).replace(day=1)
        dados['DATA_PRIMEIRO_RELATORIO'] = primeiro_mes_seguinte.strftime('%d/%m/%Y')

    # ── TELEFONE_LIMPO ─────────────────────────────────────
    if 'TELEFONE_LIMPO' not in dados and 'TELEFONE' in dados:
        dados['TELEFONE_LIMPO'] = limpar_telefone(dados['TELEFONE'])

    # ── Defaults numéricos / cálculos ─────────────────────
    if 'NOTA_ATUAL' not in dados:
        dados['NOTA_ATUAL'] = '—'

    if 'NUMERO_CONCORRENTES_NA_FRENTE' not in dados:
        posicao = int(dados.get('POSICAO', 2))
        dados['NUMERO_CONCORRENTES_NA_FRENTE'] = str(max(posicao - 1, 1))

    if 'SERVICO_PRINCIPAL' not in dados:
        dados['SERVICO_PRINCIPAL'] = dados.get('PALAVRA_CHAVE_PRINCIPAL', 'seu serviço')

    # ── PERCENT_SEM_RESPOSTA / PERCENT_RESPONDIDAS ─────────
    if 'PERCENT_SEM_RESPOSTA' not in dados:
        try:
            sem_resp = int(dados.get('NUMERO_SEM_RESPOSTA', 0))
            total    = int(dados.get('NUMERO_AVALIACOES', 1))
            pct      = round(sem_resp / total * 100) if total > 0 else 0
            dados['PERCENT_SEM_RESPOSTA'] = str(pct)
        except (ValueError, ZeroDivisionError):
            dados['PERCENT_SEM_RESPOSTA'] = '—'

    if 'PERCENT_RESPONDIDAS' not in dados:
        try:
            dados['PERCENT_RESPONDIDAS'] = str(100 - int(dados['PERCENT_SEM_RESPOSTA']))
        except (ValueError, TypeError):
            dados['PERCENT_RESPONDIDAS'] = '—'

    # ── POSTAGENS_ULTIMO_TRIMESTRE ─────────────────────────
    if 'POSTAGENS_ULTIMO_TRIMESTRE' not in dados:
        dados['POSTAGENS_ULTIMO_TRIMESTRE'] = '0'

    # ── Dados de concorrentes — defaults neutros ───────────
    concorrente_defaults = {
        'CONCORRENTE_2':                 'Concorrente local',
        'CONCORRENTE_1_AVALIACOES':      '—',
        'CONCORRENTE_1_NOTA':            '—',
        'CONCORRENTE_1_FOTOS':           '—',
        'CONCORRENTE_1_FOTOS_ULT_MES':   '—',
        'CONCORRENTE_1_POSTS':           '—',
        'CONCORRENTE_1_PERCENT_RESP':    '—',
        'CONCORRENTE_2_AVALIACOES':      '—',
        'CONCORRENTE_2_NOTA':            '—',
        'CONCORRENTE_2_FOTOS':           '—',
        'CONCORRENTE_2_FOTOS_ULT_MES':   '—',
        'CONCORRENTE_2_POSTS':           '—',
        'CONCORRENTE_2_PERCENT_RESP':    '—',
    }
    for chave, default in concorrente_defaults.items():
        if chave not in dados:
            dados[chave] = default

    # ── Slug ───────────────────────────────────────────────
    nome_base = slugify(dados.get('NOME_DO_NEGOCIO', 'proposta'))
    slug = f"{nome_base}-{dados['HASH_NUMERICO']}"
    dados['SLUG'] = slug

    # ── Diretórios de saída ────────────────────────────────
    p_dir = BASE_DIR / 'p'
    p_dir.mkdir(exist_ok=True)
    assets_dir = p_dir / 'assets'
    assets_dir.mkdir(exist_ok=True)

    depo_src = assets_dir / 'depoimento-poli-01.jpeg'
    if not depo_src.exists():
        print("Aviso: p/assets/depoimento-poli-01.jpeg não encontrado. Copie manualmente.")

    # ── Templates ──────────────────────────────────────────
    base_template   = (BASE_DIR / 'template' / 'base.html').read_text(encoding='utf-8')
    pocket_template = (BASE_DIR / 'template' / 'pocket.html').read_text(encoding='utf-8')

    # ── QR code ────────────────────────────────────────────
    url_completa = f"https://propostas.nitailab.com.br/p/{slug}"
    qr_path = p_dir / f"qr-{slug}.png"
    gerar_qr(url_completa, qr_path)

    # ── Gera proposta completa ─────────────────────────────
    html_completo = substituir_placeholders(base_template, dados)
    saida_completa = p_dir / f"{slug}.html"
    saida_completa.write_text(html_completo, encoding='utf-8')

    # ── Gera pocket ────────────────────────────────────────
    html_pocket = substituir_placeholders(pocket_template, dados)
    saida_pocket = p_dir / f"{slug}-pocket.html"
    saida_pocket.write_text(html_pocket, encoding='utf-8')

    # ── Atalhos Desktop (Windows) ──────────────────────────
    desktop_dir = Path('/mnt/c/Users/Lenovo/Desktop/_ABRIR_PROPOSTA_DEMO')
    desktop_dir.mkdir(exist_ok=True)

    # Converte path WSL -> path Windows
    def wsl_to_win(p: Path) -> str:
        parts = str(p.resolve()).split('/')
        # /mnt/c/... -> C:/...
        if len(parts) > 2 and parts[1] == 'mnt':
            drive = parts[2].upper()
            rest  = '/'.join(parts[3:])
            return f"{drive}:/{rest}"
        return str(p.resolve())

    win_completa = wsl_to_win(saida_completa)
    win_pocket   = wsl_to_win(saida_pocket)

    url_completa_local = (desktop_dir / f"{slug}.url")
    url_completa_local.write_text(
        f"[InternetShortcut]\nURL=file:///{win_completa}\n",
        encoding='utf-8'
    )

    url_pocket_local = (desktop_dir / f"{slug}-pocket.url")
    url_pocket_local.write_text(
        f"[InternetShortcut]\nURL=file:///{win_pocket}\n",
        encoding='utf-8'
    )

    # ── Output ─────────────────────────────────────────────
    print(f"\nProposta gerada com sucesso!")
    print(f"  Completa:  {url_completa}")
    print(f"  Local:     file:///{win_completa}")
    print(f"  Pocket:    file:///{win_pocket}")
    print(f"  QR code:   {qr_path.resolve()}")
    print(f"  Expira em: {dados['DATA_EXPIRACAO']}")
    print(f"  Ref:       NL-{dados['ANO']}-{dados['HASH_NUMERICO']}")
    print(f"  Atalhos:   {desktop_dir}/")


if __name__ == '__main__':
    main()

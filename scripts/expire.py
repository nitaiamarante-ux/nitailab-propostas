#!/usr/bin/env python3
"""
Nitai Lab — Remove propostas expiradas (buffer de 2 dias após expiração)
Roda via GitHub Actions diariamente.
"""

import os
import re
from datetime import date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
P_DIR = BASE_DIR / 'p'

BUFFER_DIAS = 2
hoje = date.today()
limite = hoje - timedelta(days=BUFFER_DIAS)

removidos = []

for html_file in sorted(P_DIR.glob('*.html')):
    if html_file.name.startswith('.'):
        continue

    conteudo = html_file.read_text(encoding='utf-8', errors='ignore')
    match = re.search(r'<meta name="expires-at" content="([^"]+)"', conteudo)
    if not match:
        continue

    try:
        exp_date = date.fromisoformat(match.group(1))
    except ValueError:
        continue

    if exp_date <= limite:
        slug_match = re.match(r'^(.+?)(?:-pocket)?\.html$', html_file.name)
        if not slug_match:
            continue
        slug = slug_match.group(1)
        if slug.endswith('-pocket'):
            slug = slug[:-7]

        # Remove HTML completo, pocket e QR
        for sufixo in ['.html', '-pocket.html']:
            alvo = P_DIR / f"{slug}{sufixo}"
            if alvo.exists():
                alvo.unlink()
                removidos.append(str(alvo.name))

        qr_alvo = P_DIR / f"qr-{slug}.png"
        if qr_alvo.exists():
            qr_alvo.unlink()
            removidos.append(str(qr_alvo.name))

if removidos:
    print(f"Removidos ({len(removidos)} arquivos):")
    for r in removidos:
        print(f"  - {r}")
else:
    print("Nenhuma proposta expirada pra remover.")

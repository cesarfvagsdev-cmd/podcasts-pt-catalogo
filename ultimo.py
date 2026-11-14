#!/usr/bin/env python3
"""Acrescenta a cada programa a data do último episódio (campo `ultimo`).

Lê o feed de cada programa do catalogo.json e escreve em `ultimo` a data
(AAAA-MM-DD, em UTC) do episódio mais recente que tem áudio. Serve para a
app marcar os programas em arquivo e contar os ativos.

- Um feed que não responde fica com a data que já tinha (se tinha).
- Não mexe em mais nada do ficheiro.
- A app ignora campos que não conhece: as versões antigas continuam a ler
  o catálogo como antes.

Uso: python3 ultimo.py [catalogo.json]
Precisa apenas de Python 3 e do comando curl.
"""
import concurrent.futures
import datetime
import email.utils
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

AGENTE = "Rubrica/1.0 (data do ultimo episodio)"


def curl(url, limite=60):
    cmd = ["curl", "-sS", "-L", "--proto", "=https", "--proto-redir", "=https",
           "-m", str(limite), "-A", AGENTE, url]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=limite + 10)
    except subprocess.TimeoutExpired:
        return None
    return r.stdout if r.returncode == 0 else None


def ultimo(feed):
    corpo = curl(feed)
    if not corpo or b"<!ENTITY" in corpo:
        return None
    try:
        raiz = ET.fromstring(corpo)
    except ET.ParseError:
        return None
    canal = raiz.find("channel")
    if canal is None:
        return None
    melhor = None
    for item in canal.findall("item"):
        anexo = item.find("enclosure")
        if anexo is None or not (anexo.get("url") or "").strip():
            continue
        try:
            d = email.utils.parsedate_to_datetime(item.findtext("pubDate") or "")
        except (TypeError, ValueError):
            continue
        if d.tzinfo is None:
            d = d.replace(tzinfo=datetime.timezone.utc)
        if melhor is None or d > melhor:
            melhor = d
    if melhor is None:
        return None
    return melhor.astimezone(datetime.timezone.utc).date().isoformat()


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else "catalogo.json"
    with open(caminho, encoding="utf-8") as f:
        catalogo = json.load(f)
    programas = [p for fonte in catalogo["fontes"] for p in fonte["programas"]]
    falhas = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as grupo:
        for prog, data in zip(programas, grupo.map(lambda p: ultimo(p["feed"]), programas)):
            if data:
                prog["ultimo"] = data
            else:
                falhas += 1
                print(f"sem data: {prog['id']}", file=sys.stderr)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=2)
        f.write("\n")
    hoje = datetime.date.today()
    ativos = sum(1 for p in programas if p.get("ultimo") and
                 (hoje - datetime.date.fromisoformat(p["ultimo"])).days <= 90)
    arquivo = sum(1 for p in programas if p.get("ultimo") and
                  (hoje - datetime.date.fromisoformat(p["ultimo"])).days > 365)
    print(f"{len(programas)} programas: {ativos} ativos (90 dias), "
          f"{arquivo} em arquivo (mais de um ano), {falhas} sem data")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verifica o catalogo.json.

Para cada programa confirma que:
- o feed RSS responde por HTTPS e é XML válido;
- os episódios mais recentes têm ficheiro de áudio;
- o áudio responde por HTTPS, sem pedir login.

Uso: python3 verificar.py [catalogo.json]
Precisa apenas de Python 3 e do comando curl.
"""
import concurrent.futures
import email.utils
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

AGENTE = "Mozilla/5.0 (Linux; Android 14) Rubrica/1.0"
EPISODIOS_A_TESTAR = 3
TIPOS = {"radio", "jornal"}
ID_VALIDO = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def curl(args, limite=40):
    cmd = ["curl", "-sS", "-L", "--proto", "=https", "--proto-redir", "=https",
           "-m", str(limite), "-A", AGENTE] + args
    try:
        return subprocess.run(cmd, capture_output=True, timeout=limite + 10)
    except subprocess.TimeoutExpired:
        return None


def data(item):
    try:
        d = email.utils.parsedate_to_datetime(item.findtext("pubDate") or "")
        return d.timestamp()
    except (TypeError, ValueError):
        return 0.0


def verifica_programa(prog):
    erros = []
    feed = prog.get("feed", "")
    if not feed.startswith("https://"):
        return prog, ["o feed não é HTTPS"], None
    r = curl(["-w", "\n%{http_code}", feed])
    if r is None:
        return prog, ["o feed não respondeu a tempo"], None
    corpo, _, codigo = r.stdout.rpartition(b"\n")
    if codigo != b"200":
        return prog, [f"o feed respondeu {codigo.decode() or 'sem código'}"], None
    if b"<!ENTITY" in corpo:
        return prog, ["o feed tem entidades XML (recusado por segurança)"], None
    try:
        canal = ET.fromstring(corpo).find("channel")
    except ET.ParseError as e:
        return prog, [f"o feed não é XML válido ({e})"], None
    if canal is None:
        return prog, ["o feed não tem <channel>"], None
    itens = sorted(canal.findall("item"), key=data, reverse=True)
    if not itens:
        return prog, ["o feed não tem episódios"], None
    ultimo = email.utils.parsedate_to_datetime(itens[0].findtext("pubDate")).date().isoformat() if data(itens[0]) else None
    for item in itens[:EPISODIOS_A_TESTAR]:
        titulo = (item.findtext("title") or "").strip()[:50]
        anexo = item.find("enclosure")
        url = anexo.get("url") if anexo is not None else None
        if not url:
            erros.append(f"episódio sem áudio: {titulo}")
            continue
        if not url.startswith("https://"):
            erros.append(f"áudio sem HTTPS: {titulo}")
            continue
        a = curl(["-o", "/dev/null", "-r", "0-2047", "-w", "%{http_code} %{content_type}", url], 30)
        if a is None:
            erros.append(f"o áudio não respondeu a tempo: {titulo}")
            continue
        codigo, _, tipo = a.stdout.decode().partition(" ")
        if codigo not in ("200", "206"):
            erros.append(f"o áudio respondeu {codigo or 'sem código'}: {titulo}")
        elif not tipo.startswith("audio/"):
            erros.append(f"o ficheiro não é áudio ({tipo}): {titulo}")
    return prog, erros, ultimo


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else "catalogo.json"
    with open(caminho, encoding="utf-8") as f:
        cat = json.load(f)
    problemas = []
    ids, feeds, programas = set(), set(), []
    for fonte in cat.get("fontes", []):
        if not ID_VALIDO.match(fonte.get("id", "")) or fonte["id"] in ids:
            problemas.append(f"id de fonte inválido ou repetido: {fonte.get('id')}")
        ids.add(fonte.get("id"))
        if fonte.get("tipo") not in TIPOS:
            problemas.append(f"{fonte.get('id')}: tipo desconhecido")
        for prog in fonte.get("programas", []):
            for campo in ("id", "nome", "categoria", "feed"):
                if not prog.get(campo):
                    problemas.append(f"{prog.get('id')}: falta o campo {campo}")
            if not ID_VALIDO.match(prog.get("id", "")) or prog["id"] in ids:
                problemas.append(f"id de programa inválido ou repetido: {prog.get('id')}")
            ids.add(prog.get("id"))
            if prog.get("feed") in feeds:
                problemas.append(f"feed repetido: {prog.get('id')}")
            feeds.add(prog.get("feed"))
            programas.append(prog)
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        resultados = list(ex.map(verifica_programa, programas))
    for prog, erros, ultimo in resultados:
        estado = "ERRO" if erros else "ok"
        print(f"{estado:4} | {prog.get('id', '?'):55} | último: {ultimo or '?'}")
        for e in erros:
            print(f"       - {e}")
            problemas.append(f"{prog.get('id')}: {e}")
    bons = sum(1 for _, erros, _ in resultados if not erros)
    print(f"\n{bons} de {len(programas)} programas sem problemas.")
    for p in problemas:
        print("PROBLEMA:", p)
    sys.exit(1 if problemas else 0)


if __name__ == "__main__":
    main()

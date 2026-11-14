#!/usr/bin/env python3
"""Gera o catálogo v2 (`catalogo-v2.json`): o catálogo de sempre mais a
descrição curta e as pessoas de cada programa, para a pesquisa da app.

- Lê o `catalogo.json` (versão 1) e o feed de cada programa.
- `descricao`: a descrição do programa no feed, em texto simples, cortada
  a 160 caracteres (numa palavra inteira, com "…").
- `pessoas`: quem faz o programa. Vem do autor do feed (`itunes:author` do
  programa e dos episódios mais recentes), das etiquetas `podcast:person` e
  da lista escrita à mão em `pessoas.json`. Os nomes de rádios, jornais e
  televisões não contam como pessoas. Um nome que já é conhecido (de outro
  programa ou da lista) e aparece na descrição do programa também entra.
- O `catalogo.json` não muda: as versões antigas da app continuam a lê-lo.
- Um feed que não responde fica com a descrição e as pessoas que tinha no
  `catalogo-v2.json` anterior (se havia).

Uso: python3 v2.py [catalogo.json] [catalogo-v2.json]
Precisa apenas de Python 3 e do comando curl.
"""
import concurrent.futures
import html
import json
import os
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET

AGENTE = "Rubrica/1.0 (catalogo v2)"
LIMITE_DESCRICAO = 160
MAXIMO_PESSOAS = 8
ITUNES = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"
PODCAST = "{https://podcastindex.org/namespace/1.0}"

# Palavras que mostram que um "autor" é uma empresa, rádio ou marca, e não
# uma pessoa.
NAO_PESSOA = set(
    """radio rádio renascenca renascença rfm comercial m80 tsf mega hits cidade
    smooth fm observador expresso publico público correio manha manhã jornal
    negocios negócios eco economico económico sabado sábado bola record sic
    noticias notícias cnn portugal tvi sport tv media média multimedia
    multimédia grupo global impresa cofina medialivre trust news podcast
    podcasts rr lda sa s.a. produções producoes studio studios estúdio estudio
    omny spreaker anchor redação redacao edições edicoes desporto online
    digital lusa agência agencia equipa""".split()
)
SEPARADORES = re.compile(r"\s*(?:,|;|/|\||&|\+|\be\b|\band\b|\bcom\b)\s*", re.I)


def curl(url, limite=60):
    cmd = ["curl", "-sS", "-L", "--compressed", "--proto", "=https",
           "--proto-redir", "=https", "-m", str(limite), "-A", AGENTE, url]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=limite + 10)
    except subprocess.TimeoutExpired:
        return None
    return r.stdout if r.returncode == 0 else None


def texto_simples(t):
    """Sem HTML, sem entidades e com os espaços arrumados."""
    if not t:
        return ""
    t = html.unescape(t)
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"https?://\S+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def cortar(t, limite=LIMITE_DESCRICAO):
    """Corta numa palavra inteira; o resultado (com "…") tem no máximo
    `limite` caracteres."""
    if len(t) <= limite:
        return t
    corte = t[: limite - 1]
    espaco = corte.rfind(" ")
    if espaco > limite // 2:
        corte = corte[:espaco]
    return corte.rstrip(" ,.;:-–—") + "…"


def sem_acentos(t):
    return "".join(c for c in unicodedata.normalize("NFD", t.lower())
                   if unicodedata.category(c) != "Mn")


def parece_pessoa(nome, fonte):
    """Dois a quatro nomes com maiúscula e nenhum que seja de empresa."""
    palavras = nome.split()
    if not 2 <= len(palavras) <= 4 or len(nome) > 40:
        return False
    if sem_acentos(nome) == sem_acentos(fonte):
        return False
    pequenas = {"de", "da", "do", "dos", "das", "e"}
    for p in palavras:
        if p.lower() in pequenas:
            continue
        if not p[0].isupper() or not re.fullmatch(r"[\w'’.-]+", p):
            return False
        if sem_acentos(p).strip(".") in {sem_acentos(x) for x in NAO_PESSOA}:
            return False
        if p.isupper() and len(p) > 1:
            return False  # siglas: "SIC", "RFM"
    return True


def pessoas_do_texto(t, fonte):
    if not t:
        return []
    saida = []
    for parte in SEPARADORES.split(texto_simples(t)):
        parte = parte.strip(" .-–—()[]\"'")
        if parece_pessoa(parte, fonte):
            saida.append(parte)
    return saida


# Primeiros nomes frequentes: ajudam a reconhecer quem apresenta o programa
# no início da descrição ("Ana Galvão, Joana Marques e Inês Lopes Gonçalves
# são...").
PRIMEIROS_NOMES = set(
    """Ana Joana Inês Maria Marta Rita Sofia Catarina Teresa Helena Isabel Sara
    Mariana Beatriz Carolina Filipa Patrícia Paula Sónia Susana Raquel Rosa
    Clara Cristina Luísa Leonor Margarida Júlia Vanda Vera Alexandra Andreia
    João José António Manuel Francisco Pedro Paulo Nuno Rui Luís Miguel Carlos
    Jorge Ricardo Tiago Diogo Bruno André Gonçalo Hugo Vasco Duarte Bernardo
    Henrique Fernando Daniel David Filipe Sérgio Vítor Álvaro Tomás Guilherme
    Rodrigo Martim Afonso Joaquim Mário Marco Fábio Raul Gustavo Alexandre
    Fernanda Lourenço Salvador Simão Valter Artur Hélder César""".split()
)
# Só se procura no início da descrição, onde costuma estar quem apresenta.
INICIO_DESCRICAO = 300
NOME_PROPRIO = r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõçà'’]+(?:-[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõçà'’]+)?"


def nomes_na_descricao(descricao, primeiros, fonte):
    saida = []
    padrao = re.compile(
        r"(?<![\w])(%s(?:\s+(?:de|da|do|dos|das)?\s*%s){1,3})" % (NOME_PROPRIO, NOME_PROPRIO))
    for m in padrao.finditer(descricao[:INICIO_DESCRICAO]):
        nome = re.sub(r"\s+", " ", m.group(1)).strip()
        # Corta palavras pequenas soltas no fim ("Joana Marques da").
        nome = re.sub(r"\s+(de|da|do|dos|das)$", "", nome)
        if (nome.split()[0] in primeiros and len(nome.split()[-1]) >= 3
                and parece_pessoa(nome, fonte)):
            saida.append(nome)
    return saida


def ler_feed(feed):
    corpo = curl(feed)
    if not corpo or b"<!ENTITY" in corpo:
        return None
    try:
        raiz = ET.fromstring(corpo)
    except ET.ParseError:
        return None
    return raiz.find("channel")


def dados_do_feed(canal, fonte):
    descricao = ""
    for etiqueta in ("description", ITUNES + "summary", ITUNES + "subtitle"):
        descricao = texto_simples(canal.findtext(etiqueta))
        if descricao:
            break
    candidatos = []
    candidatos += pessoas_do_texto(canal.findtext(ITUNES + "author"), fonte)
    for pessoa in canal.iter(PODCAST + "person"):
        candidatos += pessoas_do_texto(pessoa.text, fonte)
    # Autores dos episódios: só os que se repetem (um convidado não conta).
    contagem = {}
    itens = canal.findall("item")[:20]
    for item in itens:
        for nome in set(pessoas_do_texto(item.findtext(ITUNES + "author"), fonte)):
            contagem[nome] = contagem.get(nome, 0) + 1
    minimo = 2 if len(itens) >= 4 else 1
    candidatos += [n for n, c in sorted(contagem.items(), key=lambda x: -x[1]) if c >= minimo]
    return descricao, candidatos


def sem_repetidos(nomes):
    vistos, saida = set(), []
    for n in nomes:
        chave = sem_acentos(n)
        if chave not in vistos:
            vistos.add(chave)
            saida.append(n)
    return saida


def main():
    origem = sys.argv[1] if len(sys.argv) > 1 else "catalogo.json"
    destino = sys.argv[2] if len(sys.argv) > 2 else "catalogo-v2.json"
    pasta = os.path.dirname(os.path.abspath(__file__))
    with open(origem, encoding="utf-8") as f:
        catalogo = json.load(f)
    anterior = {}
    if os.path.exists(destino):
        with open(destino, encoding="utf-8") as f:
            for fonte in json.load(f).get("fontes", []):
                for p in fonte.get("programas", []):
                    anterior[p["id"]] = p
    manual = {}
    caminho_manual = os.path.join(pasta, "pessoas.json")
    if os.path.exists(caminho_manual):
        with open(caminho_manual, encoding="utf-8") as f:
            manual = {k: v for k, v in json.load(f).items() if not k.startswith("_")}

    lista = [(fonte, p) for fonte in catalogo["fontes"] for p in fonte["programas"]]

    def um(par):
        fonte, p = par
        canal = ler_feed(p["feed"])
        if canal is None:
            return None
        return dados_do_feed(canal, fonte["nome"])

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as grupo:
        lidos = list(grupo.map(um, lista))

    # Nomes conhecidos: os autores de todos os feeds e a lista à mão. Um
    # nome conhecido que aparece na descrição de um programa também entra.
    conhecidos = set()
    for dados in lidos:
        if dados:
            conhecidos.update(dados[1])
    for nomes in manual.values():
        conhecidos.update(nomes)
    conhecidos_norm = {sem_acentos(n): n for n in conhecidos}
    primeiros = {n.split()[0] for n in conhecidos} | PRIMEIROS_NOMES

    falhas = 0
    for (fonte, p), dados in zip(lista, lidos):
        if dados is None:
            falhas += 1
            antes = anterior.get(p["id"], {})
            descricao_completa = None
            pessoas = list(antes.get("pessoas", []))
            descricao = antes.get("descricao", "")
            print(f"feed sem resposta: {p['id']}", file=sys.stderr)
        else:
            descricao_completa, pessoas = dados
            descricao = cortar(descricao_completa)
        if descricao_completa:
            alvo = " " + re.sub(r"[^\w]+", " ", sem_acentos(descricao_completa)) + " "
            for chave, nome in conhecidos_norm.items():
                if " " + chave + " " in alvo:
                    pessoas.append(nome)
            pessoas += nomes_na_descricao(descricao_completa, primeiros, fonte["nome"])
        pessoas = sem_repetidos(manual.get(p["id"], []) + pessoas)[:MAXIMO_PESSOAS]
        if descricao:
            p["descricao"] = descricao
        else:
            p.pop("descricao", None)
        if pessoas:
            p["pessoas"] = pessoas
        else:
            p.pop("pessoas", None)

    catalogo["versao"] = 2
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=2)
        f.write("\n")
    progs = [p for _, p in lista]
    print(f"{len(progs)} programas: {sum(1 for p in progs if p.get('descricao'))} com descrição, "
          f"{sum(1 for p in progs if p.get('pessoas'))} com pessoas, {falhas} feeds sem resposta")


if __name__ == "__main__":
    main()

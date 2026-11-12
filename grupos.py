#!/usr/bin/env python3
"""Arruma cada programa do catálogo num grupo (campo "grupo").

O grupo sai do tema do programa ("categoria"), com uma exceção: os programas
de comentário, opinião e debate estão quase todos em "Notícias" e não há
forma automática de os separar, por isso estão numa lista escrita à mão
(COMENTARIO). Para mudar um programa de grupo, mexe-se nessa lista e
corre-se outra vez:  python3 grupos.py
"""
import json
import sys

GRUPOS = {
    "informacao": "Informação",
    "comentario": "Comentário",
    "humor": "Humor",
    "desporto": "Desporto",
    "economia": "Economia",
    "sociedade": "Sociedade",
    "cultura": "Cultura e música",
    "familia": "Família",
    "saude": "Saúde e ciência",
}

POR_CATEGORIA = {
    "Notícias": "informacao",
    "Política": "informacao",
    "Humor": "humor",
    "Desporto": "desporto",
    "Economia": "economia",
    "Sociedade": "sociedade",
    "Geral": "sociedade",
    "Religião": "sociedade",
    "Lazer": "sociedade",
    "Crime": "sociedade",
    "Cultura": "cultura",
    "Música": "cultura",
    "História": "cultura",
    "Cinema e TV": "cultura",
    "Ficção": "cultura",
    "Família": "familia",
    "Saúde": "saude",
    "Ciência": "saude",
    "Tecnologia": "saude",
    "Educação": "saude",
}

# Comentário, opinião e debate. Fonte -> nomes dos programas, tal como estão
# no catálogo.
COMENTARIO = {
    "Renascença": [
        "Casa Comum", "São Bento à Sexta", "Visto de Fora",
        "Novas Crónicas da Idade Mídia", "Conversas Cruzadas",
    ],
    "Antena 1": [
        "Contraditório", "Radicais Livres (3ª Série)",
        "Radicais Livres (2ª Série)", "Geometria Variável", "Postal do Dia",
        "Entre Políticos", "O Fio da Meada", "Antena Aberta", "Visão Global",
    ],
    "TSF": [
        "Fórum TSF", "O Estado do Sítio", "Tem a Palavra",
        "Café Duplo, Ribau Esteves e Frederico Rosa",
        "Café Duplo, com Manuel Monteiro e Paula Marques",
        "Café Duplo, com Angélique da Teresa e Bernardo Pessanha",
    ],
    "RDP África": ["Debate Africano"],
    "Observador": [
        "Contra-Corrente", "O Bom, o Mau e o Vilão", "Ideias Feitas",
        "Gabinete de Guerra", "Realpolitik", "Conversas à Quinta",
        "Semáforo Político", "Vichyssoise", "E o vencedor é...",
    ],
    "Expresso": [
        "Comissão Política", "Bloco Central",
        "Miguel Sousa Tavares de Viva Voz", "Lei da Paridade",
        "O Mundo a Seus Pés", "Bloco de Leste", "À Direita",
    ],
    "Público": ["Poder Público"],
    "Jornal Económico": [
        "A Arte da Guerra", "A Arte do Possível",
        "Maquiavel para Principiantes",
    ],
    "Sábado": ["Conselho de Segurança"],
    "SIC Notícias": [
        "Programa Cujo Nome Estamos Legalmente Impedidos de Dizer",
        "Torto e Direito", "Eixo do Mal", "Leste/Oeste de Nuno Rogeiro",
        "Expresso da Meia-Noite", "Guerra Fria", "Antes pelo contrário",
        "Linhas Vermelhas", "Facto Político",
        "Esta Semana com Maria João Avillez e Ricardo Costa", "Ana Gomes",
        "As Causas de José Miguel Júdice", "Luís Marques Mendes",
        "Pedro Nuno Santos", "O Tabu de Francisco Louçã",
    ],
    "CNN Portugal": [
        "O Princípio da Incerteza", "Crossfire", "Contrapoder",
        "Entre Dois Mundos com Gouveia e Melo",
    ],
    "TVI": [
        "Global com Paulo Portas", "5.ª Coluna com Miguel Sousa Tavares",
    ],
    "RTP": [
        "Choque de Ideias", "Telejornal - Comentário Domingo",
        "É Ou Não É? - O Grande Debate", "Pontos de Vista", "O Outro Lado",
        "O Último Apaga a Luz",
    ],
}


def main() -> int:
    with open("catalogo.json", encoding="utf-8") as f:
        catalogo = json.load(f)
    por_usar = {(fonte, nome) for fonte, nomes in COMENTARIO.items() for nome in nomes}
    contas = dict.fromkeys(GRUPOS, 0)
    for fonte in catalogo["fontes"]:
        for programa in fonte["programas"]:
            chave = (fonte["nome"], programa["nome"])
            if chave in por_usar:
                por_usar.discard(chave)
                grupo = "comentario"
            else:
                grupo = POR_CATEGORIA.get(programa.get("categoria", ""))
                if grupo is None:
                    print(f"Tema sem grupo: {programa.get('categoria')!r} em {chave}")
                    return 1
            programa["grupo"] = grupo
            contas[grupo] += 1
    if por_usar:
        print("Na lista de comentário mas não no catálogo:")
        for chave in sorted(por_usar):
            print("  ", chave)
        return 1
    with open("catalogo.json", "w", encoding="utf-8") as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=2)
        f.write("\n")
    for grupo, nome in GRUPOS.items():
        print(f"{contas[grupo]:5d}  {nome}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

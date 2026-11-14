# Catálogo — Rubrica

Lista de rádios, jornais, televisões e programas que a app mostra. A app lê o ficheiro `catalogo.json` deste repositório e depois vai buscar os episódios diretamente ao feed RSS de cada programa.

- Só entram feeds RSS públicos e confirmados.
- O áudio toca sempre a partir do feed original; este repositório não guarda ficheiros de áudio nem logos.
- Alterar o catálogo não exige publicar uma nova versão da app.

## Formato

```json
{
  "versao": 1,
  "atualizado": "AAAA-MM-DD",
  "fontes": [
    {
      "id": "exemplo-radio",
      "nome": "Rádio Exemplo",
      "tipo": "radio",
      "programas": [
        {
          "id": "exemplo-programa",
          "nome": "Programa Exemplo",
          "categoria": "Humor",
          "grupo": "humor",
          "feed": "https://example.com/feed.xml",
          "capa": "https://example.com/capa.jpg",
          "ultimo": "2026-11-13"
        }
      ]
    }
  ]
}
```

| Campo | Significado |
|---|---|
| `versao` | Versão do formato; a app ignora versões que não conhece |
| `fontes[].tipo` | `radio`, `jornal` ou `tv` |
| `programas[].categoria` | Tema do programa, tal como vem do feed |
| `programas[].grupo` | Opcional. O grupo em que a app arruma o programa: `informacao`, `comentario`, `humor`, `desporto`, `economia`, `sociedade`, `cultura`, `familia` ou `saude`. Sai do tema, exceto o comentário, que está numa lista escrita à mão em `grupos.py`. Se faltar, a app deduz o grupo do tema |
| `programas[].feed` | Endereço do feed RSS público do programa |
| `programas[].ultimo` | Opcional. O dia (AAAA-MM-DD, UTC) do episódio mais recente do feed. A app usa-o para marcar os programas em **arquivo** (sem episódios há mais de um ano) e contar os **ativos** (episódio nos últimos 90 dias). As versões antigas da app ignoram-no. Atualiza-se com `python3 ultimo.py` |
| `programas[].capa` | Opcional. Endereço da capa, tal como vem no feed do programa. Serve para a app mostrar as listas sem descarregar todos os feeds. Se faltar ou falhar, a app mostra as iniciais do programa |

O exemplo acima é fictício. A ordem dos programas no ficheiro é a ordem em que a app os mostra.

## Grupos

Depois de acrescentar programas, correr `python3 grupos.py`: preenche o campo `grupo` de todos. Para mudar um programa para "Comentário" (ou tirá-lo de lá), mexe-se na lista `COMENTARIO` desse ficheiro e corre-se outra vez.

## O que entra no catálogo

- Tudo o que cada rádio, jornal ou televisão publica como podcast com feed RSS aberto (o mesmo que usam as outras apps de podcasts), incluindo programas já terminados.
- Feed e áudio servidos por HTTPS, sem login nem assinatura.
- Fica de fora: vídeo, e o que não responde por HTTPS ou tem o áudio em erro.

Versão de 2026-11-14: 822 programas de 23 fontes. A RTP (Antena 1, 2 e 3, RDP África, RDP Internacional, Rádio Zig Zag e RTP) e a Rádio Miúdos saíram em 2026-11-14: os termos da RTP só autorizam uso pessoal e a app vai ter anúncios; os programas para crianças saem por causa dos anúncios.

| Tipo | Fontes |
|---|---|
| Rádios | Renascença, RFM, Rádio Comercial, M80, TSF, Mega Hits, Cidade FM, Smooth FM |
| Jornais e revistas | Observador, Expresso, Público, Correio da Manhã, Jornal de Negócios, ECO, Jornal Económico, Sábado, A Bola, Record |
| Televisões | SIC Notícias, SIC, CNN Portugal, TVI, Sport TV |

A ordem dos programas dentro de cada fonte é a ordem "Mais ouvidos" da app: primeiro os mais populares, depois os que têm episódios recentes, por fim o arquivo.

## Data do último episódio

```
python3 ultimo.py
```

Lê o feed de cada programa e escreve no campo `ultimo` o dia do episódio mais recente. Um feed que não responde fica com a data que já tinha. No fim diz quantos estão ativos e em arquivo. Corre-se à mão (por agora), depois de acrescentar programas ou de vez em quando.

Versão de 2026-11-14: os 822 programas têm data; 380 ativos e 314 em arquivo.

## Catálogo v2 (descrição e pessoas)

```
python3 v2.py
```

Gera o `catalogo-v2.json`: o mesmo catálogo (com `"versao": 2`) e, em cada programa, dois campos novos para a pesquisa da app (a partir da versão da fase 3):

| Campo | Significado |
|---|---|
| `programas[].descricao` | A descrição do programa no feed, em texto simples, cortada a 160 caracteres |
| `programas[].pessoas` | Quem faz o programa: o autor do feed e dos episódios, as etiquetas `podcast:person`, os nomes conhecidos que aparecem no início da descrição e a lista à mão em `pessoas.json`. Nunca nomes de rádios, jornais ou televisões. No máximo 8 |

- O `catalogo.json` (versão 1) não muda: as apps antigas continuam a lê-lo. A app nova lê primeiro o `catalogo-v2.json` e, se faltar, o `catalogo.json`.
- Corre-se depois de mudar o `catalogo.json` (e, se der jeito, uma vez por semana). Um feed que não responde fica com a descrição e as pessoas que já tinha.
- Para um nome que os feeds não dizem, acrescenta-se em `pessoas.json` e corre-se outra vez.

Versão de 2026-11-14: 822 programas, todos com descrição; 464 com pessoas.

## Verificar o catálogo

```
python3 verificar.py
```

O script confirma que cada feed responde por HTTPS e que os 3 episódios mais recentes têm áudio acessível. Precisa apenas de Python 3 e do `curl`. Correr sempre antes de alterar o `catalogo.json`.

## Pedidos de remoção

Se é responsável por um destes programas e quer que seja retirado, abra um *issue* neste repositório. O programa é removido do catálogo sem mais perguntas.

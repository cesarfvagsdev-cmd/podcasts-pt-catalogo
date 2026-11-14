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
          "capa": "https://example.com/capa.jpg"
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

## Verificar o catálogo

```
python3 verificar.py
```

O script confirma que cada feed responde por HTTPS e que os 3 episódios mais recentes têm áudio acessível. Precisa apenas de Python 3 e do `curl`. Correr sempre antes de alterar o `catalogo.json`.

## Pedidos de remoção

Se é responsável por um destes programas e quer que seja retirado, abra um *issue* neste repositório. O programa é removido do catálogo sem mais perguntas.

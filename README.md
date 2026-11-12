# Catálogo — Rubrica

Lista de rádios, jornais e programas que a app mostra. A app lê o ficheiro `catalogo.json` deste repositório e depois vai buscar os episódios diretamente ao feed RSS de cada programa.

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
          "feed": "https://example.com/feed.xml"
        }
      ]
    }
  ]
}
```

| Campo | Significado |
|---|---|
| `versao` | Versão do formato; a app ignora versões que não conhece |
| `fontes[].tipo` | `radio` ou `jornal` |
| `programas[].feed` | Endereço do feed RSS público do programa |

O exemplo acima é fictício. A ordem dos programas no ficheiro é a ordem em que a app os mostra.

## O que entra no catálogo

- Programas publicados pela própria rádio ou jornal, com feed RSS aberto (o mesmo que usam as outras apps de podcasts).
- Feed e áudio servidos por HTTPS, sem login nem assinatura.
- Fica de fora: vídeo, programas de televisão, conteúdo patrocinado e podcasts de autores independentes apenas alojados na mesma plataforma.

Primeira versão (2026-11-12): 141 programas de 10 fontes — Renascença, RFM, Rádio Comercial, M80, Antena 1, Antena 3, TSF, Observador, Expresso e Público.

## Verificar o catálogo

```
python3 verificar.py
```

O script confirma que cada feed responde por HTTPS e que os 3 episódios mais recentes têm áudio acessível. Precisa apenas de Python 3 e do `curl`. Correr sempre antes de alterar o `catalogo.json`.

## Pedidos de remoção

Se é responsável por um destes programas e quer que seja retirado, abra um *issue* neste repositório. O programa é removido do catálogo sem mais perguntas.

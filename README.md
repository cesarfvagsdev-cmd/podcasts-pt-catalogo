# Catálogo — Podcasts PT

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

O exemplo acima é fictício. A lista real começa vazia e é preenchida à medida que cada feed é confirmado.

## Pedidos de remoção

Se é responsável por um programa listado e quer que seja retirado, abra um pedido em "Issues" neste repositório.

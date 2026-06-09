import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from notion_client import Client

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


NOTION_TOKEN = os.getenv("NOTION_TOKEN")

if not NOTION_TOKEN:
    raise ValueError("A variavel de ambiente NOTION_TOKEN deve ser definida.")

notion = Client(auth=NOTION_TOKEN)

mcp = FastMCP("mcp-notion-python")


def _extract_title(item: dict[str, Any]) -> str:
    """
    Extrai o título legível de um item retornado pela API do Notion.

    A API do Notion retorna títulos em formatos diferentes para databases e
    páginas. Para databases, o título fica diretamente no campo ``title``.
    Para páginas, o título fica dentro de uma propriedade cujo tipo é
    ``"title"``.

    Args:
        item: Dicionário representando um objeto do Notion, como uma página
            ou database.

    Returns:
        O título extraído como texto simples. Caso nenhum título seja
        encontrado, retorna ``"(sem titulo)"``.
    """
    if item.get("object") == "database":
        title = item.get("title", [])
        return "".join(part.get("plain_text", "") for part in title) or "(sem titulo)"

    properties = item.get("properties") or {}
    for property_data in properties.values():
        if property_data.get("type") == "title":
            title = property_data.get("title", [])
            return "".join(part.get("plain_text", "") for part in title) or "(sem titulo)"

    return "(sem titulo)"


@mcp.tool()
def notion_test_connection() -> dict[str, Any]:
    """
    Testa a conexao do servidor MCP com a API do Notion.

    Use esta tool para verificar se o token configurado em NOTION_TOKEN
    esta valido e se a integracao consegue autenticar no Notion.

    Returns:
        Um dicionario com success=true e os dados basicos do bot autenticado,
        ou success=false com a mensagem de erro retornada pela API.
    """

    try:
        bot_user = notion.users.me()

        return {
            "success": True,
            "message": f"Conexao bem-sucedida! O bot esta autenticado como {bot_user.get('name')}.",
            "bot": {
                "id": bot_user.get("id"),
                "name": bot_user.get("name"),
                "type": bot_user.get("type"),
            },
        }

    except Exception as error:
        return {
            "success": False,
            "message": "Falha ao conectar com o Notion.",
            "error": str(error),
        }


@mcp.tool()
def notion_search_file(query: str, page_size: int = 10) -> dict[str, Any]:
    """
    Busca paginas e databases acessiveis pela integracao do Notion.

    Use esta tool quando precisar encontrar um arquivo, pagina ou database
    pelo nome ou por um termo de busca. A busca usa a API oficial do Notion
    e retorna metadados suficientes para abrir ou referenciar o resultado.

    Args:
        query: Texto que sera pesquisado no Notion.
        page_size: Quantidade maxima de resultados retornados. O valor e
            limitado internamente entre 1 e 100.

    Returns:
        Um dicionario com success=true, a lista de resultados encontrados,
        informacoes de paginacao e o cursor para continuar a busca quando
        has_more=true. Em caso de falha, retorna success=false e o erro.
    """

    try:
        safe_page_size = max(1, min(page_size, 100))
        response = notion.search(query=query, page_size=safe_page_size)

        results = []
        for item in response.get("results", []):
            results.append(
                {
                    "id": item.get("id"),
                    "object": item.get("object"),
                    "title": _extract_title(item),
                    "url": item.get("url"),
                    "last_edited_time": item.get("last_edited_time"),
                }
            )

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "has_more": response.get("has_more", False),
            "next_cursor": response.get("next_cursor"),
            "results": results,
        }

    except Exception as error:
        return {
            "success": False,
            "message": "Falha ao buscar no Notion.",
            "error": str(error),
        }


if __name__ == "__main__":
    print(notion_test_connection())
    mcp.run()

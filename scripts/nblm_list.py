import asyncio
from notebooklm import NotebookLMClient

async def main():
    # Authenticate (uses saved browser state from a previous login)
    async with await NotebookLMClient.from_storage() as client:
        # List all available notebooks
        notebooks = await client.notebooks.list()
        
        print(f"Found {len(notebooks)} notebooks:")
        for nb in notebooks:
            print(f"- {nb.title} (ID: {nb.id})")

if __name__ == "__main__":
    asyncio.run(main())

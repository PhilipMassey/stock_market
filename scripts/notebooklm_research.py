import os
import asyncio
from sec_api import QueryApi
from notebooklm import NotebookLMClient

# 1. SETUP: Read API key from environment
sec_query = QueryApi(api_key=os.environ.get("SEC_API_KEY", ""))

async def automate_research(ticker, company_name):
    # STEP A: Find the latest filing URLs automatically
    # We query for the most recent 10-K (Annual) for this ticker
    query = {
        "query": { "query_string": { 
            "query": f"ticker:{ticker} AND formType:\"10-K\"" 
        }},
        "sort": [{ "filedAt": { "order": "desc" } }]
    }
    filings = sec_query.get_filings(query)
    annual_report_url = filings['filings'][0]['linkToFilingDetails']
    #annual_report_url = 'https://www.sec.gov/Archives/edgar/data/1298946/000129894625000015/drh-20241231.htm'
    quarterly_report_url = 'https://www.investing.com/news/transcripts/earnings-call-transcript-diamondrock-beats-q4-2025-expectations-93CH-4532045'
    # STEP B: Connect to NotebookLM
    async with await NotebookLMClient.from_storage() as client:
        # Create and name the notebook
        nb_name = f"{ticker} {company_name}"
        notebook = await client.notebooks.create(title=nb_name)
        
        # STEP C: Add the sources found via API
        await client.sources.add_url(notebook.id, annual_report_url, wait=True)
        await asyncio.sleep(1)  # Short pause to let the RPC session "breathe"
        await client.sources.add_url(notebook.id, quarterly_report_url, wait=True)

        # STEP D: Ask your synthesis question
        #prompt = "Synthesize the newly added earnings call transcripts and annual reports information to provide a comprehensive update on their financial performance, major projects and strategic outlook."
        #analysis = await client.chat.ask(notebook.id, prompt)
        
        #print(f"Research for {ticker} complete:\n", analysis.answer)
        print(f"Research for {ticker} complete:\n", notebook.id)

if __name__ == "__main__":
    # Run the automation
    asyncio.run(automate_research("DRH", "DiamondRock Hospitality Company"))

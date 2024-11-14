
# Shop-Assist Repository


## Overview 

- Repository for Crawling Retailer websites & Assistant for Answering questions
- `productinfo/` contains a Scrapy based crawler which processes html / generates Embedding and stores to a Vector DB (postgres right now)
- `copilot/` contains a FastAPI based backend which talks to VectorDB / LLM to respond to questions based on questions 
- `copilot-fe/` contains a React / Next.js based FE which renders the frontend and communicates to the Copilot BE.

## Instructions 

### Crawling (Retailer) Websites 

- Create a `.env` file in the `productinfo/productinfo/` directory
- Populate it with env variables:
  - POSTGRES_DB
  - POSTGRES_HOST
  - POSTGRES_USER
  - POSTGRES_PASSWORD
  - OPENAI_API_KEY
- TODO: Instructions to setup depedencies (including separate pip env)
- Make sure the Postgres DB is setup as described in the `data/setup_db.sql` file
- From the `productinfo` directory, run
  ```
  scrapy crawl link -a domain=www.bearmattress.com
  ```

#### Notes: 

- Currently scraping is slightly specialized for a specific retailer, though we are only using the html text for generating the Embedding, so we can delete all the retailer specific logic in the `link_spider.py` 
- Processing and converting text to Embedding is done in `pipelines.py`, but the functionality for generating the Embeddings can be made into a library. 
- Might be worth thinking about using the llama_index `VectorStoreIndex` for this, or invest time in improving tokenization / chunking etc. for the text processing library.

### Running Copilot BE

- Navigate to `copilot/` directory
- Create a `.env` file in the `copilot/` directory
- Populate it with env variables:
- Populate it with env variables:
  - POSTGRES_DB
  - POSTGRES_HOST
  - POSTGRES_USER
  - POSTGRES_PASSWORD
  - OPENAI_API_KEY
- run `pip install -r requirements.txt`
- run `uvicorn main:app --reload`

### Running Copilot FE

- Navigate to `copilot/fe` directory
- run `npm install` to install all required packages from `packages*.json`
- run `npm run dev`

#### Notes

- Websocket connection to BE is specified directly in code in `src/app/page.tsx`, this should be put in an .env file or something
- UI components need to split out and "Componentized"

# GPT_PDF
This is for a coding challenge to build a full-stack app to handle uploading of PDF and using GenAI to parse them

## Project Setup

Follow the instructions below to set up the project on your local machine for development and testing purposes.

1. Clone the repository:
    ```
    git clone https://github.com/brekru212/GPT_PDF.git
    ```

    ```
    cd GPT_PDF
    ```
2. Install server dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Navigate into the `web` directory and build the Next.js project (make sure you have NVM installed):
    ```
    cd web
    npm install
    npm run build
    ```
    Wait for the build process to complete. The front end is only meant to be exported. I did not feel like setting up Typescript and React.

4. Ensure you have an API key from OpenAI.

5. Set up the required environment variable with your OpenAI API key:
    ```
    export OPENAI_API_KEY=your_openai_key
    ```
   Replace `your_openai_key` with your actual OpenAI key.
6. Go back to the root directory and run the Python application:
    ```
    cd ..
    python app.py
    ```
    Navigate to the printed URL. `http://127.0.0.1:5000/`
7. Make sure that any files you want to upload are added to the `data` directory

Things I would have liked to add if I had more time:
- Would like to play with the temperature and different models to see if results varied
- Would like to have some more time to see if having a "personalized trained collection" of invoice pdfs for a given customer can give some more interesting insight
   
   - I tried various ways to see if pre-loading all the PDFs onto chatgpt would give interesting answers (i.e. How many shipping came from Supplier x, how much is owed from supplier y) but kept running into hallucination problem
- Would like to see if having metadata stored in a vector db or graph db could lead to some more modular development
- Would like to add some gracefully shutdown when app is closed
- Type-checking and using of ORM for data sql classes
- Would love to abstract more code in the `pdf.py` file
- Local testing

Local machine:
- Using python 3.8 on 2021 MacBook Pro Apple M1 chip



This repo was inspired by: https://github.com/alexbenko/AskGPT
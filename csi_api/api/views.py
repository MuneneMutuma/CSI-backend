from django.shortcuts import render
import pysolr
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import QuerySerializer

from langchain.llms import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv, find_dotenv
import os
from time import time

solr = pysolr.Solr('http://localhost:8983/solr/CSI', always_commit=True)

load_dotenv('../../.env')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

def summarize(text):
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)
    summary_template = PromptTemplate.from_template(
                    """
                    Given here is a case file. please give a summary of it with the following details: 
                        1. The Parties, 
                        2. The charges
                        3. A list of clauses and statutes used
                        4. The final judgment 
                        
                        {file}
                    """)
    summary_chain = LLMChain(llm=llm, prompt=summary_template, verbose=True)
    result = summary_chain.run(file=text)

    return result

# Create your views here.
class QueryAPIView(APIView):
    def post(self, request):
        start = time
        serializer = QuerySerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            query = data['query']
            results = solr.search('text: f"{query}"', **{'hl': 'true', 'hl.fragsize': 4})
            files = []

            for result in results:
                files.append(result)
            
            summary = summarize(files[0]['text'])

            return Response({'data': files, 'summary': summary})
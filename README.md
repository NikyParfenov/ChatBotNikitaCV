# Rheem_customer_support

Don't forget update OPENAI_API_KEY в **.env**

Run chatbot
```commandline
docker-compose up --build
```

Current API endpoint for sending prompts:  
http://ec2-3-67-177-126.eu-central-1.compute.amazonaws.com:8000/api/upload-text/

Example of prompt body:  
```commandlin
{
    "content": "I've got A126 code, what is that and how can I solve the problem?",
    "chat_id": 0
}
```
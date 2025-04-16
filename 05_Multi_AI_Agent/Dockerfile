# Python ka official image use karo (tumhari .python-version se match karo)
FROM python:3.12-slim

# Container ke andar working directory set karo
WORKDIR /app

# Project ke saare files container me copy karo
COPY . /app

# Dependencies install karo requirements.txt se
RUN pip install --no-cache-dir -r requirements.txt

# Chainlit ka port expose karo (default 8000)
EXPOSE 8000

# Chainlit ke sath bot chalao, host ko 0.0.0.0 pe bind karo
CMD ["chainlit", "run", "My_Agent.py", "--host", "0.0.0.0", "--port", "8000"]
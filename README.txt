Arquivos gerados — modo HTML + API
Conteúdo:
- app.py              -> Flask API (usa sqlite inventario.db)
- requirements.txt    -> pip install -r requirements.txt
- index.html          -> frontend (aberto direto ou servido estaticamente)
- css/styles.css
- js/script.js
- uploads/            -> pasta de uploads (criada)

Como usar:
1) Na pasta do projeto, instale dependências:
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate
   pip install -r requirements.txt

2) Rode o backend:
   python app.py
   -> roda em http://127.0.0.1:5000

3) Abra o frontend:
   - Recomendado: sirva estaticamente (prático e evita bloqueios do file://)
     python -m http.server 8000
     e abra http://127.0.0.1:8000/index.html
   - Ou abra index.html diretamente (file://). CORS está habilitado no backend,
     mas alguns navegadores bloqueiam requests de file://. Se der erro, use o http.server.

Observações:
- O frontend aponta para API em http://127.0.0.1:5000 (API_BASE).
- Se o backend estiver em outro IP/porta, edite js/script.js e atualize API_BASE.

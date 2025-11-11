from flask import Flask, request, jsonify, send_from_directory, render_template, send_file
from flask_cors import CORS
import sqlite3, os
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ======================
# CONFIGURAÇÃO DO APP
# ======================
app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DB_FILE = os.path.join(BASE_DIR, 'inventario.db')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ======================
# BANCO DE DADOS
# ======================
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            local TEXT,
            modelo TEXT,
            data_compra TEXT,
            valor REAL,
            serie TEXT,
            descricao TEXT,
            imagem TEXT
        )''')

# ======================
# ROTAS PRINCIPAIS
# ======================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/items', methods=['GET'])
def listar():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        items = [dict(row) for row in conn.execute('SELECT * FROM items')]
    return jsonify(items)

@app.route('/api/items', methods=['POST'])
def criar():
    try:
        data = request.form.to_dict()
        file = request.files.get('imagem')
        filename = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        valor = float(data.get('valor') or 0)

        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('''INSERT INTO items (nome, local, modelo, data_compra, valor, serie, descricao, imagem)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (data.get('nome'), data.get('local'), data.get('modelo'),
                          data.get('data_compra'), valor,
                          data.get('serie'), data.get('descricao'), filename))
            conn.commit()
        return jsonify({'status': 'ok'})
    except Exception as e:
        print("Erro ao criar item:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/items/<int:id>', methods=['PUT'])
def atualizar(id):
    try:
        data = request.form.to_dict()
        file = request.files.get('imagem')
        filename = None

        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            old_item = conn.execute('SELECT * FROM items WHERE id=?', (id,)).fetchone()
            if not old_item:
                return jsonify({'error': 'Item não encontrado'}), 404

            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                filename = old_item['imagem']

            valor = float(data.get('valor') or 0)

            conn.execute('''UPDATE items
                            SET nome=?, local=?, modelo=?, data_compra=?, valor=?, serie=?, descricao=?, imagem=?
                            WHERE id=?''',
                         (data.get('nome'), data.get('local'), data.get('modelo'),
                          data.get('data_compra'), valor,
                          data.get('serie'), data.get('descricao'), filename, id))
            conn.commit()
        return jsonify({'status': 'updated'})
    except Exception as e:
        print("Erro ao atualizar item:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/items/<int:id>', methods=['DELETE'])
def apagar(id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('DELETE FROM items WHERE id=?', (id,))
            conn.commit()
        return jsonify({'status': 'deleted'})
    except Exception as e:
        print("Erro ao deletar item:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ======================
# RELATÓRIO PDF
# ======================
@app.route('/api/pdf')
def gerar_pdf():
    caminho_pdf = os.path.join(BASE_DIR, 'inventario.pdf')
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        items = [dict(row) for row in conn.execute('SELECT * FROM items ORDER BY id')]

    c = canvas.Canvas(caminho_pdf, pagesize=A4)
    largura, altura = A4
    y = altura - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, y, "Relatório de Inventário de Informática")
    y -= 40
    c.setFont("Helvetica", 11)

    for item in items:
        texto = f"{item['id']:03d} - {item.get('nome','')} | {item.get('local','')} | {item.get('modelo','')} | R$ {item.get('valor') or 0:.2f}"
        c.drawString(40, y, texto)
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = altura - 50

    c.save()
    return send_file(caminho_pdf, mimetype='application/pdf', as_attachment=False)

# ======================
# EXECUÇÃO
# ======================
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Servidor rodando em http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)

import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import PyPDF2
import docx
from bs4 import BeautifulSoup
import uuid
from datetime import datetime
import random

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SAMPLES_FOLDER'] = 'sample_contracts'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SAMPLES_FOLDER'], exist_ok=True)

client = OpenAI(
    base_url="https://api.gapgpt.app/v1",
    api_key="sk-BUgL1TkYyBcgWmigU0MDmG3KQOn0iBZ05NdckPB621x6PeKZ"
)
MODEL_NAME = "gemini-3-pro-preview"

# --- دیتابیس ---
def get_db_connection():
    conn = sqlite3.connect('contracts.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS contracts (
            id TEXT PRIMARY KEY,
            title TEXT,
            party_a TEXT,
            party_b TEXT,
            content TEXT,
            raw_data TEXT,
            created_at TEXT,
            ref_number TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- توابع کمکی ---
def ask_llm(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "شما یک وکیل و متخصص حقوقی ارشد در ایران هستید. خروجی شما باید منحصرا با فرمت HTML شامل تگ های div, p, h1, h2, h3, h4, table, ul, li با استایل های درون خطی (inline-css) رسمی، راست چین (rtl) و کاملا توجیه شده (text-align: justify) باشد. از قرار دادن تگ های <html> و <body> خودداری کنید."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.replace('```html', '').replace('```', '')
    except Exception as e:
        return f"<div style='color:red; padding:20px;'>خطا در ارتباط با مدل زبانی: {str(e)}</div>"

def extract_pages_from_word(filepath):
    pages = []
    try:
        doc = docx.Document(filepath)
        chunk = []
        page_num = 1
        for para in doc.paragraphs:
            if para.text.strip():
                chunk.append(para.text)
            if len(chunk) >= 15: # هر 15 پاراگراف یک صفحه
                pages.append({"page_num": page_num, "content": "\n".join(chunk)})
                chunk = []
                page_num += 1
        if chunk:
            pages.append({"page_num": page_num, "content": "\n".join(chunk)})
    except Exception as e:
        pages.append({"page_num": 1, "content": f"خطا در خواندن فایل: {str(e)}"})
    return pages

# --- مسیرها ---

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

@app.route('/api/generate', methods=['POST'])
def generate_contract():
    data = request.json
    
    # تولید شماره مرجع و تاریخ
    ref_number = f"CTR-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    persian_date = "۱۴۰۵/۰۴/۰۲" # تاریخ فرضی یا استفاده از کتابخانه jdatetime
    
    prompt = f"""
    لطفا متن یک قرارداد کاملا رسمی و حقوقی بر اساس اطلاعات زیر تنظیم کنید.
    نوع قرارداد: {data.get('contractType', 'نامشخص')}
    موضوع قرارداد: {data.get('subject', 'نامشخص')}
    مشخصات طرف اول: {data.get('partyA', 'نامشخص')}
    مشخصات طرف دوم: {data.get('partyB', 'نامشخص')}
    مبلغ قرارداد: {data.get('amount', 'نامشخص')}
    مدت قرارداد: {data.get('duration', 'نامشخص')}
    تعهدات طرف اول: {data.get('obligationsA', 'نامشخص')}
    تعهدات طرف دوم: {data.get('obligationsB', 'نامشخص')}
    شروط: {data.get('clauses', 'نامشخص')}
    نکات خاص: {data.get('specialNotes', 'نامشخص')}
    
    متن قرارداد باید شامل ماده‌های استاندارد (طرفین، موضوع، مبلغ، مدت، تعهدات، فورس ماژور و حل اختلاف) باشد. فقط متن مواد و بندها را با HTML زیبا و ساختارمند تولید کنید (محل امضا در انتهای متن باشد).
    """
    
    llm_content = ask_llm(prompt)
    
    # قالب بندی حرفه ای A4
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={ref_number}"
    
    final_html = f"""
    <div class="a4-container" style="background: white; width: 210mm; min-height: 297mm; margin: 0 auto; padding: 20mm; box-sizing: border-box; box-shadow: 0 0 10px rgba(0,0,0,0.1); border: 1px solid #ccc; position: relative;">
        <!-- سربرگ -->
        <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #1e3a8a; padding-bottom: 10px; margin-bottom: 20px;">
            <div style="text-align: right; width: 33%;">
                <img src="{qr_url}" alt="QR Code" style="width: 70px; height: 70px;">
            </div>
            <div style="text-align: center; width: 34%;">
                <h2 style="margin: 0; color: #1e3a8a; font-size: 24px;">بسمه تعالی</h2>
                <h3 style="margin: 5px 0 0 0; color: #333; font-size: 18px;">قرارداد {data.get('contractType', '')}</h3>
            </div>
            <div style="text-align: left; width: 33%; font-size: 12px; line-height: 1.8;">
                <div><strong>تاریخ:</strong> {persian_date}</div>
                <div><strong>شماره مرجع:</strong> <span dir="ltr">{ref_number}</span></div>
                <div><strong>پیوست:</strong> ندارد</div>
            </div>
        </div>
        
        <!-- محتوای قرارداد -->
        <div style="font-size: 14px; line-height: 2; text-align: justify; color: #000;">
            {llm_content}
        </div>
    </div>
    """
    
    return jsonify({"html": final_html, "ref_number": ref_number})

@app.route('/api/contracts', methods=['GET', 'POST'])
def handle_contracts():
    conn = get_db_connection()
    if request.method == 'POST':
        data = request.json
        contract_id = data.get('id') or str(uuid.uuid4())
        ref_number = data.get('ref_number', 'N/A')
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn.execute('''
            INSERT OR REPLACE INTO contracts (id, title, party_a, party_b, content, raw_data, created_at, ref_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (contract_id, data.get('subject'), data.get('partyA'), data.get('partyB'), data.get('html'), str(data), now, ref_number))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "id": contract_id})
        
    elif request.method == 'GET':
        contracts = conn.execute('SELECT * FROM contracts ORDER BY created_at DESC').fetchall()
        conn.close()
        return jsonify([dict(row) for row in contracts])

@app.route('/api/contracts/<id>', methods=['GET', 'DELETE'])
def handle_single_contract(id):
    conn = get_db_connection()
    if request.method == 'GET':
        contract = conn.execute('SELECT * FROM contracts WHERE id = ?', (id,)).fetchone()
        conn.close()
        return jsonify(dict(contract) if contract else {})
    elif request.method == 'DELETE':
        conn.execute('DELETE FROM contracts WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})

# --- مسیرهای مربوط به فایل ها و نمونه ها ---

@app.route('/api/samples', methods=['GET'])
def get_samples():
    files = []
    for f in os.listdir(app.config['SAMPLES_FOLDER']):
        if f.endswith('.doc') or f.endswith('.docx'):
            files.append(f)
    return jsonify(files)

@app.route('/api/samples/<filename>', methods=['GET'])
def load_sample(filename):
    filepath = os.path.join(app.config['SAMPLES_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "فایل یافت نشد"}), 404
    pages = extract_pages_from_word(filepath)
    return jsonify({"pages": pages})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "فایلی ارسال نشد"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "فایلی انتخاب نشد"}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    pages = []
    ext = file.filename.split('.')[-1].lower()
    
    try:
        if ext == 'pdf':
            reader = PyPDF2.PdfReader(filepath)
            for i, page in enumerate(reader.pages):
                pages.append({"page_num": i+1, "content": page.extract_text()})
        elif ext in ['doc', 'docx']:
            pages = extract_pages_from_word(filepath)
        elif ext in ['html', 'htm']:
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                pages.append({"page_num": 1, "content": soup.get_text(separator='\n')})
        else:
            return jsonify({"error": "فرمت فایل پشتیبانی نمی شود"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
            
    return jsonify({"pages": pages})

@app.route('/api/analyze', methods=['POST'])
def analyze_contract():
    data = request.json
    content = data.get('content')
    action = data.get('action')
    custom_prompt = data.get('customPrompt', '')
    
    if action == 'analyze':
        prompt = f"قرارداد زیر را از نظر ریسک های احتمالی و حقوقی تحلیل کنید و به صورت HTML رسمی گزارش دهید:\n\n{content}"
    elif action == 'fix':
        prompt = f"ایرادات قرارداد زیر را برطرف کرده و نسخه اصلاح شده را با HTML زیبا و رسمی ارائه دهید:\n\n{content}"
    else:
        prompt = f"با توجه به متن زیر، این کار را انجام دهید: '{custom_prompt}'\n\nمتن:\n{content}"

    html_content = ask_llm(prompt)
    return jsonify({"html": html_content})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5566, debug=True)

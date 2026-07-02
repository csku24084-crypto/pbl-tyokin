# 1. 最初にライブラリをインポートする
from flask import Flask, render_template, request, jsonify
import webbrowser

# 2. ここで「app」を定義する（これがRouteより下にいくとエラーになります）
app = Flask(__name__)

TOTAL_BUDGET = 100000
transactions = []

# 3. 「app」が定義された後で、各ルートを作る
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transaction', methods=['POST'])
def add_transaction():
    # （中略）
    global transactions
    
    # フロントエンドからの入力データを受け取る
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "データが空です"}), 400
        
    amount_str = data.get('amount')
    category = data.get('category')
    
    # --- 「その他」が選ばれている場合の処理 ---
    if category == "その他":
        other_cat = data.get('other_category')
        if other_cat:
            category = other_cat.strip()
        else:
            category = ""  # 詳細が空なら空文字にして必須チェックで弾く
    elif category:
        category = category.strip()
    
    # 必須入力チェック（金額が空、またはカテゴリが空・その他詳細が空の場合にヒット）
    if not amount_str or not category:
        return jsonify({"success": False, "error": "金額とカテゴリは必須入力です"}), 400
        
    # --- 全角数字・不正文字の厳密なチェック ---
    # .isdigit() は半角数字のみ True になります（全角数字やマイナス、小数は False）
    if not str(amount_str).isdigit():
        return jsonify({"success": False, "error": "金額には半角数字を入力してください"}), 400
        
    try:
        amount = int(amount_str)
        if amount <= 0:
            return jsonify({"success": False, "error": "金額には1以上の正の整数を入力してください"}), 400
    except ValueError:
        return jsonify({"success": False, "error": "金額には半角数字を入力してください"}), 400

    # データの保存
    new_transaction = {
        "category": category,
        "amount": amount
    }
    transactions.append(new_transaction)
    
    # 画面のリアルタイム再描画のためのデータ再計算
    total_expense = sum(t['amount'] for t in transactions)
    remaining_budget = TOTAL_BUDGET - total_expense
    
    # カテゴリごとの支出内訳の計算
    category_aggregates = {}
    for t in transactions:
        cat = t['category']
        category_aggregates[cat] = category_aggregates.get(cat, 0) + t['amount']

    # 残り予算が0未満 = 赤字アラート / それ以外 = 予算内
    is_alert = remaining_budget < 0

    return jsonify({
        "success": True,
        "total_expense": total_expense,
        "remaining_budget": remaining_budget,
        "category_aggregates": category_aggregates,
        "is_alert": is_alert
    })

if __name__ == '__main__':
    # サーバー起動前にブラウザを開く指示を出しておく
    webbrowser.open('http://127.0.0.1:5000')
    
    # Flaskサーバーを起動
    app.run(debug=True)

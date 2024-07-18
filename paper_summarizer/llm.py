import google.generativeai as genai
import json

def get_summarize_by_format_from_text(text, GEMINI_API_KEY):

    genai.configure(api_key=GEMINI_API_KEY)
    model_name = "gemini-1.5-flash-latest"
    model_json = genai.GenerativeModel(
        model_name,
        generation_config={"response_mime_type": "application/json"}
        )

    prompt1 = ["""
            次の学術論文の全文 text から、以下のJSONスキーマに沿って情報を抽出して下さい。

            **論文情報**

            *   title: 論文タイトル
            *   authors: 著者名 (配列形式)
            *   publish_date: 出版日 (yyyy-mm-dd 形式)
            *   DOI: DOI (10. から始まる形式)

            **研究内容**

            *   どんなものか？: 研究の概要を簡潔に説明してください。(日本語、1文)
            *   どこがすごい？: 従来の研究と比較した際の、この論文の進歩点を説明してください。(日本語、約3文)
            *   肝となる手法は？: 研究の鍵となる技術や実験方法を説明してください。(日本語、約3文)
            *   どう主張が示された？: 論文の中心的な主張がどのように検証されたかを説明してください。(日本語、約3文)
            *   残された課題は？: 研究によって生じた残された課題や議論点を説明してください。(日本語、約3文)
            *   論文のキーワード: 論文のキーワードを3-5個挙げてください。(英語, 配列形式)
            
            **出力形式**

            上記の情報を含むJSON形式の辞書を返してください。
    """
    ,text]
    prompt2 = ["""
            次の学術論文の全文 text から、以下のJSONスキーマに沿って情報を抽出して下さい。
            **各章要約**

            *   各章要約: 各章の内容を各章あたり約5文で要約してください。リスト形式で、各要素は "章名: 要約" とします。図表があればfig.1-3やtable.1のような形で参照してください。(日本語)

            **主張とキーワードの抽出**
            1. 論文の主題を一言にまとめてください(15文字以内)
            2. 論文の重要な主張を3-5つ、10文字以内のキーワードの形で、簡潔に書き出してください
            3. 書き出した主張に関係するキーワード(ただし主張に直接は含まれないキーワード)を各主張に対してテキストから3-5つ書き出してください(英語)
            4. 主張に関連する図番号、表番号、参考文献番号を各主張に対して3-5つ書き出してください。図はFig1,3-5, 表はTbl2,4,6, 参考文献はRef3,7-9のように表記してください。
            *   例：      
            "主張とキーワードの抽出": [
            {"主題":"材料情報学に基づく逆設計フレームワーク"},
            {"主張": "Ge/ZnS多層メタマテリアルを効率的に設計", "キーワード": ["material informatics", "inverse design", "multilayer metamaterials", "visible camouflage", "infrared camouflage", "Ge/ZnS"], "図表参考文献": ["Fig.1,3,4", "Ref.23,24"]},
            {"主張": "メタマテリアルの構造を自動的に最適化", "キーワード": ["Bayesian optimization", "transfer matrix method", "machine learning", "optimization"], "図表参考文献": ["Fig. 1,2", "Ref.26-28"]},
            {"主張": "優れた色合わせと赤外カモフラージュ性能", "キーワード": ["color matching", "infrared camouflage", "observation angle", "temperature"], "図表参考文献": ["Fig. 1-5","Ref.36,38"]},
            {"主張": "様々な多目的最適化問題に適用可能", "キーワード": ["multi-objective optimization", "multispectral camouflage", "applications"], "図表参考文献": []}
            ]
               
            **出力形式**
            上記の情報をJSON形式で返してください。
    """
    ,text]

    response1 = model_json.generate_content(prompt1).text
    response2 = model_json.generate_content(prompt2).text
    
    response1 = response1.replace("\\", "\\\\")
    response2 = response2.replace("\\", "\\\\")

    response1 = json.loads(response1, strict=False)
    response2 = json.loads(response2, strict=False)

    response1['authors'] = [{'name': author.replace(',', '.')} for author in response1['authors']]
    response1['論文のキーワード'] = [{'name': author} for author in response1['論文のキーワード']]


    response = dict(**response1, **response2)
    response['mindmap'] = convert_to_mermaid(response)

    print(response)

    return response

# mermaidのmindmapを生成する
def convert_to_mermaid(data):
    mermaid_str = "mindmap\n"

    def add_node(node, parent=None):
        nonlocal mermaid_str
        indent = "    "

        if "主題" in node:
            mermaid_str += f'id["{node["主題"]}"]\n'
        else:
            mermaid_str += f'{indent}id["{node["主張"]}"]\n'
            for keyword in node.get('キーワード', []):
                mermaid_str += f'{indent}{indent}id("{keyword}")\n'
            for ref in node.get('図表参考文献', []):
                mermaid_str += f'{indent}{indent}id{{{{"{ref}"}}}}\n'

    for i, node in enumerate(data["主張とキーワードの抽出"]):
        add_node(node, i)

    return mermaid_str
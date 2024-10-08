from notion_client import Client
import json
import re
import os
import argparse

def add_notion(dict, database_id,NOTION_API_KEY):
    print(dict)
# Notion APIキーを設定
    notion = Client(auth=NOTION_API_KEY)

    # 既存のページを取得
    existing_pages = notion.databases.query(
        database_id=database_id,
        filter={"property": "DOI", "rich_text": {"equals": dict['DOI']}}
    )

    new_page_data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": dict['title']
                        }
                    }
                ]
            },
            "authors": {
                "multi_select": dict['authors']
            },
            "出版日": {
                "date":{
                    "start": dict["publish_date"]
                }
            },
            "DOI": {
                "rich_text": [
                    {
                        "text": {
                            "content": dict['DOI']
                        }
                    }
                ]
            },
            "どんなものか？": {
                "rich_text": [
                    {
                        "text": {
                            "content": dict['どんなものか？']
                        }
                    }
                ]
            },
            "どこがすごい？": {
                "rich_text": [
                    {
                        "text": {
                            "content": dict["どこがすごい？"]
                        }
                    }
                ]
            },
            "肝となる手法は？": {
                "rich_text": [
                    {
                        "text": {
                            "content": dict['肝となる手法は？']
                        }
                    }
                ]
            },
            "どう主張が示された？": {
                "rich_text": [
                    {
                        "text": {
                            "content": dict['どう主張が示された？']
                        }
                    }
                ]
            },
            "残された課題は？": {
                "rich_text": [
                    {
                        "text": {
                            "content": dict['残された課題は？']
                        }
                    }
                ]
            },
            "論文のキーワード": {
                "multi_select": dict['論文のキーワード']
            }
        },
        "children": [
            {
                "object": "block",
                "type": "code",
                "code": {
                    "caption": [],
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": dict['mindmap'][:2000]
                        }
                    }],
                    "language": "mermaid"
                }
            }
        ]
        +
        [ 
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": text[:2000]
                            }
                        } 
                    ]
                }
            } for text in dict['各章要約']
        ]
    }
    
    # DOI が存在しない場合のみ新しいページを作成
    if len(existing_pages['results']) == 0:
        # 新しいページを追加するデータ
        # Notionのデータベースに新しいページを追加
        response = notion.pages.create(**new_page_data)
    else:
        # 既存のページを更新
        page_id = existing_pages['results'][0]['id']
        response = notion.pages.update(
            page_id=page_id,
            properties=new_page_data['properties'],
            children=new_page_data['children']
        )
    # レスポンスを表示
    #print(response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and summarize arXiv paper")
    parser.add_argument("pdf_path", type=str, help="The pdf path want to make summarize")
    args = parser.parse_args()
    add_notion(args.pdf_path)

#!/usr/bin/env python3
"""
御坂美琴一号 - 小说下载爬虫
专门用于从 5963 小说网下载《完美世界》
"""

import requests
import re
import os
import sys
import argparse
import time
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def create_session():
    """创建带重试机制的会话"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_novel_info(session, book_url):
    """获取小说基本信息"""
    try:
        response = session.get(book_url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取书名
        title_tag = soup.find('h1') or soup.find('title')
        title = title_tag.get_text().strip() if title_tag else '未知书名'
        # 清理书名（去掉" - 铅笔小说"等后缀）
        if ' - ' in title:
            title = title.split(' - ')[0]
        
        # 提取作者
        author_text = soup.find(string=re.compile(r'作者'))
        if author_text:
            author = author_text.get_text().split(':')[-1].strip()
        else:
            author = '未知作者'
        
        # 从章节目录页面获取所有章节
        # 5963.net 的章节目录在 /read/{book_id}/
        book_id_match = re.search(r'/book/(\d+)/', book_url)
        if book_id_match:
            book_id = book_id_match.group(1)
            chapter_list_url = f"http://www.5963.net/read/{book_id}/"
            
            print(f"  从章节目录页面获取：{chapter_list_url}")
            list_response = session.get(chapter_list_url, timeout=10)
            list_response.encoding = 'utf-8'
            list_soup = BeautifulSoup(list_response.text, 'html.parser')
            
            chapter_list = []
            # 查找所有章节目录链接 - 筛选包含 book_id 且是.html 的链接
            for a in list_soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text().strip()
                # 筛选条件：包含 book_id 且是章节页面（.html）
                if f'{book_id}' in href and href.endswith('.html') and text:
                    chapter_list.append({'name': text, 'url': href})
            
            print(f"  共找到 {len(chapter_list)} 章")
        else:
            chapter_list = []
            print(f"  ⚠️  无法解析书籍 ID")
        
        return {
            'title': title,
            'author': author,
            'chapter_list': chapter_list,
            'total_chapters': len(chapter_list)
        }
    except Exception as e:
        print(f"❌ 获取小说信息失败：{e}")
        import traceback
        traceback.print_exc()
        return None

def download_chapter(session, chapter_url, book_path, chapter_name, timeout=60):
    """下载单个章节"""
    try:
        # 处理相对路径
        if not chapter_url.startswith('http'):
            # 5963.net 的 URL 结构：/book/2317/652840.html
            base_url = "http://www.5963.net"
            chapter_url = base_url + chapter_url
        
        response = session.get(chapter_url, timeout=timeout)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取章节内容 - 5963.net 的章节内容通常在 #content 或 .content 中
        content = soup.find('div', id='content') or soup.find('div', class_='content')
        
        if not content:
            # 尝试其他可能的内容区域
            for selector in ['div.txt', '#reader', '.reader', 'main', 'article']:
                content = soup.select_one(selector)
                if content:
                    break
        
        if not content:
            print(f"⚠️  无法找到内容区域")
            return False
        
        # 提取正文（去除导航链接等）
        # 移除不需要的元素
        for el in content.find_all(['script', 'style', 'nav', 'footer']):
            el.decompose()
        
        text = content.get_text(strip=True)
        
        if len(text) < 100:
            print(f"⚠️  章节内容太短：{len(text)} 字符")
            return False
        
        # 保存到文件
        # 清理文件名
        clean_name = re.sub(r'[<>:"/\\|?*]', '_', chapter_name[:50])
        chapter_file = os.path.join(book_path, f"{clean_name}.txt")
        
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(f"【{chapter_name}】\n\n{text}\n\n")
        
        return True
    except Exception as e:
        print(f"❌ 下载章节失败 {chapter_name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='下载网络小说')
    parser.add_argument('-u', '--url', required=True, help='小说页面 URL')
    parser.add_argument('-o', '--output', default='~/downloads', help='输出目录')
    parser.add_argument('-d', '--delay', type=float, default=1.0, help='请求间隔（秒）')
    
    args = parser.parse_args()
    
    book_url = args.url
    output_dir = os.path.expanduser(args.output)
    
    print("=" * 70)
    print("📚 御坂美琴一号 - 小说下载器")
    print("=" * 70)
    print(f"🔗 URL: {book_url}")
    print(f"💾 输出：{output_dir}")
    print(f"⏱️  间隔：{args.delay}s")
    print("=" * 70)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 提取书名
    book_title = book_url.split('/')[-2] if '/' in book_url else 'novel'
    book_path = os.path.join(output_dir, book_title)
    os.makedirs(book_path, exist_ok=True)
    
    # 创建会话
    session = create_session()
    
    # 获取小说信息
    print("\n📖 正在获取小说信息...")
    novel_info = get_novel_info(session, book_url)
    
    if not novel_info:
        print("❌ 获取小说信息失败，程序退出")
        return
    
    print(f"✅ 书名：{novel_info['title']}")
    print(f"✍️  作者：{novel_info['author']}")
    print(f"📑 章节数：{novel_info['total_chapters']}")
    
    # 下载章节
    print(f"\n🚀 开始下载章节...")
    success_count = 0
    fail_count = 0
    
    for i, chapter in enumerate(novel_info['chapter_list'], 1):
        chapter_name = chapter['name']
        chapter_url = chapter['url']
        
        # 清理文件名
        clean_name = re.sub(r'[<>:"/\\|?*]', '_', chapter_name)
        
        print(f"[{i}/{novel_info['total_chapters']}] 下载：{clean_name[:30]}...", end=" ", flush=True)
        
        if download_chapter(session, chapter_url, book_path, chapter_name):
            success_count += 1
            print("✅")
        else:
            fail_count += 1
            print("❌")
        
        # 请求间隔
        if args.delay > 0:
            time.sleep(args.delay)
    
    print("\n" + "=" * 70)
    print("✅ 下载完成！")
    print(f"📊 成功：{success_count} | 失败：{fail_count}")
    print(f"📁 保存位置：{book_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()

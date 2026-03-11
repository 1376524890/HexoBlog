#!/usr/bin/env python3
"""
铅笔小说爬虫脚本
功能：下载小说为 TXT 格式
目标网站：http://www.5963.net

注意：该网站没有公开搜索功能，需要知道小说详情页的 URL 才能下载。
建议通过网站目录浏览找到目标小说的 URL。
"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
import tldextract
from urllib.parse import urljoin
import re
import argparse


class NovelCrawler:
    """铅笔小说爬虫类"""
    
    BASE_URL = "http://www.5963.net"
    
    def __init__(self, delay=2, user_agent=None):
        """
        初始化爬虫
        
        Args:
            delay: 请求间隔时间 (秒)
            user_agent: User-Agent 字符串
        """
        self.session = requests.Session()
        self.delay = delay
        self.user_agent = user_agent or self._get_default_ua()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })
        
    def _get_default_ua(self):
        """获取默认 User-Agent"""
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    def _is_same_domain(self, url):
        """检查 URL 是否与目标网站同域"""
        extracted = tldextract.extract(url)
        return extracted.domain == "5963" and extracted.suffix == "net"
    
    def _clean_text(self, text):
        """清理文本内容"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = BeautifulSoup(text, 'html.parser').get_text()
        text = re.sub(r'[^\w\s\u4e00-\u9fa5]', '', text)
        return text.strip()
    
    def get_novel_info(self, novel_url):
        """
        获取小说基本信息
        
        Args:
            novel_url: 小说详情页 URL
            
        Returns:
            dict: 小说信息 (标题，作者，简介等)
        """
        print(f"正在获取小说信息：{novel_url}")
        
        try:
            response = self.session.get(novel_url, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取小说标题 (h1 标签)
            h1_tag = soup.find('h1')
            title = h1_tag.get_text(strip=True) if h1_tag else "未知标题"
            
            # 提取作者 (查找包含"作者"的文本，然后获取相邻的链接)
            author = "未知作者"
            for text in soup.find_all(string=True):
                if '作者：' in text or '作者:' in text:
                    parent = text.parent
                    author_link = parent.find_next('a')
                    if author_link:
                        author = author_link.get_text(strip=True)
                    break
            
            # 提取简介
            intro = ""
            all_text = soup.get_text('\n', strip=True)
            if '最新章节' in all_text:
                lines = all_text.split('\n')
                for i, line in enumerate(lines):
                    if '最新章节' in line or '本站只' in line:
                        intro_lines = lines[:i]
                        intro_lines = [l for l in intro_lines if l and 
                                      l not in ['铅笔小说', 'www.5963.net', '搜 索', '首页']]
                        intro = '\n'.join(intro_lines[:10])
                        break
            
            time.sleep(self.delay)
            
            return {
                'title': title,
                'author': author,
                'intro': intro,
                'url': novel_url
            }
            
        except requests.RequestException as e:
            print(f"获取小说信息失败：{e}")
            return None
    
    def get_chapter_list(self, novel_url):
        """
        获取小说所有章节列表
        
        Args:
            novel_url: 小说详情页 URL
            
        Returns:
            list: 章节列表，每个元素是 (chapter_title, chapter_url) 元组
        """
        print(f"正在获取章节列表：{novel_url}")
        
        # 从小说 URL 中提取 ID
        book_id = novel_url.split('/book/')[1].split('/')[0] if '/book/' in novel_url else None
        if not book_id:
            print("无法从 URL 中提取小说 ID")
            return []
        
        chapter_list_url = f"{self.BASE_URL}/read/{book_id}/"
        print(f"章节列表 URL: {chapter_list_url}")
        
        try:
            response = self.session.get(chapter_list_url, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有章节链接 - 使用 rel="chapter"属性
            chapter_list = []
            chapter_links = soup.find_all('a', rel='chapter')
            
            for link in chapter_links:
                chapter_title = link.get_text(strip=True)
                chapter_url = urljoin(self.BASE_URL, link.get('href', ''))
                
                if self._is_same_domain(chapter_url):
                    chapter_list.append((chapter_title, chapter_url))
            
            time.sleep(self.delay)
            
            print(f"共找到 {len(chapter_list)} 个章节")
            return chapter_list
            
        except requests.RequestException as e:
            print(f"获取章节列表失败：{e}")
            return []
    
    def get_chapter_content(self, chapter_url):
        """
        获取单章节内容
        
        Args:
            chapter_url: 章节 URL
            
        Returns:
            str: 章节文本内容
        """
        print(f"正在抓取章节：{chapter_url}")
        
        try:
            response = self.session.get(chapter_url, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取章节内容
            content_lines = []
            skip_keywords = ['章节错误', '返回目录', '上一章', '下一章', 
                           '加入书签', '推荐本书', '我的书架', '投推荐票']
            
            for text in soup.find_all(string=True):
                text_str = text.strip()
                if any(keyword in text_str for keyword in skip_keywords):
                    continue
                if len(text_str) < 10:
                    continue
                content_lines.append(text_str)
            
            content = '\n\n'.join(content_lines)
            
            time.sleep(self.delay)
            
            return content.strip()
            
        except requests.RequestException as e:
            print(f"获取章节内容失败：{e}")
            return ""
    
    def save_to_txt(self, title, content, output_dir):
        """保存内容到 TXT 文件"""
        safe_title = re.sub(r'[^\w\u4e00-\u9fa5]', '_', title)
        filename = f"{safe_title}.txt"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已保存到：{filepath}")
            return filepath
        except IOError as e:
            print(f"保存文件失败：{e}")
            return None
    
    def download_novel(self, novel_url, output_dir="~/downloads"):
        """下载整本小说"""
        novel_info = self.get_novel_info(novel_url)
        if not novel_info:
            print("无法获取小说信息，下载取消")
            return None
        
        title = novel_info['title']
        author = novel_info['author']
        
        print(f"\n开始下载：{title}")
        print(f"作者：{author}")
        print("-" * 50)
        
        output_dir = os.path.expanduser(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        chapter_list = self.get_chapter_list(novel_url)
        if not chapter_list:
            print("未找到章节")
            return None
        
        full_content = []
        full_content.append(f"书名：{title}")
        full_content.append(f"作者：{author}")
        full_content.append(f"来源：{self.BASE_URL}")
        full_content.append(f"抓取时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
        full_content.append("=" * 50)
        full_content.append("")
        
        for i, (chapter_title, chapter_url) in enumerate(chapter_list, 1):
            print(f" [{i}/{len(chapter_list)}] 正在下载：{chapter_title}")
            content = self.get_chapter_content(chapter_url)
            if content:
                full_content.append(f"第{i}章 {chapter_title}")
                full_content.append("=" * 30)
                full_content.append(content)
                full_content.append("")
        
        final_content = "\n".join(full_content)
        filepath = self.save_to_txt(title, final_content, output_dir)
        
        if filepath:
            print("\n" + "=" * 50)
            print(f"下载完成！文件已保存到：{filepath}")
            print("=" * 50)
        
        return filepath


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="铅笔小说爬虫 - 下载小说为 TXT 格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 直接使用小说 URL 下载
  python novel_crawler.py -u "http://www.5963.net/book/19720/"
  
  # 指定输出目录
  python novel_crawler.py -u "http://www.5963.net/book/19720/" -o "/home/user/novels"
  
  # 设置请求间隔
  python novel_crawler.py -u "http://www.5963.net/book/19720/" -d 3

注意：铅笔小说网没有公开搜索功能，需要先通过网站目录浏览找到目标小说的 URL。
        """
    )
    
    parser.add_argument(
        "-u", "--url",
        type=str,
        required=True,
        help="小说详情页 URL(必需)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="~/downloads",
        help="输出目录 (默认：~/downloads)"
    )
    
    parser.add_argument(
        "-d", "--delay",
        type=float,
        default=2.0,
        help="请求间隔时间 (秒，默认：2.0)"
    )
    
    args = parser.parse_args()
    
    crawler = NovelCrawler(delay=args.delay)
    print(f"准备下载小说：{args.url}")
    crawler.download_novel(args.url, args.output)


if __name__ == "__main__":
    main()

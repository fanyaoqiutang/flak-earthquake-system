"""
地震科普文章自动爬虫
从中国地震局官网抓取科普文章并导入数据库
"""
import requests
from bs4 import BeautifulSoup
from app import app
from models import db, ScienceCategory, EarthQuakePopular
import time
import re

# 配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

# 中国地震局官网科普栏目
TARGET_URLS = [
    "https://www.cea.gov.cn/cea/dzpd/dzcs/ff022d03-1.html",  # 地震常识
    "https://www.cea.gov.cn/cea/dzpd/dzcs/ff022d03-2.html"
]


def clean_html(html_content):
    """清理HTML标签，提取纯文本"""
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')

    # 移除script和style标签
    for script in soup(["script", "style", "header", "footer", "nav"]):
        script.decompose()

    # 获取文本
    text = soup.get_text(separator='\n', strip=True)

    # 清理多余空行
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n\n'.join(lines)

    return text


def fetch_article_detail(article_url):
    """抓取单篇文章详情"""
    try:
        print(f"    正在访问: {article_url}")
        response = requests.get(article_url, headers=HEADERS, timeout=10)
        response.encoding = response.apparent_encoding

        if response.status_code != 200:
            print(f"    ❌ 请求失败: {response.status_code}")
            return None, None

        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取标题
        title_tag = soup.find('h1') or soup.find('title')
        title = title_tag.get_text().strip() if title_tag else ""

        # 提取正文（尝试多个选择器）
        content_selectors = [
            {'tag': 'div', 'class': 'TRS_Editor'},
            {'tag': 'div', 'class': 'article-content'},
            {'tag': 'div', 'class': 'content'},
            {'tag': 'div', 'id': 'content'},
            {'tag': 'div', 'class': 'main'},
            {'tag': 'article'},
        ]

        content_html = None
        for selector in content_selectors:
            content_html = soup.find(**selector)
            if content_html:
                break

        if content_html:
            content = clean_html(str(content_html))
        else:
            # 尝试获取body主要内容
            body = soup.find('body')
            content = clean_html(str(body)) if body else ""

        return title, content

    except Exception as e:
        print(f"    ❌ 抓取失败: {str(e)}")
        return None, None


def crawl_category_page(category_url):
    """抓取分类页面，获取文章链接"""
    try:
        print(f"\n正在访问分类页面: {category_url}")
        response = requests.get(category_url, headers=HEADERS, timeout=10)
        response.encoding = response.apparent_encoding

        if response.status_code != 200:
            print(f" 请求失败: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找文章链接
        links = soup.find_all('a', href=True)

        articles = []
        for link in links:
            href = link['href']
            title = link.get_text().strip()

            # 过滤有效的文章链接
            if not title or len(title) < 5:
                continue

            # 构建完整URL
            if href.startswith('http'):
                full_url = href
            elif href.startswith('/'):
                full_url = f"http://www.cea.gov.cn{href}"
            else:
                full_url = f"http://www.cea.gov.cn/{href}"

            articles.append({
                'title': title,
                'url': full_url
            })

        return articles

    except Exception as e:
        print(f"❌ 抓取分类页面失败: {str(e)}")
        return []


def categorize_article(title):
    """根据标题自动分类"""
    if any(kw in title for kw in ['什么是', '基础', '原理', '概念']):
        return '基础知识', ''
    elif any(kw in title for kw in ['预警', '预报', '监测']):
        return '预警技术', '⚠️'
    elif any(kw in title for kw in ['避险', '逃生', '自救', '急救']):
        return '避险技能', '🏃'
    elif any(kw in title for kw in ['防震', '准备', '物资', '应急']):
        return '防震指南', '🏠'
    elif any(kw in title for kw in ['救援', '救助', '通讯']):
        return '救援知识', ''
    else:
        return '地震科普', '📚'


def save_articles(articles_data):
    """保存文章到数据库"""
    with app.app_context():
        db.create_all()

        success_count = 0
        skip_count = 0

        for article_data in articles_data:
            try:
                # 检查是否已存在
                if EarthQuakePopular.query.filter_by(title=article_data['title']).first():
                    print(f"  ⚠️  已存在，跳过: {article_data['title'][:30]}...")
                    skip_count += 1
                    continue

                # 自动分类
                category_name, icon = categorize_article(article_data['title'])

                # 查找或创建分类
                category = ScienceCategory.query.filter_by(category_name=category_name).first()
                if not category:
                    category = ScienceCategory(
                        category_name=category_name,
                        category_icon=icon
                    )
                    db.session.add(category)
                    db.session.flush()
                    print(f"  ✅ 创建分类: {category_name}")

                # 生成摘要
                content = article_data['content']
                summary = content[:150] + "..." if len(content) > 150 else content

                # 创建文章
                article = EarthQuakePopular(
                    category_id=category.category_id,
                    title=article_data['title'],
                    content=content,
                    summary=summary,
                    icon=icon,
                    is_active=True
                )
                db.session.add(article)
                success_count += 1
                print(f"  ✅ 成功导入: {article.title[:40]}...")

            except Exception as e:
                print(f"  ❌ 导入失败: {str(e)}")
                import traceback
                traceback.print_exc()

        db.session.commit()

        print("\n" + "=" * 60)
        print(f"📊 导入统计:")
        print(f"   ✅ 成功: {success_count} 篇")
        print(f"   ⚠️  跳过: {skip_count} 篇")
        print("=" * 60)


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🚀 地震科普文章自动爬虫")
    print("=" * 60)
    print("\n目标网站: 中国地震局官网 (http://www.cea.gov.cn)")
    print("说明: 本脚本将自动抓取科普文章并导入数据库\n")

    all_articles = []

    for url in TARGET_URLS:
        print(f"\n{'=' * 40}")
        print(f"正在抓取: {url}")
        print('=' * 40)

        # 获取文章列表
        articles = crawl_category_page(url)

        if not articles:
            print(f"⚠️  该页面未找到文章，继续下一个...")
            continue

        print(f"\n 找到 {len(articles)} 篇文章链接\n")

        # 抓取每篇文章详情
        for i, article in enumerate(articles, 1):
            print(f"[{i}/{len(articles)}] {article['title'][:50]}")

            title, content = fetch_article_detail(article['url'])

            if title and content and len(content) > 200:
                all_articles.append({
                    'title': title,
                    'content': content,
                    'url': article['url']
                })
                print(f"  ✅ 成功 (内容: {len(content)} 字)")
            else:
                print(f"  ⚠️  跳过 (内容不足)")

            # 礼貌延迟
            time.sleep(2)

        print()

    # 保存到数据库
    if all_articles:
        print("\n" + "=" * 60)
        print("开始保存到数据库...")
        print("=" * 60 + "\n")
        save_articles(all_articles)
    else:
        print("\n❌ 未抓取到任何有效文章")
        print("\n建议：")
        print("1. 检查网络连接")
        print("2. 官网可能限制了爬虫访问")
        print("3. 改用手动导入方案 (python import_manual_data.py)")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n 程序出错: {str(e)}")
        import traceback

        traceback.print_exc()

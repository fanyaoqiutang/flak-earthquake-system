import sqlite3
import os
from datetime import datetime


def migrate_database():
    """迁移数据库，添加科普分类表和更新文章表"""

    # 数据库路径
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'test.db')

    if not os.path.exists(db_path):
        print(f" 数据库文件不存在: {db_path}")
        print("请先运行 python app.py 初始化数据库")
        return False

    print("📊 开始数据库迁移...")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. 检查并创建 science_category 表
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='science_category'
        """)

        if not cursor.fetchone():
            print("✅ 创建 science_category 表...")
            cursor.execute('''
                CREATE TABLE science_category (
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_name VARCHAR(50) NOT NULL UNIQUE,
                    category_icon VARCHAR(100),
                    sort_order INTEGER DEFAULT 0,
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            print("️  science_category 表已存在，检查字段...")

            # 检查 science_category 表的字段
            cursor.execute("PRAGMA table_info(science_category)")
            category_columns = [col[1] for col in cursor.fetchall()]

            # 添加缺失的字段
            if 'sort_order' not in category_columns:
                print("  ✅ 添加字段: sort_order")
                cursor.execute('''
                    ALTER TABLE science_category 
                    ADD COLUMN sort_order INTEGER DEFAULT 0
                ''')
            else:
                print("  ️  字段 sort_order 已存在")

            if 'category_icon' not in category_columns:
                print("  ✅ 添加字段: category_icon")
                cursor.execute('''
                    ALTER TABLE science_category 
                    ADD COLUMN category_icon VARCHAR(100)
                ''')
            else:
                print("  ️  字段 category_icon 已存在")

        # 2. 检查 earthquake_popular 表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='earthquake_popular'
        """)

        if not cursor.fetchone():
            print("✅ 创建 earthquake_popular 表...")
            cursor.execute('''
                CREATE TABLE earthquake_popular (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER,
                    title VARCHAR(500) NOT NULL,
                    summary TEXT,
                    content TEXT,
                    icon VARCHAR(100),
                    source VARCHAR(200) DEFAULT '国家地震科学数据中心',
                    view_count INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    update_time DATETIME,
                    FOREIGN KEY (category_id) REFERENCES science_category(category_id)
                )
            ''')
        else:
            print("⚠️  earthquake_popular 表已存在，检查字段...")

            # 获取现有表的列信息
            cursor.execute("PRAGMA table_info(earthquake_popular)")
            columns = [col[1] for col in cursor.fetchall()]

            # 添加缺失的字段
            fields_to_add = [
                ('category_id', 'INTEGER'),
                ('summary', 'TEXT'),
                ('icon', 'VARCHAR(100)'),
                ('view_count', 'INTEGER DEFAULT 0'),
                ('is_active', 'INTEGER DEFAULT 1'),
                ('update_time', 'DATETIME')
            ]

            for field_name, field_type in fields_to_add:
                if field_name not in columns:
                    print(f"  ✅ 添加字段: {field_name}")
                    cursor.execute(f'''
                        ALTER TABLE earthquake_popular 
                        ADD COLUMN {field_name} {field_type}
                    ''')
                else:
                    print(f"  ️  字段 {field_name} 已存在")

        # 3. 插入初始分类数据
        cursor.execute("SELECT COUNT(*) FROM science_category")
        if cursor.fetchone()[0] == 0:
            print("\n📚 插入初始分类数据...")

            categories = [
                ('基础知识', '', 1),
                ('预警技术', '️', 2),
                ('防震指南', '', 3),
                ('应急救援', '', 4),
                ('地震案例', '📰', 5),
                ('科学解读', '', 6),
                ('法律法规', '⚖️', 7),
                ('防灾减灾', '🛡️', 8)
            ]

            cursor.executemany('''
                INSERT INTO science_category (category_name, category_icon, sort_order)
                VALUES (?, ?, ?)
            ''', categories)

            print(f"✅ 成功插入 {len(categories)} 个分类")
        else:
            print("\n⚠️  分类数据已存在，跳过")

        # 提交更改
        conn.commit()
        print("\n 数据库迁移完成！")

    except Exception as e:
        print(f"\n❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if conn:
            conn.close()

    return True


if __name__ == '__main__':
    success = migrate_database()
    if success:
        print("\n✅ 现在可以重启 Flask 后端服务了")
    else:
        print("\n❌ 请检查错误信息并修复后重试")

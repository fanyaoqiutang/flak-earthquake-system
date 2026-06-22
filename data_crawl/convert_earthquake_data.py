"""
地震数据转换脚本：将旧数据从 province_id 转换为 city_id
"""
from app import app
from models import db, Province, City, EarthquakeInfo
import sqlite3


def convert_earthquake_data():
    """将现有地震数据从 province_id 转换为 city_id"""
    with app.app_context():
        print("开始转换地震数据...")

        # 检查是否有需要转换的数据
        # 由于 SQLAlchemy 模型已改为 city_id，我们需要直接操作数据库
        conn = sqlite3.connect('instance/test.db')
        cursor = conn.cursor()

        # 检查 earthquake_info 表是否有 province_id 字段
        cursor.execute("PRAGMA table_info(earthquake_info)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'province_id' not in columns:
            print("✅ earthquake_info 表已经是 city_id 结构，无需转换")
            conn.close()
            return

        if 'city_id' not in columns:
            print("️  需要添加 city_id 字段...")
            cursor.execute("ALTER TABLE earthquake_info ADD COLUMN city_id INTEGER")
            conn.commit()

        # 获取所有地震记录
        cursor.execute("""
            SELECT earthquake_id, province_id, earthquake_message 
            FROM earthquake_info 
            WHERE city_id IS NULL
        """)
        records = cursor.fetchall()

        if not records:
            print("✅ 所有地震数据已完成转换")
            conn.close()
            return

        print(f"找到 {len(records)} 条需要转换的地震数据")

        # 省份到主要城市的映射（用于转换）
        province_to_city = {
            "北京市": "北京市",
            "天津市": "天津市",
            "河北省": "石家庄市",
            "山西省": "太原市",
            "内蒙古自治区": "呼和浩特市",
            "辽宁省": "沈阳市",
            "吉林省": "长春市",
            "黑龙江省": "哈尔滨市",
            "上海市": "上海市",
            "江苏省": "南京市",
            "浙江省": "杭州市",
            "安徽省": "合肥市",
            "福建省": "福州市",
            "江西省": "南昌市",
            "山东省": "济南市",
            "河南省": "郑州市",
            "湖北省": "武汉市",
            "湖南省": "长沙市",
            "广东省": "广州市",
            "广西壮族自治区": "南宁市",
            "海南省": "海口市",
            "重庆市": "重庆市",
            "四川省": "成都市",
            "贵州省": "贵阳市",
            "云南省": "昆明市",
            "西藏自治区": "拉萨市",
            "陕西省": "西安市",
            "甘肃省": "兰州市",
            "青海省": "西宁市",
            "宁夏回族自治区": "银川市",
            "新疆维吾尔自治区": "乌鲁木齐市",
            "台湾省": "台北市",
            "香港特别行政区": "香港",
            "澳门特别行政区": "澳门",
        }

        converted_count = 0
        failed_count = 0

        for earthquake_id, province_id, earthquake_message in records:
            try:
                # 获取省份名称
                cursor.execute("SELECT province_name FROM province WHERE province_id = ?", (province_id,))
                province_result = cursor.fetchone()
                if not province_result:
                    print(f"️  地震 {earthquake_id}: 找不到省份 {province_id}")
                    failed_count += 1
                    continue

                province_name = province_result[0]

                # 获取默认城市
                default_city_name = province_to_city.get(province_name)
                if not default_city_name:
                    print(f"️  地震 {earthquake_id}: 省份 {province_name} 没有默认城市映射")
                    failed_count += 1
                    continue

                # 尝试从 earthquake_message 中提取更精确的城市
                target_city_name = default_city_name
                if earthquake_message:
                    # 查找所有属于该省份的城市
                    cursor.execute("""
                        SELECT city_id, city_name FROM city 
                        WHERE province_id = ?
                    """, (province_id,))
                    cities = cursor.fetchall()

                    for city_id, city_name in cities:
                        # 去掉"市"后缀进行匹配
                        city_name_short = city_name.replace("市", "")
                        if city_name_short in earthquake_message or city_name in earthquake_message:
                            target_city_name = city_name
                            break

                # 查找城市 ID
                cursor.execute("SELECT city_id FROM city WHERE city_name = ?", (target_city_name,))
                city_result = cursor.fetchone()
                if not city_result:
                    print(f"⚠️  地震 {earthquake_id}: 找不到城市 {target_city_name}")
                    failed_count += 1
                    continue

                city_id = city_result[0]

                # 更新地震记录
                cursor.execute("""
                    UPDATE earthquake_info 
                    SET city_id = ? 
                    WHERE earthquake_id = ?
                """, (city_id, earthquake_id))

                converted_count += 1
                if converted_count % 10 == 0:
                    print(f"已转换 {converted_count} 条...")

            except Exception as e:
                print(f"❌ 转换地震 {earthquake_id} 失败: {str(e)}")
                failed_count += 1

        conn.commit()
        conn.close()

        print("\n" + "=" * 60)
        print("转换完成!")
        print(f"  成功: {converted_count} 条")
        print(f"  失败: {failed_count} 条")
        print("=" * 60)


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print(" 地震数据转换：province_id -> city_id")
    print("=" * 60 + "\n")

    try:
        convert_earthquake_data()
        print("\n✅ 转换完成！")
    except Exception as e:
        print(f"\n 转换失败: {str(e)}")
        import traceback

        traceback.print_exc()

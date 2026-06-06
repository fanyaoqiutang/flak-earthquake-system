<template>
  <div class="science-container">
    <div class="page-title">
      <h1> 地震科普知识</h1>
      <p class="subtitle">选择感兴趣的分类，探索地震知识</p>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 分类卡片网格 -->
    <div v-else class="category-grid">
      <div
        v-for="category in categories"
        :key="category.category_id"
        class="category-card"
        @click="viewCategory(category)"
      >
        <div class="card-icon">{{ category.category_icon || '📄' }}</div>
        <h3>{{ category.category_name }}</h3>
        <p class="article-count">{{ category.article_count || 0 }} 篇文章</p>
        <div class="arrow-icon">→</div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty v-if="!loading && categories.length === 0" description="暂无科普分类" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/API/request.js'

const router = useRouter()
const categories = ref([])
const loading = ref(true)

// 获取分类列表（包含文章数量）
const fetchCategories = async () => {
  try {
    loading.value = true

    // 调用API获取分类
    const res = await request.get('/science/categories')

    if (res.code === 200) {
      // 获取每个分类的文章数量
      const categoriesWithCount = await Promise.all(
        res.data.map(async (category) => {
          const articlesRes = await request.get('/science/articles', {
            params: { category_id: category.category_id }
          })
          return {
            ...category,
            article_count: articlesRes.data.length
          }
        })
      )

      categories.value = categoriesWithCount
    } else {
      ElMessage.error('获取分类失败')
    }
  } catch (error) {
    console.error('获取分类失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 查看分类
const viewCategory = (category) => {
  router.push(`/science/category/${category.category_id}`)
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.science-container {
  padding: 40px;
  background: #F5F7FB;
  min-height: 100vh;
}

.page-title {
  text-align: center;
  margin-bottom: 48px;
}

.page-title h1 {
  margin: 0 0 12px 0;
  font-size: 32px;
  color: #1E293B;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #64748B;
  font-size: 16px;
}

.loading {
  text-align: center;
  padding: 80px 0;
  color: #909399;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.category-card {
  background: white;
  border-radius: 16px;
  padding: 32px 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.category-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #409eff, #66b1ff);
  opacity: 0;
  transition: opacity 0.3s;
}

.category-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 28px rgba(64, 158, 255, 0.2);
  border-color: #409eff;
}

.category-card:hover::before {
  opacity: 1;
}

.card-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.category-card h3 {
  margin: 0 0 12px 0;
  color: #1E293B;
  font-size: 20px;
  font-weight: 600;
}

.article-count {
  margin: 0 0 8px 0;
  color: #909399;
  font-size: 14px;
}

.arrow-icon {
  position: absolute;
  right: 24px;
  bottom: 24px;
  font-size: 24px;
  color: #409eff;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s;
}

.category-card:hover .arrow-icon {
  opacity: 1;
  transform: translateX(0);
}
</style>

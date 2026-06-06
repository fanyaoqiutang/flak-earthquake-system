<template>
  <div class="category-container">
    <!-- 返回按钮 -->
    <div class="back-btn" @click="goBack">
      <el-icon><ArrowLeft /></el-icon>
      返回科普分类
    </div>

    <!-- 分类标题 -->
    <div v-if="categoryName" class="category-header">
      <div class="icon">{{ categoryIcon }}</div>
      <h1>{{ categoryName }}</h1>
      <p class="count">共 {{ articles.length }} 篇文章</p>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 文章列表 -->
    <div v-else class="article-list">
      <div
        v-for="article in articles"
        :key="article.article_id"
        class="article-item"
        @click="viewArticle(article)"
      >
        <div class="article-info">
          <div class="article-icon">{{ article.icon || '📄' }}</div>
          <div class="article-content">
            <h3>{{ article.title }}</h3>
            <p>{{ article.summary }}</p>
          </div>
        </div>
        <div class="article-meta">
          <span class="views">
            <el-icon><View /></el-icon>
            {{ article.view_count }}
          </span>
          <span class="arrow">→</span>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty v-if="!loading && articles.length === 0" description="该分类下暂无文章" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Loading, View } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/API/request.js'

const route = useRoute()
const router = useRouter()

const categoryName = ref('')
const categoryIcon = ref('📄')
const articles = ref([])
const loading = ref(true)

// 获取文章列表
const fetchArticles = async () => {
  try {
    loading.value = true
    const categoryId = route.params.categoryId

    const res = await request.get('/science/articles', {
      params: { category_id: categoryId }
    })

    if (res.code === 200) {
      articles.value = res.data
      // 从第一篇文章获取分类信息
      if (res.data.length > 0) {
        categoryName.value = res.data[0].category_name
        categoryIcon.value = '📚'
      }
    } else {
      ElMessage.error('获取文章列表失败')
    }
  } catch (error) {
    console.error('获取文章列表失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 查看文章详情
const viewArticle = (article) => {
  router.push(`/science/article/${article.article_id}`)
}

// 返回
const goBack = () => {
  router.push('/science')
}

onMounted(() => {
  fetchArticles()
})
</script>

<style scoped>
.category-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px;
  background: #F5F7FB;
  min-height: 100vh;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 24px;
  color: #409eff;
  font-weight: 500;
  transition: all 0.3s;
}

.back-btn:hover {
  background: #ecf5ff;
  transform: translateX(-4px);
}

.category-header {
  text-align: center;
  margin-bottom: 40px;
}

.category-header .icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.category-header h1 {
  margin: 0 0 12px 0;
  font-size: 28px;
  color: #1E293B;
  font-weight: 600;
}

.count {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.loading {
  text-align: center;
  padding: 80px 0;
  color: #909399;
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.article-item {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid transparent;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.article-item:hover {
  transform: translateX(8px);
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
  border-color: #409eff;
}

.article-info {
  display: flex;
  gap: 16px;
  flex: 1;
}

.article-icon {
  font-size: 36px;
  flex-shrink: 0;
}

.article-content {
  flex: 1;
}

.article-content h3 {
  margin: 0 0 8px 0;
  color: #1E293B;
  font-size: 18px;
  font-weight: 600;
}

.article-content p {
  margin: 0;
  color: #64748B;
  font-size: 14px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  color: #909399;
  font-size: 14px;
}

.views {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.arrow {
  font-size: 20px;
  color: #409eff;
}
</style>

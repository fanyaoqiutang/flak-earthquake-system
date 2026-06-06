<template>
  <div class="detail-container">
    <!-- 返回按钮 -->
    <div class="back-btn" @click="goBack">
      <el-icon><ArrowLeft /></el-icon>
      返回文章列表
    </div>

    <div v-if="loading" class="loading">
      <el-icon size="40"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else-if="article" class="article-content">
      <div class="article-header">
        <el-icon class="icon"><View /></el-icon>
        <h1>{{ article.title }}</h1>
        <div class="article-meta">
          <div class="meta-item">
            <el-icon><Clock /></el-icon>
            {{ article.create_time }}
          </div>
          <div class="meta-item">来源：{{ article.source }}</div>
        </div>
      </div>
      <div class="article-body">
        <div class="content" v-html="formatContent(article.content)"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Loading, View, Clock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/API/request.js'

const route = useRoute()
const router = useRouter()

const article = ref(null)
const loading = ref(true)

// 获取文章详情
const fetchArticle = async () => {
  try {
    loading.value = true
    const articleId = route.params.articleId

    const res = await request.get(`/science/articles/${articleId}`)

    if (res.code === 200) {
      article.value = res.data
    } else {
      ElMessage.error('获取文章失败')
    }
  } catch (error) {
    console.error('获取文章详情失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 格式化内容（将换行符转换为HTML）
const formatContent = (content) => {
  if (!content) return ''
  return content.replace(/\n/g, '<br>')
}

onMounted(() => {
  fetchArticle()
})
</script>

<style scoped>
.detail-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px 40px;
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

.loading {
  text-align: center;
  padding: 60px 0;
  color: #909399;
}

.article-content {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.article-header {
  text-align: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #E4E7ED;
}

.article-header .icon {
  font-size: 60px;
  margin-bottom: 16px;
}

.article-header h1 {
  margin: 0 0 16px 0;
  font-size: 28px;
  color: #1E293B;
  font-weight: 600;
  line-height: 1.4;
}

.article-meta {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
  color: #909399;
  font-size: 14px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.article-summary {
  background: #f0f7ff;
  border-left: 4px solid #409eff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 32px;
}

.article-summary h3 {
  margin: 0 0 12px 0;
  color: #1E293B;
  font-size: 18px;
}

.article-summary p {
  margin: 0;
  color: #606266;
  line-height: 1.8;
  font-size: 15px;
}

.article-body h3 {
  margin: 0 0 20px 0;
  color: #1E293B;
  font-size: 18px;
}

.content {
  color: #303133;
  line-height: 2;
  font-size: 15px;
  white-space: pre-wrap;
}
</style>

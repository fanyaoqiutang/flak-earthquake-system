<template>
  <div class="science-container">
    <!-- 搜索栏 -->
    <div class="search-section">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索科普文章..."
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #append>
          <el-button @click="handleSearch">搜索</el-button>
        </template>
      </el-input>
    </div>

    <!-- 文章列表 -->
    <div v-if="filterArticles.length > 0" class="article-list">
      <div
        v-for="article in filterArticles"
        :key="article.article_id"
        class="article-card"
        @click="$router.push(`/science/article/${article.article_id}`)"
      >
        <div class="article-title">{{ article.title }}</div>
        <div class="article-meta">
          <span class="author">{{ article.author }}</span>
          <span class="year">{{ article.year }}</span>
          <span class="views">
            <el-icon><View /></el-icon>
            {{ article.view_count }}
          </span>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty v-else description="暂无科普文章" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, View } from '@element-plus/icons-vue'

// 静态模拟科普数据
const articleList = ref([
  {
    article_id: 1,
    title: "地震发生时室内避险正确方法",
    author: "地震预警平台",
    year: "2026",
    view_count: 1256,
    content: `<h2>一、室内紧急避震要点</h2>
<p>1. 立刻蹲、躲、护：迅速蹲在坚固桌子下方，一手抓牢桌腿，另一手护住头部颈部，远离玻璃窗、吊灯、衣柜等重物。</p>
<p>2. 切勿乱跑：地震摇晃时不要冲向门口、阳台，墙体、玻璃极易坠落伤人。</p>
<p>3. 远离危险区域：避开厨房（燃气管道）、阳台、落地窗、高大家具。</p>
<h2>二、震后撤离注意事项</h2>
<p>摇晃停止后有序撤离，走楼梯禁止乘坐电梯；撤离前关闭燃气、电源。</p>`
  },
  {
    article_id: 2,
    title: "家庭地震应急包准备清单",
    author: "地震预警平台",
    year: "2026",
    view_count: 987,
    content: `<h2>家庭应急包必备物资</h2>
<ol>
<li>饮用水、压缩饼干（可供3天食用）</li>
<li>手电筒、备用电池、手摇收音机</li>
<li>急救包：纱布、碘伏、止血棉、常用药品</li>
<li>口哨（被困用于呼救）</li>
<li>保暖薄毯、一次性口罩手套</li>
</ol>
<p>应急包放置客厅随手可拿到的位置，每半年更换一次食品与饮用水。</p>`
  },
  {
    article_id: 3,
    title: "户外遇到地震如何自救",
    author: "地震预警平台",
    year: "2025",
    view_count: 763,
    content: `<p>1. 马路边：远离高楼、广告牌、电线杆，跑到空旷平地蹲下。</p>
<p>2. 山区：警惕滑坡、落石，向垂直山坡方向撤离。</p>
<p>3. 河边海边：立刻向高处转移，防范地震引发海啸。</p>`
  },
  {
    article_id: 4,
    title: "不同震级地震危害科普",
    author: "地震预警平台",
    year: "2025",
    view_count: 621,
    content: `<ul>
<li>3级以下：微弱震动，无破坏</li>
<li>3~4.9级：室内轻微晃动，物品小幅移动</li>
<li>5~5.9级：墙体开裂，老旧房屋受损</li>
<li>6级以上：建筑坍塌，易造成人员伤亡</li>
</ul>`
  }
])

const searchKeyword = ref('')
// 搜索过滤文章
const filterArticles = computed(() => {
  if (!searchKeyword.value.trim()) return articleList.value
  return articleList.value.filter(item => item.title.includes(searchKeyword.value))
})

const handleSearch = () => {}
</script>

<style scoped>
.science-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px;
  background: #F5F7FB;
  min-height: 100vh;
}
.search-section {
  margin-bottom: 24px;
}
.article-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.article-card {
  background: white;
  border-radius: 8px;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid transparent;
}
.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(64, 158, 0.15);
  border-color: #409eff;
}
.article-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 8px;
  line-height: 1.5;
}
.article-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #909399;
  font-size: 13px;
}
.author {
  color: #64748B;
}
.year {
  color: #909399;
}
.views {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
}
@media (max-width: 768px) {
  .science-container {
    padding: 16px;
  }
  .article-card {
    padding: 14px 16px;
  }
  .article-title {
    font-size: 15px;
  }
  .article-meta {
    font-size: 12px;
    gap: 10px;
  }
}
</style>
<template>
  <div class="detail-container">
    <!-- 返回按钮 -->
    <div class="back-btn" @click="$router.back()">
      <el-icon><ArrowLeft /></el-icon>
      返回文章列表
    </div>

    <div v-if="currentArticle" class="article-content">
      <div class="article-header">
        <h1>{{ currentArticle.title }}</h1>
        <div class="article-meta">
          <div class="meta-item">
            <el-icon><Clock /></el-icon>
            {{ currentArticle.year }}年
          </div>
          <div class="meta-item">作者：{{ currentArticle.author }}</div>
          <div class="meta-item">
            <el-icon><View /></el-icon>
            阅读 {{ currentArticle.view_count }}
          </div>
        </div>
      </div>
      <div class="article-body">
        <div class="content" v-html="currentArticle.content"></div>
      </div>
    </div>

    <el-empty v-else description="文章不存在" />
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { ArrowLeft, View, Clock } from '@element-plus/icons-vue'
import { ref } from 'vue'

const route = useRoute()

// 和列表页完全一致的静态数据
const allArticles = [
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
]

const currentArticle = ref(null)
// 根据路由id匹配文章
const aid = Number(route.params.articleId)
currentArticle.value = allArticles.find(item => item.article_id === aid)
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
  flex-wrap: wrap;
}
.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.content {
  color: #303133;
  line-height: 2;
  font-size: 15px;
}
/* 富文本内容样式穿透 */
.content :deep(p) {
  margin-bottom: 1em;
}
.content :deep(h2) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: bold;
  color: #1E293B;
}
.content :deep(ul), .content :deep(ol) {
  padding-left: 2em;
  margin-bottom: 1em;
}
@media (max-width: 768px) {
  .detail-container {
    padding: 16px;
  }
  .article-content {
    padding: 24px;
  }
  .article-header h1 {
    font-size: 22px;
  }
}
</style>
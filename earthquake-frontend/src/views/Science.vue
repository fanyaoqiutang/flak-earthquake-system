<template>
  <div class="science-container">
    <!-- 删掉了紫色横幅，只保留标题 -->
    <div class="page-title">
      <h1>📚 地震科普知识</h1>
    </div>

    <div class="knowledge-grid">
      <div
        v-for="article in articles"
        :key="article.id"
        class="knowledge-card"
        @click="viewDetail(article)"
      >
        <div class="card-icon">{{ article.icon }}</div>
        <h3>{{ article.title }}</h3>
        <p>{{ article.summary }}</p>
        <el-tag :type="article.type" size="small">{{ article.category }}</el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const articles = ref([
  {
    id: 1,
    icon: '🌍',
    title: '什么是地震?',
    summary: '地震是地球内部能量释放引起的地表震动现象，主要由地壳板块运动造成，按成因可分为构造地震、火山地震等类型。',
    category: '基础知识',
    type: 'primary'
  },
  {
    id: 2,
    icon: '⚠️',
    title: '地震预警原理',
    summary: '利用地震波传播速度差异，在破坏性横波到达前发出警报，为避险争取数秒至数十秒的宝贵时间。',
    category: '预警技术',
    type: 'danger'
  },
  {
    id: 3,
    icon: '🏠',
    title: '家庭防震准备',
    summary: '准备应急包、制定家庭应急预案、固定易倾倒物品、学习避险技能，提高家庭抗震能力。',
    category: '防震指南',
    type: 'success'
  },
  {
    id: 4,
    icon: '🎒',
    title: '应急物资清单',
    summary: '饮用水、食品、急救用品、手电筒、哨子等必备物资，建议储备至少3天的用量。',
    category: '应急准备',
    type: 'warning'
  },
  {
    id: 5,
    icon: '🏃',
    title: '室内地震避险方法',
    summary: '地震发生时，应立即躲在坚固家具下，远离窗户、吊灯和外墙，保护头部。',
    category: '避险技能',
    type: 'info'
  },
  {
    id: 6,
    icon: '🚪',
    title: '室外地震避险方法',
    summary: '在室外应远离建筑物、电线杆、桥梁等危险物，前往开阔地带蹲下，保护头部。',
    category: '避险技能',
    type: 'info'
  },
  {
    id: 7,
    icon: '🏥',
    title: '地震后自救互救',
    summary: '被困时保持冷静，检查伤情、发出求救信号；发现他人被困，应科学施救，等待专业救援。',
    category: '救援知识',
    type: ''
  },
  {
    id: 8,
    icon: '📊',
    title: '地震等级划分',
    summary: '震级按释放能量划分，通常3级以下为微震，5级以上为破坏性地震，震级每升1级能量增32倍。',
    category: '基础知识',
    type: 'primary'
  },
  {
    id: 9,
    icon: '🌋',
    title: '火山地震与构造地震',
    summary: '构造地震占地震总数90%以上，由板块运动引发；火山地震由火山活动引起，多分布在火山带附近。',
    category: '基础知识',
    type: 'primary'
  },
  {
    id: 10,
    icon: '🚇',
    title: '公共场所地震避险',
    summary: '在商场、地铁等公共场所，应听从工作人员指挥，避开拥挤人流，就近寻找安全位置躲避。',
    category: '避险技能',
    type: 'info'
  },
  {
    id: 11,
    icon: '📞',
    title: '震后通讯与求助',
    summary: '震后优先使用短信、微信等文字通讯，减少语音通话占用信道；可通过社交媒体或应急频道求助。',
    category: '救援知识',
    type: ''
  },
  {
    id: 12,
    icon: '🌐',
    title: '地震次生灾害防范',
    summary: '地震可能引发火灾、滑坡、海啸等次生灾害，震后应检查燃气、水电安全，远离危险区域。',
    category: '防震指南',
    type: 'success'
  }
])

const viewDetail = (article) => {
  ElMessage.info(`${article.title} - 详细内容开发中`)
}
</script>

<style scoped>
.science-container {
  padding: 24px 40px;
  background: #F5F7FB;
  min-height: 100vh;
}

/* 简化后的标题样式 */
.page-title {
  margin-bottom: 32px;
}

.page-title h1 {
  margin: 0;
  font-size: 24px;
  color: #1E293B;
  font-weight: 600;
}

.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.knowledge-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.knowledge-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.card-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.knowledge-card h3 {
  margin: 0 0 8px 0;
  color: #1E293B;
  font-size: 18px;
  font-weight: 500;
}

.knowledge-card p {
  color: #64748B;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 12px;
}
</style>
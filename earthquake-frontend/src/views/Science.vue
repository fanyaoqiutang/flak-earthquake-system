<template>
  <div class="earthquake-knowledge">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>地震科普知识</h1>
      <p class="subtitle">了解地震，科学防护</p>
    </div>

    <!-- 导航目录 -->
    <div class="table-of-contents">
      <h2>目录</h2>
      <ul>
        <li><a href="#definition" @click.prevent="scrollToSection('definition')">地震定义</a></li>
        <li><a href="#characteristics" @click.prevent="scrollToSection('characteristics')">地震特征</a></li>
        <li><a href="#causes" @click.prevent="scrollToSection('causes')">成因与类型</a></li>
        <li><a href="#distribution" @click.prevent="scrollToSection('distribution')">地震分布</a></li>
        <li><a href="#disasters" @click.prevent="scrollToSection('disasters')">地震灾害</a></li>
        <li><a href="#prevention" @click.prevent="scrollToSection('prevention')">预防应急</a></li>
        <li><a href="#statistics" @click.prevent="scrollToSection('statistics')">统计数据</a></li>
      </ul>
    </div>

    <!-- 地震定义 -->
    <section id="definition" class="content-section">
      <h2>一、地震定义</h2>
      <div class="section-content">
        <p>地震（英文：earthquake），又称地动、地振动，是地壳快速释放能量过程中造成的振动，期间会产生地震波的一种自然现象。</p>
        <p>地球上板块与板块之间相互挤压碰撞，造成板块边沿及板块内部产生错动和破裂，是引起地震的主要原因。</p>

        <div class="info-box">
          <h3>基本概念</h3>
          <ul>
            <li><strong>震源：</strong>地震开始发生的地点</li>
            <li><strong>震中：</strong>震源正上方的地面</li>
            <li><strong>极震区：</strong>破坏性地震的地面振动最烈处，往往也就是震中所在的地区</li>
          </ul>
        </div>

        <div class="highlight-box">
          <p>据统计，地球上每年约发生500多万次地震，即每天要发生上万次的地震。其中绝大多数太小或太远，以至于人们感觉不到；真正能对人类造成严重危害的地震大约有十几二十次；能造成特别严重灾害的地震大约有一两次。</p>
        </div>
      </div>
    </section>

    <!-- 地震特征 -->
    <section id="characteristics" class="content-section">
      <h2>二、地震特征</h2>

      <h3>2.1 地球结构</h3>
      <div class="section-content">
        <p>地球分为三层：中心层是地核，中间是地幔，外层是地壳。地球的平均半径为6370公里左右，地壳厚度为35公里左右，大多数破坏性地震就发生在地壳内。</p>
      </div>

      <h3>2.2 地震波传播方式</h3>
      <div class="section-content">
        <div class="wave-types">
          <div class="wave-card">
            <h4>纵波（P波）</h4>
            <ul>
              <li>振动方向与传播方向一致</li>
              <li>传播速度较快</li>
              <li>到达地面时人感觉颠动，物体上下跳动</li>
            </ul>
          </div>
          <div class="wave-card">
            <h4>横波（S波）</h4>
            <ul>
              <li>振动方向与传播方向垂直</li>
              <li>传播速度比纵波慢</li>
              <li>到达地面时人感觉摇晃，物体会来回摆动</li>
              <li><strong>是造成破坏的主要原因</strong></li>
            </ul>
          </div>
          <div class="wave-card">
            <h4>面波</h4>
            <ul>
              <li>当体波到达岩层界面或地表时产生</li>
              <li>沿界面或地表传播的幅度很大的波</li>
              <li>传播速度小于横波，跟在横波的后面</li>
            </ul>
          </div>
        </div>
        <p class="tip">发生较大的近震时，一般人们先感到上下颠簸，过数秒到十几秒后才感到有很强的水平晃动。</p>
      </div>

      <h3>2.3 地震震级</h3>
      <div class="section-content">
        <p>震级是地震大小的一种度量，根据地震释放能量的多少来划分，用"级"来表示。震级的标度最初是美国地震学家里克特（C.F.Richter）于1935年研究加里福尼亚地方性地震时提出的。</p>

        <div class="magnitude-table">
          <h4>震级分类</h4>
          <table>
            <thead>
              <tr>
                <th>类型</th>
                <th>震级范围</th>
                <th>特征</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>弱震</td>
                <td>&lt; 3级</td>
                <td>如果震源不是很浅，这种地震人们一般不易觉察</td>
              </tr>
              <tr>
                <td>有感地震</td>
                <td>3级 ~ 4.5级</td>
                <td>人们能够感觉到，但一般不会造成破坏</td>
              </tr>
              <tr>
                <td>中强震</td>
                <td>4.5级 ~ 6级</td>
                <td>属于可造成破坏的地震，但破坏轻重还与震源深度、震中距等多种因素有关</td>
              </tr>
              <tr>
                <td>强震</td>
                <td>≥ 6级</td>
                <td>其中震级大于等于8级的又称为巨大地震</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="info-box">
          <p><strong>能量关系：</strong>地震相差一级，能量相差约30倍。震级相差0.1级，释放的能量平均相差1.4倍。</p>
        </div>
      </div>

      <h3>2.4 地震烈度</h3>
      <div class="section-content">
        <p>同样大小的地震，造成的破坏不一定相同；同一次地震，在不同的地方造成的破坏也不同。为衡量地震破坏程度，科学家又"制作"了另一把"尺子"——地震烈度。</p>
        <p>影响烈度的因素有震级、震源深度、距震源的远近、地面状况和地层构造等。</p>

        <div class="highlight-box">
          <p><strong>重要概念：</strong>一次地震只有一个震级，但它所造成的破坏在不同的地区是不同的。即一次地震，可以划分出好几个烈度不同的地区。</p>
        </div>

        <p>中国1980年重新编订了地震烈度表，按12个烈度等级划分烈度。</p>
      </div>
    </section>

    <!-- 地震成因与类型 -->
    <section id="causes" class="content-section">
      <h2>三、地震成因与类型</h2>

      <h3>3.1 地震成因</h3>
      <div class="section-content">
        <p>由于地壳运动引起地壳岩层断裂错动而发生的地壳震动，称为地震。目前科学家比较公认的解释是构造地震是由地壳板块运动造成的。</p>
        <p>由于地球在无休止地自转和公转，其内部物质也在不停地进行分异，所以，围绕在地球表面的地壳，或者说岩石圈也在不断地生成、演变和运动，这便促成了全球性地壳构造运动。</p>
      </div>

      <h3>3.2 地震类型</h3>
      <div class="section-content">
        <h4>按发生位置分类</h4>
        <ul>
          <li><strong>板缘地震（板块边界地震）：</strong>发生在板块边界上的地震，环太平洋地震带上绝大多数地震属于此类</li>
          <li><strong>板内地震：</strong>发生在板块内部的地震，如欧亚大陆内部（包括中国）的地震多属此类</li>
          <li><strong>火山地震：</strong>由火山爆发时所引起的能量冲击而产生的地壳振动</li>
        </ul>

        <h4>按形成原因分类</h4>
        <ul>
          <li><strong>构造地震：</strong>由于岩层断裂，发生变位错动，在地质构造上发生巨大变化而产生的地震，也叫断裂地震</li>
          <li><strong>火山地震：</strong>由火山爆发时所引起的能量冲击而产生的地壳振动，只占地震次数的7%左右</li>
          <li><strong>陷落地震：</strong>由于地层陷落引起的地震，只占地震总次数的3%左右，震级很小</li>
          <li><strong>诱发地震：</strong>在特定的地区因某种地壳外界因素诱发（如陨石坠落、水库蓄水、深井注水）而引起的地震</li>
          <li><strong>人工地震：</strong>地下核爆炸、炸药爆破等人为引起的地面振动</li>
        </ul>

        <h4>按震源深度分类</h4>
        <div class="depth-types">
          <div class="depth-card">
            <h5>浅源地震</h5>
            <p>深度 &lt; 70公里</p>
            <p>大多数破坏性地震是浅源地震</p>
          </div>
          <div class="depth-card">
            <h5>中源地震</h5>
            <p>深度 70~300公里</p>
          </div>
          <div class="depth-card">
            <h5>深源地震</h5>
            <p>深度 &gt; 300公里</p>
            <p>世界纪录最深地震震源深度为786公里</p>
          </div>
        </div>
        <p class="tip">一年中，全球所有地震释放的能量约有85%来自浅源地震，12%来自中源地震，3%来自深源地震。</p>

        <h4>构造地震的分类</h4>
        <ul>
          <li><strong>孤立型地震：</strong>有突出的主震，余震次数少、强度低；主震所释放的能量占全序列的99.9%以上</li>
          <li><strong>主震—余震型地震：</strong>主震非常突出，余震十分丰富；最大地震所释放的能量占全序列的90%以上</li>
          <li><strong>双震型地震：</strong>一次地震活动序列中，90%以上的能量主要由发生时间接近，地点接近，大小接近的两次地震释放</li>
          <li><strong>震群型地震：</strong>有两个以上大小相近的主震，余震十分丰富；主要能量通过多次震级相近的地震释放</li>
        </ul>
      </div>
    </section>

    <!-- 地震分布 -->
    <section id="distribution" class="content-section">
      <h2>四、地震分布</h2>

      <h3>4.1 时间分布</h3>
      <div class="section-content">
        <p>地震活动在时间上的分布是不均匀的：一段时间发生地震较多，震级较大，称为<strong>地震活跃期</strong>；另一段时间发生地震较少，震级较小，称为<strong>地震活动平静期</strong>；表现出地震活动的周期性。</p>
        <p>中国大陆东部地震活动周期普遍比西部长。东部的活动周期大约300年左右，西部为100至200年左右。</p>
      </div>

      <h3>4.2 地理分布</h3>
      <div class="section-content">
        <h4>世界地震分布</h4>
        <p>据统计，全球有85%的地震发生在板块边界上。世界上主要有三大地震带：</p>

        <div class="earthquake-belts">
          <div class="belt-item">
            <h5>环太平洋地震带</h5>
            <p>分布在太平洋周围，是全球分布最广、地震最多的地震带，所释放的能量约占全球的四分之三。</p>
          </div>
          <div class="belt-item">
            <h5>欧亚地震带</h5>
            <p>从地中海向东，一支经中亚至喜马拉雅山，然后向南经中国横断山脉，过缅甸，呈弧形转向东，至印度尼西亚。</p>
          </div>
          <div class="belt-item">
            <h5>大洋中脊地震活动带</h5>
            <p>蜿蜒于各大洋中间，几乎彼此相连。此地震活动带的地震活动性较之前两个带要弱得多，而且均为浅源地震。</p>
          </div>
        </div>

        <h4>中国地震分布</h4>
        <p>中国的地震活动主要分布在5个地区：</p>
        <ol>
          <li>台湾省及其附近海域</li>
          <li>西南地区，包括西藏、四川中西部和云南中西部</li>
          <li>西部地区，主要在甘肃河西走廊、青海、宁夏以及新疆天山南北麓</li>
          <li>华北地区，主要在太行山两侧、汾渭河谷、阴山—燕山一带、山东中部和渤海湾</li>
          <li>东南沿海地区，广东、福建等地</li>
        </ol>

        <div class="highlight-box">
          <p><strong>中国南北地震带：</strong>从中国的宁夏，经甘肃东部、四川中西部直至云南，有一条纵贯中国大陆、大致呈南北走向的地震密集带，历史上曾多次发生强烈地震。2008年5月12日汶川8.0级地震就发生在该带中南段。</p>
        </div>
      </div>
    </section>

    <!-- 地震灾害 -->
    <section id="disasters" class="content-section">
      <h2>五、地震灾害</h2>

      <h3>5.1 直接灾害</h3>
      <div class="section-content">
        <p>地震直接灾害是地震的原生现象，如地震断层错动，以及地震波引起地面振动，所造成的灾害。主要有：</p>
        <ul>
          <li>地面的破坏</li>
          <li>建筑物与构筑物的破坏</li>
          <li>山体等自然物的破坏（如滑坡、泥石流等）</li>
          <li>海啸、地光烧伤等</li>
        </ul>

        <div class="info-box">
          <p><strong>典型案例：</strong>1976年中国河北唐山地震中，70%～80%的建筑物倒塌，人员伤亡惨重。</p>
        </div>
      </div>

      <h3>5.2 次生灾害</h3>
      <div class="section-content">
        <p>地震次生灾害是直接灾害发生后，破坏了自然或社会原有的平衡或稳定状态，从而引发出的灾害。主要有：</p>
        <ul>
          <li><strong>火灾：</strong>地震火灾多是因房屋倒塌后火源失控引起的，是次生灾害中最常见、最严重的</li>
          <li><strong>海啸：</strong>地震时海底地层发生断裂，部分地层出现猛烈上升或下沉，造成从海底到海面的整个水层发生剧烈"抖动"</li>
          <li><strong>瘟疫：</strong>强烈地震发生后，灾区水源、供水系统等遭到破坏或受到污染，极易造成疫病流行</li>
          <li><strong>滑坡和崩塌：</strong>这类地震的次生灾害主要发生在山区和塬区，往往是毁灭性的</li>
          <li><strong>水灾：</strong>地震引起水库、江湖决堤，或是由于山体崩塌堵塞河道造成水体溢出等</li>
        </ul>
      </div>

      <h3>5.3 破坏特点</h3>
      <div class="section-content">
        <ul>
          <li><strong>瞬时性：</strong>地震在瞬间发生，地震作用的时间很短，最短十几秒，最长两三分钟就造成山崩地裂，房倒屋塌</li>
          <li><strong>伤亡大：</strong>地震使大量房屋倒塌，是造成人员伤亡的元凶</li>
        </ul>

        <div class="highlight-box warning">
          <p><strong>历史教训：</strong>1976年7月28日中国唐山7.8级大地震，死亡24.2万余人，重伤16.4万余人。统计表明，约60%的死亡是抗震能力差的砖石房屋倒塌造成的。</p>
        </div>
      </div>

      <h3>5.4 地震之最</h3>
      <div class="section-content">
        <ul>
          <li><strong>古今中外地震死亡人口之最：</strong>1556年1月23日发生在中国陕西华县的8.0级地震，估计死亡83万余人</li>
          <li><strong>世界上第一次成功预报的地震：</strong>1975年2月4日，海城地震（中国的地震工作者成功地预报）</li>
          <li><strong>世界上最大的地震带：</strong>环太平洋地震带</li>
          <li><strong>世界上有仪器记录的最大地震：</strong>1960年5月22日，智利地震（8.9级，也有9.5级的说法）</li>
          <li><strong>中国最早的地震记录：</strong>帝舜时大约在公元前23世纪，距今已有四千多年历史</li>
        </ul>
      </div>
    </section>

    <!-- 预防应急 -->
    <section id="prevention" class="content-section">
      <h2>六、预防应急</h2>

      <h3>6.1 设防环节</h3>
      <div class="section-content">
        <ol>
          <li><strong>抗震设防要求的确定：</strong>通过制定地震区划图、开展地震小区划工作以及进行地震安全性评价，来确定工程所需的抗震设防要求</li>
          <li><strong>抗震设计：</strong>工程师需要按照相关的抗震设计规范，进行工程的设计工作</li>
          <li><strong>抗震施工：</strong>施工团队需要严格按照抗震设计进行施工，确保工程在建造过程中符合抗震要求</li>
        </ol>
      </div>

      <h3>6.2 抗震场地选择</h3>
      <div class="section-content">
        <p>建筑场地选择好建筑场地，千万不要在不利于抗震的场地建房，不利于抗震的场地有：</p>
        <ul>
          <li>活动断层及其附近地区</li>
          <li>饱含水的松砂层、软弱的淤泥层、松软的人工填土层</li>
          <li>古河道、旧池塘和河滩地</li>
          <li>容易产生开裂、沉陷、滑移的陡坡、河坎</li>
          <li>细长突出的山嘴、高耸的山包或三面临水田的台地等</li>
        </ul>
      </div>

      <h3>6.3 房屋加固</h3>
      <div class="section-content">
        <p>为了抗御地震的突然袭击，要经常注意老旧房屋的维修保养：</p>
        <ul>
          <li>墙体如有裂缝或歪闪，要及时修理</li>
          <li>易风化酥碱的土墙，要定期抹面</li>
          <li>屋顶漏水应迅速修补</li>
          <li>大雨过后要马上排除房屋周围积水，以免长期浸泡墙基</li>
          <li>木梁和柱等要预防腐朽虫蛀，如有损坏及时检修</li>
        </ul>
      </div>

      <h3>6.4 地震前兆</h3>
      <div class="section-content">
        <h4>地下水异常</h4>
        <ul>
          <li>水位、水量的反常变化</li>
          <li>水质的变化：变色、变味、变浑，有异味等</li>
          <li>水温的变化</li>
          <li>翻花冒泡、喷气发响、井壁变形等</li>
        </ul>

        <h4>生物异常</h4>
        <p>动物是观察地震前兆的"活仪器"，它们往往在震前出现各种反常行为：</p>
        <ul>
          <li><strong>惊恐反应：</strong>如大牲畜不进圈，狗狂吠，鸟或昆虫惊飞、非正常群迁等</li>
          <li><strong>抑制型异常：</strong>如行为变得迟缓，或发呆发痴，不知所措；或不肯进食等</li>
          <li><strong>生活习性变化：</strong>如冬眠的蛇出洞，老鼠白天活动不怕人，大批青蛙上岸活动等</li>
        </ul>

        <h4>电磁异常</h4>
        <p>收音机、电视机、日光灯等出现的失灵现象。最常见的是收音机的失灵、手机信号减弱或消失、电子闹钟失灵等现象。</p>

        <h4>地声</h4>
        <p>临近地震发生前，往往有声响自地下深处传来，这就是"地声"。地声一般出现在震前几分钟、几小时、几天或更早。</p>

        <h4>地光</h4>
        <p>地光也是临震前的一种宏观现象，一般出现在临震前或震时，也有出现于震前数小时或更早的。地光的颜色很多，有红、黄、蓝、白、紫等。</p>
      </div>

      <h3>6.5 地震应急避震</h3>
      <div class="section-content">
        <h4>可能产生的伤害</h4>
        <ul>
          <li><strong>直接伤害：</strong>在室内因器物倾倒或房屋倒塌被砸伤；在室外被倒塌的建筑物等砸伤；在野外被山上的滚石砸伤；被地光烧伤</li>
          <li><strong>间接伤害：</strong>地震引起的火灾、水灾、毒气泄漏、危险品爆炸</li>
        </ul>

        <h4>避震原则</h4>
        <div class="principle-box">
          <ol>
            <li>一要因地制宜，不要一定之规</li>
            <li>二要行动果断，不要犹豫不决</li>
            <li>三在公共场所要听从指挥，不要擅自行动</li>
          </ol>
        </div>

        <h4>避震要点</h4>
        <div class="emergency-tips">
          <div class="tip-item">
            <span class="tip-number">1</span>
            <p><strong>就近躲避，震后撤离：</strong>震时就近躲避，震后迅速撤离到安全的地方，是应急避震较好的办法</p>
          </div>
          <div class="tip-item">
            <span class="tip-number">2</span>
            <p><strong>选择安全位置：</strong>躲在室内结实、不易倾倒、能掩护身体的物体下或物体旁，空间小、有支撑的地方；室外远离建筑物，开阔、安全的地方</p>
          </div>
          <div class="tip-item">
            <span class="tip-number">3</span>
            <p><strong>保护身体：</strong>应趴下，使身体重心降到最低，脸朝下，不要压住口鼻，以利呼吸；蹲下或坐下时尽量蜷曲身体；抓住身边牢固的物体</p>
          </div>
          <div class="tip-item">
            <span class="tip-number">4</span>
            <p><strong>保护头部：</strong>低头，用手护住头部和后颈，有可能时，用身边的物品，如枕头、被褥等顶在头上以保护头颈部</p>
          </div>
          <div class="tip-item">
            <span class="tip-number">5</span>
            <p><strong>避免二次伤害：</strong>不要随便点明火，因为空气中可能有易燃易爆气体充溢；要避开人流，不要乱挤乱拥</p>
          </div>
        </div>

        <h4>灾后生活注意</h4>
        <ul>
          <li>注意饮食和个人卫生</li>
          <li>搭建和居住防震棚要注意防火</li>
          <li>积极投入恢复重建工作</li>
          <li>按规定服用预防药物，增强身体抵抗力，防疫灭病</li>
        </ul>
      </div>
    </section>

    <!-- 统计数据 -->
    <section id="statistics" class="content-section">
      <h2>七、统计数据</h2>
      <div class="section-content">
        <h3>近年中国地震统计</h3>

        <div class="stats-cards">
          <div class="stat-card">
            <h4>2023年</h4>
            <ul>
              <li>共发生5级以上地震18次</li>
              <li>大陆发生5级以上地震11次</li>
              <li>最大地震：12月18日甘肃积石山6.2级地震</li>
              <li>活动水平较2022年和历史平均水平明显偏弱</li>
            </ul>
          </div>

          <div class="stat-card">
            <h4>2024年</h4>
            <ul>
              <li>中国大陆地区发生5.0级以上地震25次</li>
              <li>主要分布在新疆地区</li>
              <li>新疆乌什7.1级地震造成3人死亡</li>
              <li>直接经济损失37.9亿元</li>
            </ul>
          </div>

          <div class="stat-card">
            <h4>2025年</h4>
            <ul>
              <li>共发生5.0级以上地震11次</li>
              <li>各级地震共造成直接经济损失97亿元</li>
            </ul>
          </div>
        </div>

        <div class="info-box">
          <p><strong>数据来源：</strong>国家统计局《中华人民共和国国民经济和社会发展统计公报》</p>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="page-footer">
      <p>本页面内容整理自百度百科，仅供科普教育使用</p>
      <p class="update-time">最后更新：2026年6月</p>
    </footer>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

const scrollToSection = (id) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

onMounted(() => {
  // 页面加载时的初始化操作
  console.log('地震科普知识页面已加载')
})
</script>

<style scoped>
.earthquake-knowledge {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  background: #F5F7FB;
  min-height: 100vh;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
}

.page-header h1 {
  margin: 0 0 12px 0;
  font-size: 42px;
  font-weight: 700;
}

.subtitle {
  margin: 0;
  font-size: 18px;
  opacity: 0.95;
}

/* 目录 */
.table-of-contents {
  background: white;
  padding: 24px 32px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 32px;
}

.table-of-contents h2 {
  margin: 0 0 16px 0;
  font-size: 20px;
  color: #1E293B;
}

.table-of-contents ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.table-of-contents li a {
  color: #409eff;
  text-decoration: none;
  padding: 8px 16px;
  display: block;
  border-radius: 6px;
  transition: all 0.3s;
}

.table-of-contents li a:hover {
  background: #ecf5ff;
  color: #66b1ff;
}

/* 内容区块 */
.content-section {
  background: white;
  padding: 32px;
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.content-section > h2 {
  margin: 0 0 24px 0;
  font-size: 28px;
  color: #1E293B;
  border-bottom: 3px solid #409eff;
  padding-bottom: 12px;
}

.content-section > h3 {
  margin: 32px 0 16px 0;
  font-size: 22px;
  color: #334155;
}

.content-section > h4 {
  margin: 24px 0 12px 0;
  font-size: 18px;
  color: #475569;
}

.content-section > h5 {
  margin: 20px 0 10px 0;
  font-size: 16px;
  color: #64748B;
  font-weight: 600;
}

.section-content {
  color: #334155;
  line-height: 1.8;
}

.section-content p {
  margin: 12px 0;
}

.section-content ul, .section-content ol {
  margin: 12px 0;
  padding-left: 24px;
}

.section-content li {
  margin: 8px 0;
}

/* 信息框 */
.info-box {
  background: #f0f9ff;
  border-left: 4px solid #409eff;
  padding: 16px 20px;
  margin: 20px 0;
  border-radius: 6px;
}

.info-box h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #1E293B;
}

/* 高亮框 */
.highlight-box {
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
  padding: 16px 20px;
  margin: 20px 0;
  border-radius: 6px;
}

.highlight-box.warning {
  background: #fee2e2;
  border-left-color: #ef4444;
}

.highlight-box p {
  margin: 0;
}

/* 地震波类型卡片 */
.wave-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.wave-card {
  background: #f8fafc;
  padding: 20px;
  border-radius: 10px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s;
}

.wave-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.wave-card h4 {
  margin: 0 0 12px 0;
  color: #1E293B;
  font-size: 18px;
}

.wave-card ul {
  margin: 0;
  padding-left: 20px;
}

/* 震级表格 */
.magnitude-table {
  margin: 20px 0;
  overflow-x: auto;
}

.magnitude-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.magnitude-table thead {
  background: #409eff;
  color: white;
}

.magnitude-table th,
.magnitude-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.magnitude-table tbody tr:hover {
  background: #f8fafc;
}

/* 深度类型卡片 */
.depth-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin: 20px 0;
}

.depth-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
}

.depth-card h5 {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: white;
}

.depth-card p {
  margin: 6px 0;
  opacity: 0.95;
}

/* 地震带 */
.earthquake-belts {
  display: grid;
  gap: 16px;
  margin: 20px 0;
}

.belt-item {
  background: #f8fafc;
  padding: 16px 20px;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.belt-item h5 {
  margin: 0 0 8px 0;
  color: #1E293B;
  font-size: 16px;
}

.belt-item p {
  margin: 0;
  color: #64748B;
}

/* 提示文本 */
.tip {
  background: #e0f2fe;
  padding: 12px 16px;
  border-radius: 6px;
  margin: 16px 0;
  color: #0369a1;
  font-size: 14px;
}

/* 原则框 */
.principle-box {
  background: #dcfce7;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
}

.principle-box ol {
  margin: 0;
  padding-left: 24px;
}

/* 应急提示 */
.emergency-tips {
  display: grid;
  gap: 16px;
  margin: 20px 0;
}

.tip-item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
}

.tip-number {
  background: #409eff;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.tip-item p {
  margin: 0;
  flex: 1;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.stat-card h4 {
  margin: 0 0 16px 0;
  font-size: 20px;
  color: white;
}

.stat-card ul {
  margin: 0;
  padding-left: 20px;
}

.stat-card li {
  margin: 8px 0;
  opacity: 0.95;
}

/* 页脚 */
.page-footer {
  text-align: center;
  padding: 32px 20px;
  margin-top: 40px;
  color: #64748B;
}

.page-footer p {
  margin: 8px 0;
}

.update-time {
  font-size: 14px;
  opacity: 0.8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .earthquake-knowledge {
    padding: 20px 16px;
  }

  .page-header h1 {
    font-size: 32px;
  }

  .content-section {
    padding: 24px 20px;
  }

  .content-section > h2 {
    font-size: 24px;
  }

  .table-of-contents ul {
    grid-template-columns: 1fr;
  }

  .wave-types,
  .depth-types,
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>
<template>
  <div class="content">
    <Row :gutter="20">
      <i-col span="18">
        <article-content/>
      </i-col>
      <i-col span="6" :gutter="20">
        <right-sider/>
      </i-col>
    </Row>
  </div>
</template>

<script>
import ArticleContent from './article-content.vue'
import RightSider from './right-sider.vue'
export default {
  name: 'guest_article',
  components: {
    ArticleContent,
    RightSider
  }
}
</script>

<style scoped>
.content {
  min-height: calc(100vh - 210px);
  margin-left: 250px;
  margin-right: 250px;
}
</style>

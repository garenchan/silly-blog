<template>
  <div class="content">
    <Row :gutter="20">
      <i-col span="18">
        <article-content/>
      </i-col>
      <i-col span="6" :gutter="20">
        <Affix :offset-top="75">
          <right-sider/>
        </Affix>
      </i-col>
    </Row>
  </div>
</template>

<script>
import ArticleContent from './article-content.vue'
import RightSider from '../home/right-sider.vue'
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

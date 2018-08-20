<template>
  <div class="content">
    <Row :gutter="20">
      <i-col span="18">
        <newest-articles/>
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
import NewestArticles from './newest-articles.vue'
import RightSider from './right-sider.vue'

export default {
  name: 'index',
  components: {
    NewestArticles,
    RightSider
  },
  data () {
    return {}
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

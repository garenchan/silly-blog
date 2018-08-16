<template>
  <div class="content">
    <Row :gutter="20">
      <i-col span="18">
        <Card>
          111
        </Card>
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
import RightSider from './right-sider.vue'
export default {
  name: 'index',
  components: {
    RightSider
  },
  data () {
    return {}
  }
}
</script>

<style>
.content {
  min-height: 1700px;
  margin-left: 200px;
  margin-right: 200px;
}
</style>

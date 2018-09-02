<template>
  <div class="content">
    <Row :gutter="20">
      <i-col span="18">
        <category-content/>
      </i-col>
      <i-col span="6" :gutter="20">
      </i-col>
    </Row>
  </div>
</template>

<script>
import CategoryContent from './category-content.vue'

export default {
  name: 'guest_category',
  components: {
    CategoryContent
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

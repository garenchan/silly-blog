<template>
  <div>
    <Card>
      <p slot="title">
        <Icon type="md-grid"/>
        分类资料
      </p>
      <b>{{ category.name }}</b>
      <p>{{ category.description }}</p>
      <Spin size="large" fix v-if="loading"></Spin>
    </Card>
  </div>
</template>

<script>
export default {
  name: 'right-sider',
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    category: {
      type: Object,
      default: Map
    }
  }
}
</script>

<style scoped>

</style>

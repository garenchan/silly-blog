<template>
  <div class="content">
    <Row :gutter="20">
      <i-col span="18">
        <category-content/>
      </i-col>
      <i-col span="6" :gutter="20">
        <right-sider :category="category" :loading="loading"/>
      </i-col>
    </Row>
  </div>
</template>

<script>
import { mapMutations } from 'vuex'
import { getCategory } from '@/api/category'
import CategoryContent from './category-content.vue'
import RightSider from './right-sider.vue'

export default {
  name: 'guest_category',
  components: {
    CategoryContent,
    RightSider
  },
  data () {
    return {
      categoryId: this.$route.params.category_id,
      loading: false,
      category: {}
    }
  },
  methods: {
    ...mapMutations([
      'setActiveKey'
    ]),
    getCurrentCategory () {
      return new Promise((resolve, reject) => {
        this.loading = true
        getCategory(this.categoryId).then(res => {
          this.loading = false
          let category = this.category = res.category
          // 更新顶部导航栏
          this.setActiveKey(category.name)
        }).catch(err => {
          this.loading = false
          console.log('load current category failed:' + err)
          let response = err.response
          if (response.status === 404) this.$router.push({ name: 'error_404' })
        })
      })
    }
  },
  mounted () {
    this.getCurrentCategory()
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

<template>
  <div>
    <Card class="category-article-card" :dis-hover="true">
      <h2 slot="title">
        <Icon type="logo-buffer"/>
        分类文章
      </h2>
      <div>
        <Table :loading="loading"
               :show-header="false"
               :disabled-hover="true"
               :columns="columns"
               :no-data-text="noDataText"
               :data="articles"/>
      </div>
    </Card>
  </div>
</template>

<script>
import { mapMutations } from 'vuex'
import { getCategory } from '@/api/category'

export default {
  name: 'category-content',
  data () {
    return {
      categoryId: this.$route.params.category_id,
      loading: false,
      columns: [],
      noDataText: '尚无文章, 亲亲速度来发表喔!',
      articles: []
    }
  },
  methods: {
    ...mapMutations([
      'setActiveKey'
    ]),
    getCurrentCategory () {
      return new Promise((resolve, reject) => {
        getCategory(this.categoryId).then(res => {
          let category = res.category
          // 更新顶部导航栏
          this.setActiveKey(category.name)
        }).catch(err => {
          console.log('load current category failed:' + err)
          let response = err.response
          if (response.status === 404) this.$router.push({ name: 'error_404' })
        })
      })
    }
  },
  mounted () {
    this.getCurrentCategory()
  },
  beforeDestroy () {
    this.setActiveKey(null)
  }
}
</script>

<style>
.category-article-card > .ivu-card-body {
  padding: 0px;
}
.category-article-card .ivu-table-wrapper {
  border-top-width: 0px;
  border-left-width: 0px;
  border-right-width: 0px;
}
.category-article-card .ivu-table-cell {
  padding-left: 0px;
  padding-right: 0px;
}
</style>

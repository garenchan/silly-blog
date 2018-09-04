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
      <div style="margin: 10px;overflow: hidden" v-if="dataTotal > 0">
        <div style="float: right;">
            <Page :total="dataTotal"
                  :page-size-opts="pageSizeOpts"
                  :page-size="pageSize"
                  :current="currentPage"
                  @on-change="changePage"
                  @on-page-size-change="changePageSize"/>
        </div>
      </div>
    </Card>
  </div>
</template>

<script>
import { mapMutations } from 'vuex'
import { listArticles } from '@/api/article'
import CategoryArticleItem from './category-article-item.vue'

export default {
  name: 'category-content',
  data () {
    return {
      categoryId: this.$route.params.category_id,
      loading: false,
      columns: [
        {
          key: 'id',
          render: (h, params) => {
            return h(CategoryArticleItem, {
              props: {
                article: params.row
              }
            })
          }
        }
      ],
      noDataText: '尚无文章, 亲亲速度来发表喔!',
      articles: [],
      // 分页显示
      dataTotal: 0,
      pageSize: 10,
      pageSizeOpts: [10, 15, 20],
      currentPage: 1,
      sortColumn: 'published_at',
      SortDirection: 'desc'
    }
  },
  methods: {
    ...mapMutations([
      'setActiveKey'
    ]),
    getCategoryArticles () {
      return new Promise((resolve, reject) => {
        let params = {
          published: true,
          sort: this.sortColumn,
          direction: this.SortDirection,
          page: this.currentPage,
          pageSize: this.pageSize,
          category_id: this.categoryId
        }
        this.loading = true
        listArticles(params).then(res => {
          this.loading = false
          this.articles = res.articles
          this.dataTotal = res.total
        }).catch(err => {
          this.loading = false
          console.log('load category articles failed:' + err)
        })
      })
    },
    changePage (index) {
      this.currentPage = index
      this.getCategoryArticles()
    },
    changePageSize (size) {
      this.pageSize = size
      this.getCategoryArticles()
    }
  },
  mounted () {
    this.getCategoryArticles()
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

<template>
  <div>
    <Card class="newest-article-card" :dis-hover="true">
      <h2 slot="title">
        <Icon type="logo-buffer"/>
        最新文章
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
import NewestArticleItem from './newest-article-item.vue'
import { listArticles } from '@/api/article'

export default {
  name: 'newest-articles',
  components: {
    NewestArticleItem
  },
  data () {
    return {
      loading: false,
      noDataText: '尚无文章, 亲亲速度来发表喔!',
      columns: [
        {
          key: 'id',
          render: (h, params) => {
            return h(NewestArticleItem, {
              props: {
                article: params.row
              }
            })
          }
        }
      ],
      articles: []
    }
  },
  methods: {
    getNewestArticles () {
      return new Promise((resolve, reject) => {
        let params = {
          published: true,
          sort: 'published_at',
          direction: 'desc',
          page: 1,
          pageSize: 10
        }
        this.loading = true
        listArticles(params).then(res => {
          this.loading = false
          this.articles = res.articles
        }).catch(err => {
          this.loading = false
          console.log('load newest articles failed:' + err)
        })
      })
    }
  },
  mounted () {
    this.getNewestArticles()
  }
}
</script>

<style>
.newest-article-card > .ivu-card-body {
  padding: 0px;
}
.newest-article-card .ivu-table-wrapper {
  border-top-width: 0px;
  border-left-width: 0px;
  border-right-width: 0px;
}
.newest-article-card .ivu-table-cell {
  padding-left: 0px;
  padding-right: 0px;
}
</style>

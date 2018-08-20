<template>
  <div>
    <Card>
      <p slot="title">
        <Icon type="md-contact"/>
        个人资料
      </p>
      <div style="text-align: center">
        <Avatar :style="{ background: avatarColor }">{{ author.name }}</Avatar>
        &nbsp;<span style="font-weight: bold">{{ author.display_name || author.name }}</span>
      </div>
      <Spin size="large" fix v-if="userLoading"></Spin>
    </Card>
    <Card style="margin-top: 20px">
      <p slot="title">
        <Icon type="md-flame"/>
        热门文章
      </p>
      <div :key="article.id" v-for="article in hotestArticles">
        <router-link :to="{ name: 'guest_article', params: { article_id: article.id }}">
          [{{ article.source.name }}] {{ article.title }}
        </router-link>
      </div>
      <Spin size="large" fix v-if="articleLoading"></Spin>
    </Card>
  </div>
</template>

<script>
import { getUser } from '@/api/user'
import { listArticles } from '@/api/article'

export default {
  name: 'right-sider',
  data () {
    return {
      userLoading: false,
      articleLoading: false,
      userId: null,
      author: {},
      hotestArticles: []
    }
  },
  computed: {
    avatarColor () {
      if (this.author.name && !this.userLoading) return 'black'
      else return 'white'
    }
  },
  methods: {
    getArticleAuthor () {
      return new Promise((resolve, reject) => {
        this.userLoading = true
        getUser(this.userId).then(res => {
          this.userLoading = false
          this.author = res.user
        }).catch(err => {
          this.userLoading = false
          console.log('load article author failed:' + err)
        })
      })
    },
    getHotestArticles () {
      return new Promise((resolve, reject) => {
        let params = {
          sort: 'views',
          direction: 'desc',
          page: 1,
          pageSize: 5
        }
        this.articleLoading = true
        listArticles(params).then(res => {
          this.articleLoading = false
          this.hotestArticles = res.articles
        }).catch(err => {
          this.articleLoading = false
          console.log('load hotest articles failed:' + err)
        })
      })
    }
  },
  mounted () {
    this.getHotestArticles()
    this.$root.$on('articleAuthor', data => {
      this.userId = data
      this.getArticleAuthor()
    })
  }
}
</script>

<style scoped>
</style>

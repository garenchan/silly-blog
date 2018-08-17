<template>
  <div>
    <Card>
      <div>
        <Avatar style="background-color: #f56a00">{{ article.source && article.source.name }}</Avatar>
        <span class="title">&nbsp;{{ article.title }}</span>
      </div>
      <Divider />
      <Article v-html="content">
      </Article>
    </Card>
  </div>
</template>

<script>
import { getArticle } from '@/api/article'
import { EventBus } from '@/libs/bus'
import showdown from 'showdown'

export default {
  name: 'article-content',
  data () {
    return {
      id: this.$route.params.article_id,
      article: {},
      content: '',
      converter: null
    }
  },
  methods: {
    getCurrentArticle () {
      return new Promise((resolve, reject) => {
        getArticle(this.id).then(res => {
          let article = this.article = res.article
          this.content = this.converter.makeHtml(article.content)
          // 更新顶部导航栏
          if (article.category.length) EventBus.$emit('menuChanged', article.category.slice(-1)[0].name)
        }).catch(err => {
          console.log('load current article failed:' + err)
        })
      })
    }
  },
  mounted () {
    this.converter = new showdown.Converter()
    this.getCurrentArticle()
  }
}
</script>

<style scoped>
.title {
  font-size: 20px;
  font-weight: bold;
}
</style>
